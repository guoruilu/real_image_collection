# EEG_Obj_Detection — 真实图像采集系列

> 项目名沿用历史命名。**实际职能**：为 EEG 物体识别任务采集真实照片数据集。给定一个类别（埃及猫、吉他、马、熊猫……），从互联网下载图片 → 过滤掉卡通/插画/表情包/手办等非真实照片 → 输出可用的图像数据。

本目录下有两个子工程，对应两种产物形态：

## 子工程

| 子工程 | 产物 | 适用场景 |
|---|---|---|
| [`small_image_collection/`](small_image_collection/) | 目标主体的**精确裁剪小图**（已用 YOLO-World 裁好） | 单一物体识别、分类训练样本、紧凑刺激 |
| [`scene_image_collection/`](scene_image_collection/) | **带共存物体的场景大图**（原图 + JSON 元数据 + 可视化画框工具） | 多目标共存识别、EEG 复杂视觉刺激 |

## 共享资源

- `CLAUDE.md` — 协作约定（日志/文档/真实性/数量规则），两个子工程共用
- `img_list.txt` — 30 类 ImageNet wnid + 中文类别列表，两个子工程通过 `../img_list.txt` 引用
- `.gitignore` — 共用一份，排除所有图像和模型权重文件

## 30 秒上手

进入对应子工程，按其 `README.md` 操作。例如：

```bash
cd small_image_collection
python collect.py --queries "acoustic guitar" "原声吉他" --detect "guitar" --out guitars --n 50
```

或：

```bash
cd scene_image_collection
python collect_scene.py --queries "Egyptian Mau in living room" "埃及猫 客厅" \
  --target "cat" --out egyptian_mau_scenes --n 80
```

## 目录结构

```
real_image_collection/
├── README.md                  # 本文件
├── CLAUDE.md                  # 协作约定（两子工程共用）
├── img_list.txt               # 30 类列表（共享）
├── .gitignore                 # 共享
├── small_image_collection/    # 子工程 A：裁剪小图
│   ├── collect.py
│   ├── run_all.py
│   ├── README.md
│   ├── docs/
│   ├── logs/
│   └── images/
└── scene_image_collection/    # 子工程 B：场景大图
    ├── collect_scene.py
    ├── run_all.py
    ├── draw_boxes.py
    ├── README.md
    ├── docs/
    ├── logs/
    ├── images/                # 原图 + JSON
    └── images_annotated/      # 画框可视化
```
