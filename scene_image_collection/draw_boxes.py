"""Read collect_scene.py outputs (jpg + json) and draw bounding boxes onto copies.

Target box: red. Co-objects: blue. Boxes are saved as `<stem>_annotated.jpg` in --out-dir.
Originals are never overwritten.
"""
import argparse, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
ANNOT_DIR = ROOT / "images_annotated"


def _font(size=18):
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def draw_one(jpg_path: Path, json_path: Path, out_path: Path):
    img = Image.open(jpg_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    font = _font(max(14, img.size[0] // 60))
    meta = json.loads(json_path.read_text(encoding="utf-8"))

    tgt = meta["target"]
    x1, y1, x2, y2 = tgt["box"]
    draw.rectangle([x1, y1, x2, y2], outline="red", width=4)
    draw.text((x1 + 4, max(0, y1 - 22)),
              f'{tgt["prompt"]} {tgt["conf"]:.2f}',
              fill="red", font=font)

    for co in meta.get("co_objects", []):
        x1, y1, x2, y2 = co["box"]
        draw.rectangle([x1, y1, x2, y2], outline="blue", width=3)
        draw.text((x1 + 4, max(0, y1 - 20)),
                  f'{co["label"]} {co["conf"]:.2f}',
                  fill="blue", font=font)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, quality=92)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-dir", required=True,
                    help="directory containing <name>.jpg + <name>.json pairs")
    ap.add_argument("--out-dir", default=None,
                    help="output dir for *_annotated.jpg (default: "
                         "images_annotated/<basename of in-dir>/)")
    args = ap.parse_args()

    in_dir = Path(args.in_dir)
    out_dir = Path(args.out_dir) if args.out_dir else ANNOT_DIR / in_dir.name

    pairs = []
    for j in sorted(in_dir.glob("*.json")):
        i = j.with_suffix(".jpg")
        if i.exists():
            pairs.append((i, j))
    print(f"{len(pairs)} pairs found in {in_dir}")
    for jpg, jsn in pairs:
        draw_one(jpg, jsn, out_dir / f"{jpg.stem}_annotated.jpg")
    print(f"saved to {out_dir}")


if __name__ == "__main__":
    main()
