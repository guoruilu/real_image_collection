# 流水线内部结构（collect_scene.py）

## 数据流

```
download()                  icrawler Bing+Baidu × 关键词
   ↓
gather_images()             汇总 _raw/ 所有候选
   ↓
filter_by_resolution()      W ≥ min_side ∧ H ≥ min_side
   ↓
load_clip() / clip_real_scores()
                            CLIP-ViT-L/14 算 real_score
                            real_score ≥ real_thresh
   ↓
[释放 CLIP]
   ↓
YOLO("yolov8s-worldv2.pt").set_classes([target])
detect_target()             单类目标定位，取最高 conf 框
   ↓
[area_ratio < target_max_ratio]
   ↓
YOLO("yolov8s.pt")          COCO 80 类
YOLO("yolov8s-worldv2.pt").set_classes(LVIS_COMMON)
                            LVIS 风格 ~100 词
detect_co_objects()         合并去重，剔除与 target_box IoU>0.5 的框
   ↓
[≥ 1 个共存物体]
   ↓
保存 jpg + 同名 json
```

## 关键函数

- `download(query_list, raw_dir, per_kw)`：复用 small_image_collection 的多引擎多关键词子目录策略。`min_size=(600,600)`，比小图流水线的 300 更严，先在抓取阶段过滤小图。
- `filter_by_resolution(files, min_side)`：本工程独有，遍历 PIL.Image.size，仅保留 W 和 H 同时 ≥ 阈值的图。
- `clip_real_scores(...)`：复用 small_image_collection 的 real-vs-fake 多模板 softmax 打分，但**不**算 cat_score（细类匹配靠场景化 query）。
- `iou(a, b)` / `merge_boxes(boxes, iou_thresh)`：跨检测器的框合并（greedy NMS）。
- `detect_target(yolo_world_target, image_path, conf_thresh=0.1)`：YOLO-World 单类调用，取最高 conf 框。conf 阈值较低（0.1）确保不错过模糊场景中的目标。
- `detect_co_objects(yolo_coco, yolo_world_ext, ext_class_names, image_path, target_box, co_conf_thresh)`：双检测器并行扫描，合并、去重、剔除与目标重叠的框。

## 设计取舍

- **三个检测器序列加载**：CLIP 先用先释放；之后 `yolo_world_target`、`yolo_world_ext`、`yolo_coco` 三个 YOLO 同时在显存。RTX 4070 Laptop 8GB 实测峰值 ~5 GB。
- **共存物体不允许与目标重叠**：用 IoU>0.5 阈值剔除。避免「沙发=cat」这种误报被计入共存。
- **场景化 query 取代 small_image_collection 的细类 CLIP 二次分类**：用 `"Egyptian Mau in living room"` 比用 `"cat"` + 细类 CLIP 更直接，且对场景采集更有效。
- **`--n × 6` 候选池**：和 small_image_collection 一致；但本工程对每张图的过滤更严，建议把 `--n` 调到 80 以上。
- **JSON 元数据与图分离**：方便后续按元数据筛选（如「只要目标占比 < 0.3 的」「只要包含 person 的」），不需要重新跑流水线。

## 显存与时间

- CLIP-ViT-L/14：约 1.2 GB
- YOLO-World ×2：约 1.5 GB × 2
- YOLOv8s COCO：约 0.5 GB
- 综合峰值：~5 GB
- 单类 80 候选：约 5–15 分钟（下载占大头）
