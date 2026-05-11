# 流水线内部结构（collect.py）

## 数据流
```
download()        icrawler: Bing+Baidu × 关键词，分流到 _raw/{engine}_{i}/
   ↓
gather_images()   汇总全部候选
   ↓
load_clip()       CLIP-ViT-L/14 (openai)
   ↓
clip_scores()     对每张图计算 real_score（必）+ cat_score（可选）
   ↓
[筛选 + 排序]    real ≥ real-thresh ∩ cat ≥ cat-thresh，按综合分降序
   ↓
YOLO-World        set_classes([detect_prompt])，imgsz=640, conf=0.05
   ↓
[裁剪 + 加 5% 边距 + min_box 检查] → 保存到 out_dir
   ↓
成功则删 _raw/，否则保留供重试
```

## 关键函数
- `download(query_list, raw_dir, per_kw)`：每个 `(engine, keyword)` 独立子目录，防止文件名覆盖；`file_idx_offset="auto"` 让 icrawler 在子目录内自动续编号。
- `load_clip()`：加载 `ViT-L-14` + `openai` 预训练权重，返回 model / preprocess / tokenizer。
- `encode_text(...)`：把 prompt 列表编码成单位向量，便于后续点积求相似度。
- `clip_scores(...)`：分批前向，对每张图同时算 `real_score` 和（可选）`cat_score`。
- `collect(...)`：主入口，串起 download → CLIP filter → YOLO-World detect。

## 设计取舍要点
- **CLIP 用完即释放**：检测前 `del clip_model; torch.cuda.empty_cache()`，显存峰值压在 ~3 GB。
- **候选量自适应**：默认 `n × 6` 候选，再除以 `len(queries) × 2`（双引擎）作为每关键词下载量。
- **去重**：粗粒度用 `(image.size, file_size)` 哈希，避免完全相同的图被多次裁剪。pHash 待加。
- **细类不进检测词**：见 `tech_stack.md` §2.C "关键经验"——`--detect` 永远用通用类，细类靠 CLIP 的 `--category-*`。

更详细的设计演进、踩坑点、版本对比见 `logs/2026-05-11_egyptian_mau_pipeline.md`。
