"""One-off remediation pass for low-yield classes.

Re-runs collect_scene.py with:
- richer scene queries that explicitly mention likely co-objects
- relaxed thresholds (--target-max-ratio 0.7, --co-conf-thresh 0.15, --real-thresh 0.5)
- larger candidate pool (--n 120)
- --start-index to continue numbering after the existing files

Outputs are merged into the existing class directories.
"""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).parent
IMAGES_DIR = ROOT / "images"

# class_dir : (richer_scene_queries, target_prompt)
REMEDY = {
    "clothes_irons": (
        ["clothes iron on ironing board", "person ironing shirt",
         "steam iron with laundry basket", "iron and hanger laundry room",
         "熨斗 烫衣板", "熨斗 衣架", "熨斗 衣物"],
        "iron",
    ),
    "radio_telescopes": (
        ["radio telescope with mountains", "radio telescope and antenna",
         "radio observatory tower landscape", "FAST telescope dish ground",
         "射电望远镜 山", "射电望远镜 地面"],
        "telescope",
    ),
    "brooms": (
        ["broom and dustpan", "person sweeping with broom",
         "broom against chair kitchen", "broom in shop corner",
         "扫帚 簸箕", "扫帚 厨房", "扫帚 角落"],
        "broom",
    ),
    "revolvers": (
        ["revolver in holster on belt", "revolver and bullets on table",
         "revolver on wood table", "左轮手枪 子弹", "左轮手枪 枪套"],
        "handgun",
    ),
    "missiles": (
        ["missile on truck launcher", "missile in museum with soldier",
         "missile parade vehicle", "missile launch tower",
         "导弹 卡车", "导弹 阅兵", "导弹 展览"],
        "missile",
    ),
    "pool_tables": (
        ["pool table with cues on wall", "pool table with people playing",
         "billiard table chairs bar", "pool table balls and cue stick",
         "台球桌 球杆", "台球桌 人 玩"],
        "pool table",
    ),
    "mittens": (
        ["child wearing mittens with scarf", "mittens and hat winter",
         "mittens on snow with sled", "person mittens skiing",
         "连指手套 围巾", "连指手套 雪 滑雪"],
        "mitten",
    ),
    "parachutes": (
        ["parachutist with parachute landing field", "skydiver parachute and harness",
         "parachute open with person sky", "paratrooper landing ground",
         "降落伞 着陆 人", "降落伞 跳伞员"],
        "parachute",
    ),
    "mailbags": (
        ["mailman with mailbag and letters", "postal worker bag at mailbox",
         "mail courier bag and packages", "mailbag with envelopes",
         "邮差 邮袋 信件", "邮差 邮箱 包裹"],
        "bag",
    ),
    "boletes": (
        ["bolete mushroom on forest floor with leaves", "porcini in basket with moss",
         "bolete mushroom near fallen log", "Boletus edulis on grass leaves",
         "牛肝菌 落叶 森林", "牛肝菌 篮子 苔藓"],
        "mushroom",
    ),
    "daisies": (
        ["daisies in vase on table", "daisy bouquet with hand",
         "daisies in garden with bees", "daisy field with grass",
         "雏菊 花瓶", "雏菊 草地 蜜蜂"],
        "flower",
    ),
}


def existing_count(name: str) -> int:
    d = IMAGES_DIR / name
    if not d.is_dir():
        return 0
    return len(list(d.glob("*.jpg")))


def run_one(name, queries, target, start_index):
    cmd = [sys.executable, str(ROOT / "collect_scene.py"),
           "--queries", *queries,
           "--target", target,
           "--out", name,
           "--n", "120",
           "--min-side", "800",
           "--target-max-ratio", "0.7",
           "--real-thresh", "0.5",
           "--co-conf-thresh", "0.15",
           "--start-index", str(start_index)]
    print(f"\n========== REMEDY {name} (start_index={start_index}) ==========")
    print(" ".join(f'"{a}"' if " " in a else a for a in cmd[2:]))
    res = subprocess.run(cmd, cwd=str(ROOT))
    return res.returncode


def main():
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    summary = []
    for name, (queries, target) in REMEDY.items():
        if only and name not in only:
            continue
        before = existing_count(name)
        rc = run_one(name, queries, target, start_index=before)
        after = existing_count(name)
        summary.append((name, "ok" if rc == 0 else f"fail({rc})", before, after, after - before))

    print("\n========== REMEDY SUMMARY ==========")
    print(f"{'class':30s} {'status':10s} before  after  +delta")
    for name, status, before, after, delta in summary:
        print(f"{name:30s} {status:10s} {before:6d} {after:6d} {delta:+6d}")


if __name__ == "__main__":
    main()
