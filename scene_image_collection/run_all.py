"""Batch driver for scene_image_collection: run collect_scene.py for every class.

Per-class config: scene-flavored queries + generic target prompt.
Reuses the class roster from real_image_collection/img_list.txt (parent dir).
"""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).parent
IMAGES_DIR = ROOT / "images"

# class_dir : (scene_queries, target_prompt)
CONFIG = {
    "german_shepherds": (
        ["German shepherd dog in yard", "German shepherd with handler",
         "German shepherd in park", "德国牧羊犬 户外", "德国牧羊犬 主人"],
        "dog",
    ),
    "horses": (
        ["horse in pasture", "horse with rider", "horses in field",
         "马 草原", "马 骑手"],
        "horse",
    ),
    "giant_pandas": (
        ["giant panda eating bamboo", "giant panda in zoo enclosure",
         "panda cub with mother", "大熊猫 竹子", "大熊猫 动物园"],
        "bear",
    ),
    "mobile_phones": (
        ["person using mobile phone", "smartphone on desk with laptop",
         "phone in hand outdoor", "手机 桌面", "手机 手"],
        "cellphone",
    ),
    "coffee_mugs": (
        ["coffee mug on table with breakfast", "coffee mug on desk",
         "person holding coffee cup cafe", "咖啡杯 桌面", "咖啡杯 早餐"],
        "cup",
    ),
    "folding_chairs": (
        ["folding chair in backyard", "folding chair at event",
         "folding chair camping", "折叠椅 院子", "折叠椅 户外"],
        "chair",
    ),
    "golf_balls": (
        ["golf ball on tee with club", "golf ball on green",
         "golf ball with golfer", "高尔夫球 球场", "高尔夫球 球杆"],
        "ball",
    ),
    "mountain_bikes": (
        ["mountain bike on trail", "mountain biker in forest",
         "mountain bike with rider", "山地自行车 山路", "山地自行车 骑手"],
        "bicycle",
    ),
    "bananas": (
        ["bananas on kitchen counter", "bananas in fruit bowl",
         "bananas at market stall", "香蕉 厨房", "香蕉 水果摊"],
        "banana",
    ),
    "pizzas": (
        ["pizza on table with drinks", "pizza on plate",
         "pizza in restaurant", "披萨 餐桌", "披萨 餐厅"],
        "pizza",
    ),
    "egyptian_mau_cats": (
        ["Egyptian Mau cat in living room", "Egyptian Mau on sofa",
         "Egyptian Mau in home", "埃及猫 客厅", "埃及猫 沙发", "埃及猫 家居"],
        "cat",
    ),
    "lycaenid_butterflies": (
        ["lycaenid butterfly on flower", "blue butterfly on plant",
         "hairstreak butterfly garden", "灰蝶 花朵", "灰蝶 自然"],
        "butterfly",
    ),
    "capuchin_monkeys": (
        ["capuchin monkey in forest", "capuchin monkey on tree",
         "白面卷尾猴 雨林", "卷尾猴 自然"],
        "monkey",
    ),
    "asian_elephants": (
        ["Asian elephant in wild", "Asian elephant with calf",
         "Asian elephant in forest", "亚洲象 野外", "亚洲象 群"],
        "elephant",
    ),
    "clownfish": (
        ["clownfish in anemone", "clownfish coral reef",
         "小丑鱼 海葵", "小丑鱼 珊瑚"],
        "fish",
    ),
    "airliners": (
        ["airliner on runway", "airliner at airport gate",
         "passenger jet boarding", "客机 机场", "客机 跑道"],
        "airplane",
    ),
    "brooms": (
        ["broom leaning against wall", "broom in kitchen corner",
         "扫帚 角落", "扫帚 室内"],
        "broom",
    ),
    "canoes": (
        ["canoe on lake", "canoe on river bank", "独木舟 湖", "独木舟 岸边"],
        "canoe",
    ),
    "convertibles": (
        ["convertible car on street", "convertible parked",
         "敞篷车 街道", "敞篷车 停"],
        "car",
    ),
    "desktop_computers": (
        ["desktop computer on desk", "PC tower with monitor desk setup",
         "台式电脑 书桌", "台式电脑 办公"],
        "computer",
    ),
    "digital_watches": (
        ["digital watch on wrist", "digital watch on table",
         "数码表 手腕", "数码表 桌面"],
        "watch",
    ),
    "electric_guitars": (
        ["electric guitar on stand", "electric guitar on stage",
         "电吉他 舞台", "电吉他 房间"],
        "guitar",
    ),
    "electric_trains": (
        ["electric train at station", "electric train on tracks",
         "电力火车 车站", "高铁 站台"],
        "train",
    ),
    "espresso_machines": (
        ["espresso machine in kitchen", "espresso machine cafe counter",
         "浓缩咖啡机 厨房", "咖啡机 吧台"],
        "coffee machine",
    ),
    "grand_pianos": (
        ["grand piano in room", "grand piano on stage",
         "三角钢琴 厅", "三角钢琴 舞台"],
        "piano",
    ),
    "clothes_irons": (
        ["clothes iron on ironing board", "steam iron in laundry",
         "熨斗 烫衣板", "熨斗 衣物"],
        "iron",
    ),
    "jack_o_lanterns": (
        ["jack-o-lantern on porch", "carved pumpkin on table",
         "南瓜灯 门廊", "南瓜灯 万圣节"],
        "jack-o-lantern",
    ),
    "mailbags": (
        ["mailman with mailbag", "postal worker mailbag",
         "邮差 邮袋", "邮差 街道"],
        "bag",
    ),
    "missiles": (
        ["missile on launcher", "missile in museum display",
         "导弹 发射", "导弹 展示"],
        "missile",
    ),
    "mittens": (
        ["mittens on hands snow", "mittens on table winter",
         "连指手套 雪地", "连指手套 桌面"],
        "mitten",
    ),
    "mountain_tents": (
        ["mountain tent in campsite", "camping tent forest",
         "露营帐篷 营地", "帐篷 野外"],
        "tent",
    ),
    "pajamas": (
        ["pajamas on bed", "person wearing pajamas in room",
         "睡衣 床", "睡衣 卧室"],
        "pajamas",
    ),
    "parachutes": (
        ["parachute skydiver in sky", "parachute open landing",
         "降落伞 跳伞", "降落伞 天空"],
        "parachute",
    ),
    "pool_tables": (
        ["pool table in bar", "billiard table in room",
         "台球桌 酒吧", "台球桌 球房"],
        "pool table",
    ),
    "radio_telescopes": (
        ["radio telescope landscape", "radio telescope dish field",
         "射电望远镜 远景", "射电望远镜 山"],
        "telescope",
    ),
    "reflex_cameras": (
        ["SLR camera in hands", "DSLR camera on table",
         "单反相机 手", "单反相机 桌面"],
        "camera",
    ),
    "revolvers": (
        ["revolver on table", "revolver in holster",
         "左轮手枪 桌面", "左轮手枪 枪套"],
        "handgun",
    ),
    "running_shoes": (
        ["running shoes on track", "running shoes on feet outdoor",
         "运动鞋 跑道", "运动鞋 路面"],
        "shoe",
    ),
    "daisies": (
        ["daisy flowers in field", "daisies in garden",
         "雏菊 田野", "雏菊 花园"],
        "flower",
    ),
    "boletes": (
        ["bolete mushroom in forest", "porcini mushroom on ground",
         "牛肝菌 森林", "牛肝菌 地面"],
        "mushroom",
    ),
}


def already_done(name: str) -> bool:
    d = IMAGES_DIR / name
    if not d.is_dir():
        return False
    return len(list(d.glob("*.jpg"))) > 0


def run_one(name, conf):
    queries, target = conf
    cmd = [sys.executable, str(ROOT / "collect_scene.py"),
           "--queries", *queries,
           "--target", target,
           "--out", name,
           "--n", "80",
           "--real-thresh", "0.55"]
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
            print(f"-- skip {name} (already has output)")
            summary.append((name, "skip", len(list((IMAGES_DIR/name).glob('*.jpg')))))
            continue
        rc = run_one(name, conf)
        cnt = len(list((IMAGES_DIR/name).glob("*.jpg")))
        summary.append((name, "ok" if rc == 0 else f"fail({rc})", cnt))

    print("\n========== SUMMARY ==========")
    for name, status, cnt in summary:
        print(f"{name:30s} {status:10s} {cnt} files")


if __name__ == "__main__":
    main()
