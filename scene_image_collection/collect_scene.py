"""Scene image collector: download -> CLIP real-photo filter -> open-vocab detect target
-> require at least one co-occurring (non-target) object -> save full image + JSON metadata.

Output policy: final saved count is NOT capped. `--n` only sizes the candidate pool.
Every image that:
  - has min side >= --min-side
  - passes CLIP real-photo threshold
  - contains the target (YOLO-World) with area_ratio < --target-max-ratio
  - contains at least one non-target object (COCO YOLOv8 + YOLO-World on LVIS-style words)
will be saved as `images/<out>/<out>_NNN.jpg` plus `images/<out>/<out>_NNN.json`.
"""
import argparse, shutil, os, json
from pathlib import Path
from PIL import Image
import torch
import open_clip
from ultralytics import YOLO
from icrawler.builtin import BingImageCrawler, BaiduImageCrawler

ROOT = Path(__file__).parent
IMAGES_DIR = ROOT / "images"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

REAL_TEMPLATES = [
    "a photograph of {}", "a real photo of {}", "a candid photo of {}",
    "a high-resolution photo of {}",
]
FAKE_TEMPLATES = [
    "a cartoon of {}", "a drawing of {}", "an illustration of {}",
    "a 3d render of {}", "a meme of {}", "clip art of {}",
    "a painting of {}", "an anime drawing of {}", "a sketch of {}",
    "a plush toy of {}", "a figurine of {}",
]

# ~100 curated common-object words for YOLO-World co-object detection.
# Source: LVIS frequent categories + common indoor/outdoor objects.
LVIS_COMMON = [
    "person", "child", "man", "woman",
    "chair", "sofa", "couch", "bed", "table", "desk", "bench", "stool",
    "cabinet", "shelf", "bookshelf", "drawer", "wardrobe",
    "lamp", "ceiling light", "candle",
    "rug", "curtain", "pillow", "blanket", "towel",
    "tv", "television", "monitor", "laptop", "computer", "keyboard", "mouse",
    "phone", "cellphone", "tablet", "camera", "remote control", "speaker",
    "book", "magazine", "newspaper", "paper",
    "cup", "mug", "glass", "bottle", "wine glass", "bowl", "plate", "fork", "knife", "spoon",
    "kettle", "teapot", "pot", "pan", "microwave", "oven", "refrigerator", "toaster",
    "food", "bread", "fruit", "vegetable", "cake", "pizza",
    "backpack", "handbag", "suitcase", "umbrella", "hat", "glasses", "watch",
    "shoe", "boot",
    "car", "truck", "bus", "motorcycle", "bicycle",
    "traffic light", "traffic sign", "fire hydrant", "stop sign",
    "tree", "plant", "flower pot", "potted plant", "grass", "rock",
    "dog", "cat", "bird", "horse", "cow", "sheep",
    "fence", "wall", "door", "window", "stairs",
    "clock", "picture frame", "mirror", "vase",
    "ball", "toy", "guitar", "piano", "violin",
    # additions for low-yield classes
    "ironing board", "hanger", "laundry basket", "dustpan",
    "antenna", "satellite dish", "tower",
    "cue stick", "billiard ball", "scarf", "earmuffs",
    "envelope", "letter", "mailbox", "package",
    "log", "leaf", "moss", "fern", "fallen log",
    "holster", "ammunition", "bullet",
    "launcher", "military truck", "soldier",
    "mushroom",
]


def download(query_list, raw_dir, per_kw=40):
    raw_dir.mkdir(exist_ok=True)
    for i, kw in enumerate(query_list):
        for engine_name, Engine in [("bing", BingImageCrawler), ("baidu", BaiduImageCrawler)]:
            d = raw_dir / f"{engine_name}_{i}"
            d.mkdir(exist_ok=True)
            try:
                Engine(storage={"root_dir": str(d)},
                       feeder_threads=2, parser_threads=2, downloader_threads=4
                       ).crawl(keyword=kw, max_num=per_kw, min_size=(600, 600),
                               file_idx_offset="auto")
            except Exception as e:
                print(f"[{engine_name}] {kw}: {e}")


def gather_images(raw_dir):
    files = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp", "*.bmp"):
        files.extend(raw_dir.rglob(ext))
    return sorted(set(files))


def filter_by_resolution(files, min_side):
    out = []
    for f in files:
        try:
            with Image.open(f) as im:
                W, H = im.size
            if W >= min_side and H >= min_side:
                out.append(f)
        except Exception:
            continue
    return out


def load_clip():
    model, _, preprocess = open_clip.create_model_and_transforms(
        "ViT-L-14", pretrained="openai", device=DEVICE)
    model.eval()
    tokenizer = open_clip.get_tokenizer("ViT-L-14")
    return model, preprocess, tokenizer


