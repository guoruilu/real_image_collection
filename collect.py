"""Generic real-photo collector: download -> CLIP real-photo filter -> open-vocab detect & crop.

Output count policy: the final number of saved images is NOT capped.
`--n` only controls candidate-pool size (how many to download); every candidate
that passes CLIP real-photo + category filtering AND yields a valid detection
box will be saved.
"""
import argparse, shutil, os
from pathlib import Path
from PIL import Image
import torch
import open_clip
from ultralytics import YOLO
from icrawler.builtin import BingImageCrawler, BaiduImageCrawler

ROOT = Path(__file__).parent
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


def download(query_list, raw_dir, per_kw=40):
    raw_dir.mkdir(exist_ok=True)
    for i, kw in enumerate(query_list):
        for engine_name, Engine in [("bing", BingImageCrawler), ("baidu", BaiduImageCrawler)]:
            d = raw_dir / f"{engine_name}_{i}"
            d.mkdir(exist_ok=True)
            try:
                Engine(storage={"root_dir": str(d)},
                       feeder_threads=2, parser_threads=2, downloader_threads=4
                       ).crawl(keyword=kw, max_num=per_kw, min_size=(300, 300),
                               file_idx_offset="auto")
            except Exception as e:
                print(f"[{engine_name}] {kw}: {e}")


def gather_images(raw_dir):
    files = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp", "*.bmp"):
        files.extend(raw_dir.rglob(ext))
    return sorted(set(files))


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
def clip_scores(model, preprocess, files, real_prompts, fake_prompts,
                category_prompts=None, batch=32):
    """Return list of dicts: {file, real_score, cat_score (or None)}."""
    real_t = real_prompts  # already encoded
    fake_t = fake_prompts
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
        # real vs fake: softmax over [real_mean, fake_mean] per-image
        sim_real = (feats @ real_t.T).mean(dim=-1)
        sim_fake = (feats @ fake_t.T).mean(dim=-1)
        # temperature 100 like CLIP
        s = torch.stack([sim_real, sim_fake], dim=-1) * 100
        prob_real = s.softmax(dim=-1)[:, 0].cpu().tolist()

        cat_scores = [None] * len(ok)
        if category_prompts is not None:
            sim_cat = (feats @ category_prompts.T) * 100
            prob_cat = sim_cat.softmax(dim=-1)[:, 0].cpu().tolist()  # first is positive
            cat_scores = prob_cat

        for f, pr, pc in zip(ok, prob_real, cat_scores):
            out.append({"file": f, "real": pr, "cat": pc})
    return out


