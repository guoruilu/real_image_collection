# EEG_Obj_Detection — 真实物体图片采集与精确裁剪流水线

> 项目名沿用历史命名，**实际职能**是：给定一个类别（埃及猫、吉他、马、熊猫……），自动从互联网下载图片 → 过滤掉卡通/插画/表情包/手办等非真实照片 → 用开放词表检测器精确裁剪出目标物体 → 把所有过得了过滤的图像全部保存下来。

## 这个项目能做什么

输入一个/多个搜索关键词和一个检测词，输出全部「真实拍摄 + 已裁剪到目标」的 JPG（**数量不设上限**，过滤出多少存多少）。

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

然后跑：
```bash
cd ~/prjs/EEG_Obj_Detection
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
| 历次任务日志、版本演进、踩坑记录 | [logs/](logs/) |
| 与 Agent 协作的项目约定 | [CLAUDE.md](CLAUDE.md) |

## 目录结构
```
~/prjs/EEG_Obj_Detection/
├── README.md                   # 本文件（梗概）
├── CLAUDE.md                   # 协作约定（日志/文档更新规则）
├── collect.py                  # 主流水线（CLI 入口）
├── docs/                       # 详细文档
│   ├── usage.md
│   ├── tech_stack.md
│   ├── models.md
│   └── pipeline.md
├── logs/                       # 任务日志（每次任务追加一份 md）
│   └── 2026-05-11_egyptian_mau_pipeline.md
├── egyptian_mau_cats/          # 第一次跑出的 50 张埃及猫
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
- [x] 通用采集流水线 `collect.py`
- [x] 埃及猫 50 张产出（验证流水线，存放于 `egyptian_mau_cats/`）
- [x] 项目约定 `CLAUDE.md`、文档体系 `docs/`、历史日志 `logs/`

### 🚧 待完成（按优先级）
1. **跑其他类别**：吉他、马、熊猫……（命令模板见 `docs/usage.md`）
2. **流水线鲁棒性**：
   - 加 pHash 近似图去重（目前只按 `(size, filesize)` 粗去重）
   - 加 `--engines bing,baidu,google` 开关；中文关键词可禁用 Bing 提速
   - 真实性过滤负模板按类别裁剪（吉他不需要 "plush toy / figurine"）
3. **质量评估**：
   - 写一个小脚本随机抽样产出图做人工核验，记录 precision
   - 跨类别的稳定阈值表（real/cat 的合适默认值）
4. **EEG 关联（原项目意图，待用户澄清）**：
   - 项目名含 "EEG"，但当前流水线只做图像采集，未涉及脑电信号处理
   - 推测后续要把这些图作为视觉刺激集，配合 EEG 做物体识别任务——具体方向请询问用户