@torch.no_grad()
def encode_text(model, tokenizer, prompts):
    toks = tokenizer(prompts).to(DEVICE)
    feats = model.encode_text(toks)
    feats /= feats.norm(dim=-1, keepdim=True)
    return feats


@torch.no_grad()
def clip_real_scores(model, preprocess, files, real_t, fake_t, batch=32):
    out = []
    for i in range(0, len(files), batch):
        chunk = files[i:i+batch]
        imgs, ok = [], []
        for f in chunk:
            try:
                img = Image.open(f).convert("RGB")
                imgs.append(preprocess(img))
                ok.append(f)
            except Exception:
                continue
        if not imgs:
            continue
        x = torch.stack(imgs).to(DEVICE)
        feats = model.encode_image(x)
        feats /= feats.norm(dim=-1, keepdim=True)
        sim_real = (feats @ real_t.T).mean(dim=-1)
        sim_fake = (feats @ fake_t.T).mean(dim=-1)
        s = torch.stack([sim_real, sim_fake], dim=-1) * 100
        prob_real = s.softmax(dim=-1)[:, 0].cpu().tolist()
        for f, pr in zip(ok, prob_real):
            out.append({"file": f, "real": pr})
    return out


def iou(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0, ix2 - ix1), max(0, iy2 - iy1)
    inter = iw * ih
    area_a = max(0, ax2 - ax1) * max(0, ay2 - ay1)
    area_b = max(0, bx2 - bx1) * max(0, by2 - by1)
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def merge_boxes(boxes, iou_thresh=0.5):
    """Greedy NMS-like dedup across mixed-source boxes (keep higher conf)."""
    boxes = sorted(boxes, key=lambda b: b["conf"], reverse=True)
    kept = []
    for b in boxes:
        if any(iou(b["box"], k["box"]) > iou_thresh for k in kept):
            continue
        kept.append(b)
    return kept


def detect_target(yolo_world_target, image_path, conf_thresh=0.1):
    """Run YOLO-World with single target class; return best box or None."""
    try:
        res = yolo_world_target.predict(source=str(image_path), conf=conf_thresh,
                                         iou=0.5, verbose=False, imgsz=640)[0]
    except Exception as e:
        print(f"target detect error {image_path.name}: {e}")
        return None
    if len(res.boxes) == 0:
        return None
    best = int(res.boxes.conf.argmax())
    x1, y1, x2, y2 = [float(v) for v in res.boxes.xyxy[best].tolist()]
    return {"box": [x1, y1, x2, y2], "conf": float(res.boxes.conf[best])}


def detect_co_objects(yolo_coco, yolo_world_ext, ext_class_names, image_path,
                      target_box, co_conf_thresh=0.25):
    """Run COCO YOLOv8 + YOLO-World(LVIS_COMMON); merge, drop target-overlapping boxes."""
    candidates = []
    try:
        r = yolo_coco.predict(source=str(image_path), conf=co_conf_thresh,
                              iou=0.5, verbose=False, imgsz=640)[0]
        names = r.names
        for b in r.boxes:
            cls = int(b.cls[0])
            candidates.append({
                "label": names[cls],
                "box": [float(v) for v in b.xyxy[0].tolist()],
                "conf": float(b.conf[0]),
                "source": "coco",
            })
    except Exception as e:
        print(f"coco detect error {image_path.name}: {e}")
    try:
        r = yolo_world_ext.predict(source=str(image_path), conf=co_conf_thresh,
                                    iou=0.5, verbose=False, imgsz=640)[0]
        for b in r.boxes:
            cls = int(b.cls[0])
            candidates.append({
                "label": ext_class_names[cls],
                "box": [float(v) for v in b.xyxy[0].tolist()],
                "conf": float(b.conf[0]),
                "source": "yolo_world_lvis",
            })
    except Exception as e:
        print(f"lvis detect error {image_path.name}: {e}")
    candidates = merge_boxes(candidates, iou_thresh=0.5)
    out = []
    for c in candidates:
        if iou(c["box"], target_box) > 0.5:
            continue
        out.append(c)
    return out