def collect(query_list, detect_prompt, out_dir, n=50, raw_dir=None,
            category_pos=None, category_neg=None,
            real_thresh=0.7, cat_thresh=0.5, candidates_factor=6,
            yolo_world="yolov8s-worldv2.pt", min_box=60):
    """
    query_list: search keywords (multiple language/variants)
    detect_prompt: text for YOLO-World detection (e.g., "egyptian mau cat")
    category_pos / category_neg: optional CLIP prompts for fine category filtering
        e.g. pos=["egyptian mau cat"], neg=["persian cat","tabby cat","ragdoll cat"]
    """
    out_dir = Path(out_dir); out_dir.mkdir(exist_ok=True)
    raw_dir = Path(raw_dir or (ROOT / "_raw"))

    target_candidates = n * candidates_factor
    per_kw = max(20, target_candidates // (len(query_list) * 2))
    download(query_list, raw_dir, per_kw=per_kw)
    files = gather_images(raw_dir)
    print(f"raw downloaded: {len(files)}")

    print("loading CLIP ViT-L/14...")
    clip_model, preprocess, tokenizer = load_clip()
    obj = detect_prompt
    real_t = encode_text(clip_model, tokenizer, [t.format(obj) for t in REAL_TEMPLATES])
    fake_t = encode_text(clip_model, tokenizer, [t.format(obj) for t in FAKE_TEMPLATES])

    cat_t = None
    if category_pos:
        cat_prompts = [f"a photo of a {p}" for p in category_pos] + \
                      [f"a photo of a {p}" for p in (category_neg or [])]
        # Build so that positives come first
        cat_t = encode_text(clip_model, tokenizer, cat_prompts)
        # For softmax-over-all-classes interpretation, use first class as target.
        # We'll compute prob mass over positive classes.
        n_pos = len(category_pos)

    scores = clip_scores(clip_model, preprocess, files, real_t, fake_t,
                         category_prompts=cat_t)

    # Filter
    kept = [s for s in scores if s["real"] >= real_thresh]
    if cat_t is not None:
        # Re-interpret: we want prob of being a positive class across all class prompts
        # Need to recompute per-image prob mass over positives
        kept2 = []
        # Re-encode kept images for cat distribution (could refactor; keep simple)
        for s in kept:
            try:
                img = Image.open(s["file"]).convert("RGB")
            except Exception:
                continue
            x = preprocess(img).unsqueeze(0).to(DEVICE)
            with torch.no_grad():
                fe = clip_model.encode_image(x)
                fe /= fe.norm(dim=-1, keepdim=True)
                sim = (fe @ cat_t.T) * 100
                probs = sim.softmax(dim=-1)[0]
                pos_mass = probs[:n_pos].sum().item()
            s["cat"] = pos_mass
            if pos_mass >= cat_thresh:
                kept2.append(s)
        kept = kept2

    # Free CLIP
    del clip_model
    torch.cuda.empty_cache()

    # Rank: real first, then cat
    kept.sort(key=lambda s: (s["real"] + (s["cat"] or 0)), reverse=True)
    print(f"after CLIP filter: {len(kept)} (real>={real_thresh}"
          + (f", cat>={cat_thresh}" if cat_t is not None else "") + ")")

    # YOLO-World detection
    print(f"loading {yolo_world}...")
    det = YOLO(yolo_world)
    det.set_classes([detect_prompt])

    saved = 0
    used_keys = set()
    for s in kept:
        f = s["file"]
        try:
            img = Image.open(f).convert("RGB")
        except Exception:
            continue
        # dedupe by (size, filesize)
        key = (img.size, os.path.getsize(f))
        if key in used_keys:
            continue
        used_keys.add(key)

        res = det.predict(source=str(f), conf=0.05, iou=0.5, verbose=False, imgsz=640)[0]
        if len(res.boxes) == 0:
            continue
        boxes = res.boxes
        best = int(boxes.conf.argmax())
        x1, y1, x2, y2 = map(int, boxes.xyxy[best].tolist())
        W, H = img.size
        mx = int(0.05 * (x2 - x1)); my = int(0.05 * (y2 - y1))
        x1 = max(0, x1 - mx); y1 = max(0, y1 - my)
        x2 = min(W, x2 + mx); y2 = min(H, y2 + my)
        if (x2 - x1) < min_box or (y2 - y1) < min_box:
            continue
        crop = img.crop((x1, y1, x2, y2))
        saved += 1
        crop.save(out_dir / f"{out_dir.name}_{saved:03d}.jpg", quality=92)

    print(f"saved {saved} to {out_dir}")
    return saved, raw_dir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--queries", nargs="+", required=True,
                    help="search keywords (can mix languages)")
    ap.add_argument("--detect", required=True, help="open-vocab detection prompt")
    ap.add_argument("--out", required=True, help="output directory name")
    ap.add_argument("--n", type=int, default=50,
                    help="target candidate count for sizing the download pool; "
                         "final output is NOT capped — every image passing all "
                         "filters is saved")
    ap.add_argument("--category-pos", nargs="*", default=None,
                    help="positive fine-category prompts for CLIP")
    ap.add_argument("--category-neg", nargs="*", default=None,
                    help="negative fine-category prompts (e.g. similar breeds)")
    ap.add_argument("--real-thresh", type=float, default=0.7)
    ap.add_argument("--cat-thresh", type=float, default=0.5)
    ap.add_argument("--keep-raw", action="store_true",
                    help="don't delete _raw after success")
    ap.add_argument("--yolo-world", default="yolov8s-worldv2.pt")
    args = ap.parse_args()

    saved, raw_dir = collect(
        query_list=args.queries,
        detect_prompt=args.detect,
        out_dir=ROOT / args.out,
        n=args.n,
        category_pos=args.category_pos,
        category_neg=args.category_neg,
        real_thresh=args.real_thresh,
        cat_thresh=args.cat_thresh,
        yolo_world=args.yolo_world,
    )
    if not args.keep_raw:
        shutil.rmtree(raw_dir, ignore_errors=True)
        print(f"removed {raw_dir}")
    if saved < args.n:
        print(f"NOTE: saved {saved} (< target {args.n}). "
              f"Lower thresholds or add more --queries to grow the pool.")


if __name__ == "__main__":
    main()
