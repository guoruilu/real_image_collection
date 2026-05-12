# 使用指南（scene_image_collection）

## 环境
与 `../small_image_collection/` 共用 `eh` conda 环境。无新增依赖（`ultralytics` 同时提供 COCO YOLOv8 和 YOLO-World）。

## 完整参数（collect_scene.py）

| 参数 | 必填 | 说明 |
|---|---|---|
| `--queries` | ✓ | 搜索关键词列表，**用场景化描述**（如 `"X in room"`、`"X with people"`、`"X 客厅"`），不要用单词特写 |
| `--target` | ✓ | YOLO-World 目标检测词，**用通用类**（`"cat"`、`"guitar"`、`"car"`），细类匹配靠场景化 query |
| `--out` | ✓ | 输出子目录名（最终路径 `images/<out>/`） |
| `--n` | | 候选池**目标量**（用于估算下载数），默认 80。最终输出不设上限 |
| `--min-side` | | 大图最小边长，默认 800 |
| `--target-max-ratio` | | 目标在图中占比上限，默认 0.5。降低（如 0.3）可强制更宽松的场景 |
| `--real-thresh` | | CLIP 真实性概率阈值，默认 0.55 |
| `--co-conf-thresh` | | 共存物体置信度阈值，默认 0.25 |
| `--yolo-world` | | YOLO-World 权重，默认 `yolov8s-worldv2.pt` |
| `--yolo-coco` | | COCO YOLOv8 权重，默认 `yolov8s.pt`（首次会自动下载） |
| `--keep-raw` | | 调试用，不删 `_raw/` |

## 输出策略

最终图片数量不设上限，所有通过全部过滤的图都会保存。`--n` 只用于估算候选池（下载 `n × 6` 张候选）。想要更多产出就加大 `--n` 和 `--queries`。

## 调阈值经验

- **产出过少**：
  - 加更多 `--queries`，尤其是场景化描述
  - 降低 `--min-side`（如 600）
  - 降低 `--co-conf-thresh`（如 0.15）
  - 提高 `--target-max-ratio`（如 0.7）
- **产出混了特写**：降低 `--target-max-ratio` 到 0.3
- **产出有低质量图**：提高 `--real-thresh` 到 0.7
- **共存物体几乎是同一个目标**：检查 LVIS 词表是否包含与 target 同义的词，必要时移除

## 画框可视化（draw_boxes.py）

```bash
python draw_boxes.py --in-dir images/egyptian_mau_scenes/
python draw_boxes.py --in-dir images/egyptian_mau_scenes/ --out-dir /tmp/check/
```

输出文件名 `<orig_stem>_annotated.jpg`，目标框红色 + 共存框蓝色 + 类别 + conf。