def collect(query_list, target_prompt, out_dir, n=80, raw_dir=None,
            min_side=800, target_max_ratio=0.5, real_thresh=0.55,
            co_conf_thresh=0.25, candidates_factor=6,
            yolo_world="yolov8s-worldv2.pt", yolo_coco="yolov8s.pt",
            start_index=0):
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = Path(raw_dir or (ROOT / "_raw"))

    target_candidates = n * candidates_factor
    per_kw = max(20, target_candidates // (len(query_list) * 2))
    download(query_list, raw_dir, per_kw=per_kw)
    files = gather_images(raw_dir)
    print(f"raw downloaded: {len(files)}")

    files = filter_by_resolution(files, min_side)
    print(f"after resolution filter (>= {min_side}): {len(files)}")
    if not files:
        return 0, raw_dir

    print("loading CLIP ViT-L/14...")
    clip_model, preprocess, tokenizer = load_clip()
    real_t = encode_text(clip_model, tokenizer,
                         [t.format(target_prompt) for t in REAL_TEMPLATES])
    fake_t = encode_text(clip_model, tokenizer,
                         [t.format(target_prompt) for t in FAKE_TEMPLATES])
    scores = clip_real_scores(clip_model, preprocess, files, real_t, fake_t)
    kept = [s for s in scores if s["real"] >= real_thresh]
    print(f"after CLIP real-photo filter (>= {real_thresh}): {len(kept)}")
    del clip_model
    torch.cuda.empty_cache()

    print(f"loading {yolo_world} (target)...")
    det_target = YOLO(yolo_world)
    det_target.set_classes([target_prompt])

    print(f"loading {yolo_world} (LVIS co-objects)...")
    det_ext = YOLO(yolo_world)
    det_ext.set_classes(LVIS_COMMON)

    print(f"loading {yolo_coco} (COCO co-objects)...")
    det_coco = YOLO(yolo_coco)

    saved = 0
    used_keys = set()
    for s in sorted(kept, key=lambda x: x["real"], reverse=True):
        f = s["file"]
        try:
            img = Image.open(f).convert("RGB")
        except Exception:
            continue
        W, H = img.size
        key = (img.size, os.path.getsize(f))
        if key in used_keys:
            continue
        used_keys.add(key)

        tgt = detect_target(det_target, f)
        if tgt is None:
            continue
        x1, y1, x2, y2 = tgt["box"]
        area_ratio = ((x2 - x1) * (y2 - y1)) / (W * H)
        if area_ratio >= target_max_ratio:
            continue

        co = detect_co_objects(det_coco, det_ext, LVIS_COMMON, f, tgt["box"],
                                co_conf_thresh=co_conf_thresh)
        if not co:
            continue

        saved += 1
        stem = f"{out_dir.name}_{start_index + saved:03d}"
        img.save(out_dir / f"{stem}.jpg", quality=92)
        meta = {
            "source_path": str(f),
            "image_size": [W, H],
            "real_score": s["real"],
            "target": {
                "prompt": target_prompt,
                "box": tgt["box"],
                "conf": tgt["conf"],
                "area_ratio": area_ratio,
            },
            "co_objects": co,
        }
        with open(out_dir / f"{stem}.json", "w", encoding="utf-8") as fp:
            json.dump(meta, fp, ensure_ascii=False, indent=2)

    print(f"saved {saved} to {out_dir}")
    return saved, raw_dir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--queries", nargs="+", required=True,
                    help="scene-flavored search keywords (mix languages)")
    ap.add_argument("--target", required=True,
                    help="open-vocab prompt for the target object (use generic class)")
    ap.add_argument("--out", required=True, help="output subdir name under images/")
    ap.add_argument("--n", type=int, default=80,
                    help="target candidate pool size (controls download volume; "
                         "final output is NOT capped)")
    ap.add_argument("--min-side", type=int, default=800,
                    help="minimum image width AND height (default 800)")
    ap.add_argument("--target-max-ratio", type=float, default=0.5,
                    help="target box must occupy < this fraction of image area")
    ap.add_argument("--real-thresh", type=float, default=0.55)
    ap.add_argument("--co-conf-thresh", type=float, default=0.25,
                    help="confidence threshold for co-occurring objects")
    ap.add_argument("--yolo-world", default="yolov8s-worldv2.pt")
    ap.add_argument("--yolo-coco", default="yolov8s.pt")
    ap.add_argument("--keep-raw", action="store_true")
    ap.add_argument("--start-index", type=int, default=0,
                    help="offset for output filenames (e.g. continue numbering "
                         "after a previous run that left N files)")
    args = ap.parse_args()

    saved, raw_dir = collect(
        query_list=args.queries,
        target_prompt=args.target,
        out_dir=IMAGES_DIR / args.out,
        n=args.n,
        min_side=args.min_side,
        target_max_ratio=args.target_max_ratio,
        real_thresh=args.real_thresh,
        co_conf_thresh=args.co_conf_thresh,
        yolo_world=args.yolo_world,
        yolo_coco=args.yolo_coco,
        start_index=args.start_index,
    )
    if not args.keep_raw:
        shutil.rmtree(raw_dir, ignore_errors=True)
        print(f"removed {raw_dir}")
    print(f"DONE: saved {saved} scene images.")


if __name__ == "__main__":
    main()
