"""Batch driver: run collect.py for every class in img_list.txt.

Reads CONFIG (defined below) for per-class queries / detect prompt / fine-category prompts.
Skips classes whose output dir already exists with > 50 files (already uncapped).
"""
import subprocess, sys, os
from pathlib import Path

ROOT = Path(__file__).parent

# class_dir : (queries, detect, category_pos|None, category_neg|None)
CONFIG = {
    "egyptian_mau_cats": (
        ["Egyptian Mau cat", "Egyptian Mau kitten", "Egyptian Mau breed",
         "spotted Egyptian Mau", "silver Egyptian Mau", "Egyptian Mau full body",
         "埃及猫", "埃及神猫", "埃及猫 写真"],
        "cat",
        ["egyptian mau cat", "spotted egyptian mau cat"],
        ["persian cat", "ragdoll cat", "siamese cat", "british shorthair cat",
         "bengal cat", "maine coon cat"],
    ),
    "lycaenid_butterflies": (
        ["lycaenid butterfly", "gossamer-winged butterfly", "hairstreak butterfly",
         "blue butterfly Lycaenidae", "copper butterfly Lycaenidae",
         "灰蝶", "灰蝶 蝴蝶", "灰蝶 自然", "灰蝶 标本", "Lycaenidae"],
        "butterfly",
        ["lycaenid butterfly", "small blue butterfly", "hairstreak butterfly",
         "copper butterfly"],
        ["swallowtail butterfly", "monarch butterfly", "white butterfly",
         "nymphalid butterfly", "skipper butterfly", "moth", "dragonfly"],
    ),
    "capuchin_monkeys": (
        ["capuchin monkey", "white-faced capuchin", "tufted capuchin",
         "black capuchin monkey", "Cebus capucinus",
         "卷尾猴", "白面卷尾猴", "黑帽悬猴", "悬猴"],
        "monkey",
        ["capuchin monkey", "white-faced capuchin monkey", "tufted capuchin monkey"],
        ["macaque", "spider monkey", "squirrel monkey", "marmoset", "tamarin",
         "chimpanzee", "baboon", "orangutan", "gorilla", "lemur"],
    ),
    "asian_elephants": (
        ["Asian elephant", "亚洲象", "Indian elephant", "Asian elephant in wild",
         "Elephas maximus"],
        "elephant",
        ["asian elephant", "indian elephant"],
        ["african elephant", "elephant toy", "elephant figurine", "elephant sculpture"],
    ),
    "clownfish": (
        ["clownfish", "小丑鱼", "anemonefish", "Amphiprion", "clownfish in anemone"],
        "fish",
        ["clownfish", "anemonefish"],
        ["goldfish", "koi fish", "tropical fish", "angelfish", "betta fish"],
    ),
    "airliners": (
        ["airliner", "客机", "passenger jet airplane", "commercial aircraft",
         "Boeing 737", "Airbus A320"],
        "airplane",
        ["passenger airliner", "commercial jet aircraft"],
        ["fighter jet", "private jet", "biplane", "helicopter", "rocket",
         "model airplane toy"],
    ),
    "brooms": (
        ["broom", "扫帚", "household broom", "straw broom"],
        "broom",
        None, None,
    ),
    "canoes": (
        ["canoe", "独木舟", "wooden canoe", "kayak canoe paddling"],
        "canoe",
        ["canoe boat"],
        ["yacht", "speedboat", "rowboat", "raft"],
    ),
    "convertibles": (
        ["convertible car", "敞篷车", "open-top car", "convertible sports car",
         "cabriolet car"],
        "car",
        ["convertible car", "open-top sports car"],
        ["sedan car", "SUV", "truck", "minivan", "coupe with hardtop", "car toy"],
    ),
    "desktop_computers": (
        ["desktop computer", "台式电脑", "PC tower", "desktop PC with monitor"],
        "computer",
        ["desktop computer tower", "PC tower"],
        ["laptop computer", "tablet", "smartphone", "monitor alone"],
    ),
    "digital_watches": (
        ["digital watch", "数码表", "digital wristwatch", "LCD digital watch"],
        "watch",
        ["digital watch", "digital wristwatch"],
        ["analog watch", "mechanical watch", "pocket watch", "smartwatch"],
    ),
    "electric_guitars": (
        ["electric guitar", "电吉他", "Stratocaster", "Les Paul guitar"],
        "guitar",
        ["electric guitar"],
        ["acoustic guitar", "bass guitar", "classical guitar", "guitar toy"],
    ),
    "electric_trains": (
        ["electric train", "电力火车", "electric locomotive", "high-speed electric train"],
        "train",
        ["electric train", "electric locomotive"],
        ["steam locomotive", "diesel locomotive", "toy train", "model train"],
    ),
    "espresso_machines": (
        ["espresso machine", "浓缩咖啡机", "espresso maker", "espresso coffee machine"],
        "coffee machine",
        ["espresso machine"],
        ["drip coffee maker", "french press", "moka pot", "kettle"],
    ),
    "grand_pianos": (
        ["grand piano", "三角钢琴", "concert grand piano"],
        "piano",
        ["grand piano"],
        ["upright piano", "digital piano", "keyboard piano", "piano toy"],
    ),
    "clothes_irons": (
        ["clothes iron", "熨斗", "steam iron", "electric iron"],
        "iron",
        ["clothes iron", "steam iron"],
        ["soldering iron", "waffle iron", "curling iron"],
    ),
    "jack_o_lanterns": (
        ["jack-o-lantern", "南瓜灯", "carved pumpkin Halloween", "Halloween pumpkin lantern"],
        "jack-o-lantern",
        ["jack-o-lantern carved pumpkin", "Halloween carved pumpkin"],
        ["uncarved pumpkin", "plastic pumpkin", "pumpkin pie"],
    ),
    "mailbags": (
        ["mailbag", "邮袋", "postal sack", "mail courier bag"],
        "bag",
        ["mailbag postal sack"],
        ["backpack", "handbag", "shopping bag"],
    ),
    "missiles": (
        ["missile", "导弹", "guided missile", "ballistic missile"],
        "missile",
        None, None,
    ),
    "mittens": (
        ["mitten", "连指手套", "winter mitten", "wool mitten"],
        "mitten",
        ["mitten gloves"],
        ["five-finger glove", "boxing glove", "oven mitt"],
    ),
    "mountain_tents": (
        ["mountain tent", "露营帐篷", "camping tent", "backpacking tent"],
        "tent",
        ["mountain tent", "camping tent"],
        ["circus tent", "wedding tent", "tent toy"],
    ),
    "pajamas": (
        ["pajamas", "睡衣", "pyjamas sleepwear", "two-piece pajamas"],
        "pajamas",
        ["pajamas pyjamas"],
        ["bathrobe", "nightgown", "underwear"],
    ),
    "parachutes": (
        ["parachute", "降落伞", "skydiving parachute"],
        "parachute",
        None, None,
    ),
    "pool_tables": (
        ["pool table", "billiard table", "台球桌", "snooker table"],
        "pool table",
        None, None,
    ),
    "radio_telescopes": (
        ["radio telescope", "射电望远镜", "radio telescope dish", "FAST radio telescope"],
        "telescope",
        ["radio telescope dish", "radio observatory dish"],
        ["optical telescope", "binoculars"],
    ),
    "reflex_cameras": (
        ["SLR camera", "reflex camera", "DSLR camera", "反光相机", "单反相机"],
        "camera",
        ["SLR camera", "DSLR reflex camera"],
        ["mirrorless camera", "compact camera", "phone camera", "film point-and-shoot"],
    ),
    "revolvers": (
        ["revolver handgun", "左轮手枪", "Colt revolver", "six-shooter revolver"],
        "handgun",
        ["revolver handgun"],
        ["semi-automatic pistol", "rifle", "shotgun", "toy gun"],
    ),
    "running_shoes": (
        ["running shoe", "sneaker", "运动鞋", "athletic running shoe"],
        "shoe",
        ["running shoe", "athletic sneaker"],
        ["dress shoe", "leather shoe", "boot", "sandal", "high heel"],
    ),
    "daisies": (
        ["daisy flower", "雏菊", "common daisy", "Bellis perennis"],
        "flower",
        ["daisy flower"],
        ["sunflower", "rose", "tulip", "chrysanthemum", "marigold"],
    ),
    "boletes": (
        ["bolete mushroom", "牛肝菌", "Boletus edulis", "porcini mushroom"],
        "mushroom",
        ["bolete mushroom", "boletus mushroom", "porcini"],
        ["agaric mushroom", "shiitake mushroom", "button mushroom", "amanita"],
    ),
}


