# small_image_collection — 真实物体图片采集与精确裁剪

给定一个/多个搜索关键词和一个检测词，输出全部「真实拍摄 + 已裁剪到目标」的 JPG（**数量不设上限**，过滤出多少存多少）。

- **真实性过滤**：CLIP-ViT-L/14 用「照片 vs 卡通/插画/3D 渲染/表情包/手办/绘画/动漫」多模板对比打分，剔除非照片。
- **细类过滤（可选）**：对易混类别（如猫的品种）做 CLIP 二次分类。
- **开放词表裁剪**：YOLO-World 接受任意文本作为检测类，不限 COCO 80 类。
- **多源抓取**：Bing + Baidu 并行，中英文混合关键词。
- **自动清理**：成功后删除候选缓存 `_raw/`。

## 30 秒上手

新机器先建环境（详见 [docs/setup.md](docs/setup.md)）：
```bash
conda env create -f environment.yml && conda activate eh
```

然后：
```bash
cd ~/prjs/EEG_Obj_Detection/real_image_collection/small_image_collection
python collect.py --queries "acoustic guitar" "原声吉他" --detect "guitar" --out guitars --n 50
```

完整参数、调阈值经验、带细类过滤的例子见 [docs/usage.md](docs/usage.md)。

## 文档地图

| 想知道 | 看哪 |
|---|---|
| 怎么在新机器上建环境 | [docs/setup.md](docs/setup.md) |
| 怎么用 `collect.py`、参数表、调参经验 | [docs/usage.md](docs/usage.md) |
| 用了哪些模型、为什么选它们、各自角色 | [docs/tech_stack.md](docs/tech_stack.md) |
| 模型权重去哪下、缓存在哪、离线打包 | [docs/models.md](docs/models.md) |
| `collect.py` 内部数据流和函数 | [docs/pipeline.md](docs/pipeline.md) |
| 历次任务日志 | [logs/](logs/) |
| 与 Agent 协作的项目约定 | [../CLAUDE.md](../CLAUDE.md) |

## 目录结构

```
small_image_collection/
├── README.md
├── collect.py                  # 主流水线（CLI 入口）
├── run_all.py                  # 批量驱动：按内嵌 CONFIG 跑全部类别
├── docs/                       # 详细文档
├── logs/                       # 任务日志
├── images/                     # 所有类别产出统一在这下面
│   └── <class_name>/           # 30 个类别目录
├── yolov8n.pt                  # COCO YOLOv8 nano（v1 遗留，可删）
├── yolov8s-worldv2.pt          # YOLO-World 开放词表权重
└── _raw/                       # 候选图缓存，跑成功后自动删
```

## 资源参考（RTX 4070 Laptop 8GB）
- 显存峰值 ≈ 4 GB
- 单次任务（50 张产出）≈ 3–10 分钟，主要时间花在下载
- 首次运行需联网下载 CLIP-L 权重 ≈ 338 MB

## 已完成 / 待完成

### ✅ 已完成
- [x] 通用采集流水线 `collect.py`（带 YOLO 单图容错 + `--detect-fallback` 整图兜底）
- [x] 批量驱动 `run_all.py`，跑完 `../img_list.txt` 全 30 类，共 **2,916 张**
- [x] 输出策略：不限 50 张，过滤出多少存多少

### 🚧 待完成
1. pHash 近似图去重（目前只按 `(size, filesize)` 粗去重）
2. `--engines bing,baidu,google` 开关；中文关键词可禁用 Bing 提速
3. 真实性过滤负模板按类别裁剪（吉他不需要 "plush toy / figurine"）
4. 跨类别的稳定阈值表（real/cat 的合适默认值）
