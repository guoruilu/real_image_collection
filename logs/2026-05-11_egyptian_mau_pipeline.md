# 2026-05-11 埃及猫图片采集 & 通用采集流水线建立

## 任务目标
1. 下载 50 张真实的埃及猫图片（排除卡通/表情包/插画/3D 渲染/手办等）
2. 把图中的猫精确裁剪出来
3. 构建可复用的流水线（后续会用于吉他、马、熊猫等其它类别）
4. 最终产物落到独立子目录，候选图任务完成后删除

## 环境
- 主机：WSL2 (Linux 6.6.114.1)，bash
- GPU：NVIDIA GeForce RTX 4070 Laptop GPU
- Conda 环境：`eh`（torch 2.6.0+cu126, opencv 4.11, pillow 12.2）
- 工程位置变更：`/mnt/e/wps/Projects/EEG_Obj_Detection` → `~/prjs/EEG_Obj_Detection`
  原因：从 Windows 挂载盘移到 Linux 本地盘以提高 I/O 性能。
  备注：原 Windows 路径下残留一个空目录，挂载层无法用 `rm` 删除（需从 Windows 端清理）。

## 依赖安装
在 `eh` 环境追加安装：
- `ultralytics` 8.4.48（YOLOv8 / YOLO-World）
- `icrawler`（Bing / Baidu 图像爬虫）
- `open_clip_torch`（CLIP-ViT-L/14 用于真实性 + 品种过滤）
- `pi-heif`、`pillow>=11.1` 由 ultralytics 自动升级

## 设计演进

### v1（已弃用）：YOLOv8n + 单语种关键词
- 流程：Bing icrawler 抓图 → YOLOv8n 检测 COCO `cat` 类 → 取置信度最高框 + 5% 边距裁剪
- 问题：Bing 单关键词只下到 4 张，后续关键词又覆盖目录（`file_idx_offset="auto"` 在跨次调用时失效），最终 0 张产出。

### v2（已弃用）：多语种多引擎 + 子目录分流
- 关键词扩展为中英文 8 个，Bing + Baidu 双引擎，每个 keyword/engine 独立子目录避免覆盖
- 候选图 190 张，YOLOv8n 裁出 50 张
- 问题：混入了卡通、表情包、艺术图、手办；无品种过滤，混有其它花猫品种

### v3（当前）：CLIP 双重过滤 + YOLO-World 开放词表检测
**关键设计：** 通用化，将来跑吉他/马/熊猫只需改命令行参数。
- 下载：多关键词（中英文）× 多引擎（Bing + Baidu），自动分流到子目录
- 真实性过滤：CLIP-ViT-L/14（openai 权重），对每张图计算
  - 正模板：`a photograph of {obj}`, `a real photo of {obj}`, `a candid photo of {obj}`, `a high-resolution photo of {obj}`
  - 负模板：`a cartoon/drawing/illustration/3d render/meme/clip art/painting/anime drawing/sketch/plush toy/figurine of {obj}`
  - 取正负模板特征的均值相似度，softmax(温度=100) 得到 `real_score`
- 品种过滤（可选）：CLIP 对正负品种 prompt 做 softmax，取正类概率质量
- 检测裁剪：YOLO-World v2（`yolov8s-worldv2.pt`），通过 `set_classes([detect_prompt])` 支持开放词表
  - 教训：detect_prompt 太具体（如 "egyptian mau cat"）时定位率低；改用通用类（"cat"）效果更好——品种已由 CLIP 把关
- 候选量：默认 `n × 6` 候选，按 `(real + cat)` 综合分排序后裁剪

## 关键参数（埃及猫这次）
```
--queries "Egyptian Mau cat" "Egyptian Mau kitten" "Egyptian Mau breed"
          "spotted Egyptian Mau" "silver Egyptian Mau" "Egyptian Mau full body"
          "bronze Egyptian Mau" "black smoke Egyptian Mau"
          "埃及猫" "埃及神猫" "埃及猫 写真"
--detect "cat"
--category-pos "egyptian mau cat" "spotted egyptian mau cat"
--category-neg "persian cat" "ragdoll cat" "siamese cat"
               "british shorthair cat" "bengal cat" "maine coon cat"
--real-thresh 0.55 --cat-thresh 0.2 --n 50
```

## 跑批数据
| 阶段 | 数量 |
|---|---|
| 原始下载（最终一次） | 919 |
| CLIP 真实性+品种过滤后 | 381 |
| YOLO-World 检测+裁剪 | 50 |

源头分布观察：Bing 引擎对中英文埃及猫关键词召回率低（多数 Bing 子目录只有 0~3 张，常出现"埃及"主题非猫的图）；Baidu 召回稳定（多数子目录 20~41 张）。CLIP 过滤承担了去噪主力。

## 资源消耗
- 显存峰值：~4 GB（CLIP-L + YOLO-World 同时加载时分两阶段，实际峰值各自约 2~3 GB）
- 磁盘：模型权重 ~1.2 GB（CLIP-L 338 MB + YOLO-World-s ~50 MB + yolov8n 6 MB），候选图过程峰值 ~300 MB
- 端到端耗时：~5 分钟（首次需下载 CLIP-L，约 3 分钟）

## 遇到的问题与解决
1. **Bing icrawler 跨次调用覆盖文件名**：改成每个 (engine, keyword) 独立子目录。
2. **首次 CLIP+YOLO-World 后只产出 24/50**：阈值过严（`real>=0.7, cat>=0.35`），放宽到 `0.55/0.2`。
3. **降阈值后仍只 49/50**：YOLO-World 用细类 prompt "egyptian mau cat" 定位率不足；改用通用类 "cat"（品种过滤交给 CLIP），一次出 50 张。
4. **最小裁剪框阈值**：默认 `min_box=80`，曾降到 60 但意义不大；最终保留 60。
5. **`grep` 过滤把后台日志全清空**：导致中间无法观察进度，改用 `TaskOutput` 直读后台输出。

## 产出
- 脚本：`collect.py`（CLI 通用入口）
- 输出目录：`egyptian_mau_cats/`（`egyptian_mau_cats_001.jpg` ~ `egyptian_mau_cats_050.jpg`）
- 模型权重缓存：`yolov8n.pt`, `yolov8s-worldv2.pt`（工程根目录）
- 项目约定：`CLAUDE.md`

## 后续可改进项（未实施）
- 加 `--keep-bing/--no-bing` 开关，关键词偏中文时直接禁用 Bing 引擎
- 加 Google 引擎备援（icrawler 内置 `GoogleImageCrawler`，需要 VPN）
- 真实性过滤的负模板可按类别动态裁剪（如吉他无需 "plush toy / figurine"）
- 增加近似图去重（pHash），目前仅按 `(size, filesize)` 粗去重
