# scene_image_collection — 含共存物体的「大图」采集

给定一个目标类别和场景化关键词，输出**整张原图**（不裁剪），要求：
1. 真实拍摄（CLIP 真实性过滤）
2. 分辨率足够大（默认 `--min-side 800`）
3. 目标在图中占比 < 50%（保证是「场景」而非「特写」）
4. 至少包含一个**非目标**的其它物体（用 COCO YOLOv8 + YOLO-World LVIS 风格词表共同扫描）

每张图配一份 JSON 元数据，记录目标框、共存物体框、置信度。`draw_boxes.py` 读 JSON 在原图上画框生成可视化副本（不覆盖原图）。

## 与 `../small_image_collection/` 的区别

| 维度 | small_image_collection | scene_image_collection（本目录） |
|---|---|---|
| 产物 | 裁剪后的目标主体 jpg | 整张原图 + JSON 元数据 |
| 共存物体 | 不关心 | 必须 ≥ 1 个非目标物体 |
| 分辨率 | 不限 | ≥ `--min-side`（默认 800） |
| 目标占比 | 不限 | < `--target-max-ratio`（默认 0.5） |
| 检测器 | YOLO-World 单类 | YOLO-World 目标 + YOLOv8 COCO + YOLO-World LVIS 词表 |

## 30 秒上手

环境与 `small_image_collection` 共用（同一个 `eh` conda 环境）。首次需额外下载 COCO YOLOv8 权重：

```bash
cd ~/prjs/EEG_Obj_Detection/real_image_collection/scene_image_collection
# yolov8s.pt 会在首次 YOLO("yolov8s.pt") 时由 ultralytics 自动下载
# yolov8s-worldv2.pt 可以从 ../small_image_collection/ 软链或复制过来
ln -s ../small_image_collection/yolov8s-worldv2.pt .
```

单类试跑：
```bash
python collect_scene.py \
  --queries "Egyptian Mau in living room" "埃及猫 客厅" "Egyptian Mau on sofa" \
  --target "cat" \
  --out egyptian_mau_scenes \
  --n 30
```

画框可视化：
```bash
python draw_boxes.py --in-dir images/egyptian_mau_scenes/
# 默认输出到 images_annotated/egyptian_mau_scenes/
```

批量跑全 30 类：
```bash
python run_all.py
# 或指定子集
python run_all.py egyptian_mau_cats clownfish
```

## 文档地图

| 想知道 | 看哪 |
|---|---|
| CLI 参数表、调参经验 | [docs/usage.md](docs/usage.md) |
| 流水线内部数据流 | [docs/pipeline.md](docs/pipeline.md) |
| 双检测器策略、LVIS 词表来源 | [docs/tech_stack.md](docs/tech_stack.md) |
| 现有公开数据集对照 + 本数据集必要性 | [docs/dataset_landscape.md](docs/dataset_landscape.md) |
| 研究计划速览（关键点决策表） | [docs/research_plan.md](docs/research_plan.md) |
| 研究计划完整论证（块设计原理、对照表、原文摘录） | [docs/research_plan_details.md](docs/research_plan_details.md) |
| 协作约定 | [../CLAUDE.md](../CLAUDE.md) |

## 目录结构

```
scene_image_collection/
├── README.md
├── collect_scene.py            # 主流水线（CLI 入口）
├── draw_boxes.py               # 可视化工具：JSON → 画框图
├── run_all.py                  # 批量驱动 30 类
├── docs/
├── logs/
├── images/<class>/             # <class>_NNN.jpg + <class>_NNN.json
└── images_annotated/<class>/   # <class>_NNN_annotated.jpg
```

## JSON 元数据格式

```json
{
  "source_path": "/.../_raw/bing_0/000005.jpg",
  "image_size": [1280, 853],
  "real_score": 0.71,
  "target": {
    "prompt": "cat",
    "box": [410.2, 220.5, 780.3, 612.1],
    "conf": 0.62,
    "area_ratio": 0.27
  },
  "co_objects": [
    {"label": "sofa", "box": [0, 180, 1280, 853], "conf": 0.81, "source": "coco"},
    {"label": "pillow", "box": [820, 320, 1010, 460], "conf": 0.44, "source": "yolo_world_lvis"}
  ]
}
```