def already_done(name: str) -> bool:
    """Skip if dir already has >50 files (means it was already uncapped)."""
    d = ROOT / name
    if not d.is_dir():
        return False
    return len(list(d.glob("*.jpg"))) > 50


def run_one(name, conf):
    queries, detect, pos, neg = conf
    cmd = [sys.executable, str(ROOT / "collect.py"),
           "--queries", *queries,
           "--detect", detect,
           "--out", name,
           "--n", "80",
           "--real-thresh", "0.55",
           "--cat-thresh", "0.2"]
    if pos:
        cmd += ["--category-pos", *pos]
    if neg:
        cmd += ["--category-neg", *neg]
    # remove any old (capped) output
    out = ROOT / name
    if out.exists():
        for f in out.glob("*.jpg"):
            f.unlink()
    print(f"\n========== {name} ==========")
    print(" ".join(f'"{a}"' if " " in a else a for a in cmd[2:]))
    res = subprocess.run(cmd, cwd=str(ROOT))
    return res.returncode


def main():
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    summary = []
    for name, conf in CONFIG.items():
        if only and name not in only:
            continue
        if already_done(name):
            print(f"-- skip {name} (already > 50 files)")
            summary.append((name, "skip", len(list((ROOT/name).glob('*.jpg')))))
            continue
        rc = run_one(name, conf)
        cnt = len(list((ROOT/name).glob("*.jpg")))
        summary.append((name, "ok" if rc == 0 else f"fail({rc})", cnt))

    print("\n========== SUMMARY ==========")
    for name, status, cnt in summary:
        print(f"{name:30s} {status:10s} {cnt} files")


if __name__ == "__main__":
    main()
