# 现有目标检测数据集综述与本数据集的必要性

> 报告日期：2026-05-12
> 范围：评估公开目标检测/定位数据集是否能满足本工程 `scene_image_collection/` 的需求，并论证为什么仍需自建。

---

## 1. 本数据集的需求规格

`scene_image_collection/` 的目标是为 **EEG 视觉刺激实验** 准备图像，每张样本必须同时满足：

1. **细粒度类别**：来自 `img_list.txt` 的 40 个 ImageNet-1k synset（如 n02106662 德国牧羊犬、n03297495 浓缩咖啡机、n13054560 牛肝菌），不能用粗粒度父类（"dog"、"coffee maker"）替代——EEG 解码任务依赖类别可分性，粗类会损失刺激设计的语义维度。
2. **真实拍摄**：排除卡通、雕塑、表情包、CG、绘画。
3. **场景化构图**：单图内必须有 **≥ 1 个非目标共存物体**（人、家具、其它动物、餐具等），目标占比 < 50%，模拟自然观察场景。
4. **元数据可机读**：每张图配 JSON，记录目标框、共存物体框、置信度、来源检测器，方便后续按构图条件过滤而无需重跑流水线。

---

## 2. 现有目标检测/定位数据集对照

| 数据集 | 类别数 | 标注粒度 | 多目标场景 | 覆盖本工程 40 类 | 关键缺陷 |
|---|---|---|---|---|---|
| **COCO** (2014/2017) | 80 | 粗（"dog", "cat", "cell phone"） | ✅ 密集 | ❌ 仅 ~10/40 命中（且都是粗类） | 无细粒度品种/型号；无 espresso machine、jack-o-lantern、bolete、Egyptian Mau 等 |
| **Pascal VOC** | 20 | 粗 | 中等 | ❌ ~5/40 | 类别太少 |
| **Open Images V7** | ~600 | 粗到中 | ✅ 密集 | ⚠ ~25/40 粗类命中 | 同样无细粒度品种；标注稀疏（每图非穷尽） |
| **Objects365** | 365 | 粗到中 | ✅ 密集 | ⚠ ~20/40 粗类命中 | 无 ImageNet 级细分 |
| **LVIS** | 1203 | 中（含长尾） | ✅ 密集 | ⚠ ~30/40（粗-中类） | 没有 ImageNet 品种细分（无 German Shepherd vs Husky） |
| **ILSVRC DET** | 200 | 中 | 单/多 | ⚠ 父类合并，丢失细粒度 | 把 1000 类合成 200 个父类，正是丢掉了我们要的粒度 |
| **ImageNet Object Localization (ILSVRC2012-Loc)** | 1000 | **细粒度（synset 级）✅** | ❌ **基本一图一框** | ✅ **40/40 全部覆盖** | 单主体定位标注，缺多目标共存场景 |
| **ImageNet BBox 全集** (image-net.org) | ~3000 synsets | 细 | ❌ 单主体 | ✅ 40/40 | 同上 |
| **Visual Genome** | 开放词表（~33k 对象类型） | 中（自由文本）| ✅ 密集 | ⚠ 拼写/对齐困难 | 标注噪声大；细粒度词不规范，与 ImageNet synset 无 1-1 映射 |
| **iNaturalist (检测分支)** | ~10k 物种 | 极细（动植物）| ❌ 单主体 | 部分（仅动植物类）| 不覆盖人造物；非场景图 |

### 直接 EEG 视觉刺激相关数据集

| 数据集 | 类别 | 是否带检测框 | 是否多目标共存 | 备注 |
|---|---|---|---|---|
| Spampinato 2017 (40 类 EEG) | 40 ImageNet 类 | ❌ | ❌ 单主体 | 与本工程类目高度重合，但只有刺激图、没有检测/共存标注 |
| THINGS-EEG2 (Gifford et al. 2022) | 1854 概念 | ❌ | ❌ 居中单主体 | 概念级图像库，无检测框 |
| BOLD5000 / NSD (fMRI) | COCO/SUN 子集 | 部分（继承 COCO） | ✅ | 是脑影像，不针对 EEG；类别非细粒度 |

---

## 3. 关键差距：没有任何公开数据集同时满足「细粒度 synset」+「多目标共存」

| 维度组合 | 公开数据集 |
|---|---|
| 细粒度 + 单主体 | ✅ ImageNet-Loc / ImageNet BBox |
| 粗粒度 + 多目标场景 | ✅ COCO / Open Images / Objects365 / LVIS |
| **细粒度 + 多目标场景** | ❌ **空白** |

EEG 视觉刺激设计需要的恰好是右下角这格——既要保证类别在 ImageNet 级别的可分性（实验范式与 Spampinato/THINGS 系列对齐），又要让刺激包含真实场景中的视觉竞争与上下文（贴近自然观察、便于研究 EEG 中的对象-场景交互信号）。

---

## 4. 本工程已采集的产物（截至 2026-05-12）

`scene_image_collection/images/` 下覆盖了全部 40 个类别（外加 `egyptian_mau_scenes/` 与 `egyptian_mau_cats/` 两轮重复采集，后续需合并去重），每张图配 JSON 元数据，记录目标框、共存物体（COCO YOLOv8 + YOLO-World LVIS 风格词表）、置信度和来源检测器。可视化副本在 `images_annotated/`。

> **当前图片数量仅为流水线的自动产物，未做人工质检**：CLIP 真实性、YOLO-World 目标定位、共存物体扫描都可能误判（卡通漏过、目标错框、共存物其实是目标的局部、构图不符合 EEG 刺激要求等）。最终人工筛选后的留量预计**远低于**当前自动产物，因此本报告**不**以当前数量作为「足够 / 不足」的判断依据；类别平衡与扩采决策需等人工审核完成后再定。

**与现有公开数据集无重复**：
- 抓取来源是 Bing/Baidu 实时搜索，标注由我们自动生成（YOLO-World + COCO YOLOv8），不复用任何外部数据集的图或标注文件。
- 关键的不可替代性见下一节，**不**指望「过滤口径」「JSON 字段」这类工程差异作为创新点。

---

## 5. 真正的创新点（核查后修正）

经过对 Open Images V7 类目表、LVIS 1203 类目、ILSVRC DET 200 类、ImageNet-Loc 任务设计、Visual Genome WordNet 对齐策略，以及 EEG-ImageNet (2024) / NOD MEG-EEG (2025) 等近期 EEG 视觉刺激数据集的比对（见 §2），**唯一站得住脚的创新点**是：

> **在 ImageNet-1k 细粒度 synset 标签下，单图同时给出目标 + 非目标共存物体的检测框。**

证据：

| 检查的潜在 prior | 是否同时满足「细粒度 synset」和「多目标共存框」 |
|---|---|
| Open Images V7（600 boxable） | ❌ 只有 "Dog"/"Cat"，无品种；17 个具体类逐一核查均不在类表 |
| LVIS（1203） | ❌ 仅粗类「dog/cat/guitar/piano/camera/mushroom」；giant_panda 个别命中，但整体非 ImageNet-1k 对齐 |
| ILSVRC DET（200） | ❌ 文档明确写 "DET dataset contains the parent 'dog' category"，细粒度品种被父类合并 |
| ImageNet-Loc（1000）| ❌ 单类定位任务，只标目标 synset，不标共存的其它类对象 |
| Visual Genome | ⚠ WordNet 对齐但自动映射默认到最常见父 synset，长尾品种实例稀疏，不是为细粒度 synset 检测设计 |
| EEG-ImageNet (2024) / NOD (2025) | ❌ 都是单主体 ImageNet 风格刺激，无场景、无 box |

### 我之前列过但**不**成立的「创新点」

- **CLIP 真实性过滤** — 不算创新。COCO/LVIS/Open Images/ImageNet 都是人工采集筛选过的，本来就是真实图。我们用模型替代人工只是降本，不改变产物性质。
- **JSON 元数据格式** — 不算创新。COCO/Pascal 的 JSON/XML 同样可以记录任意字段，是工程实现差异。
- **「EEG 友好元数据」** — 不成立（前一轮已修正）。当前 JSON 只是通用检测元数据，无 EEG 专属字段。
- **过滤口径组合** — 工程参数选择，非学术贡献。

### 还需要诚实交代的限制

- **共存框是模型自动生成、非 ground truth**：YOLO-World + YOLOv8 COCO 在共存物体上的 precision/recall 没有人工核验。如果将来要发表，必须明确为「弱监督 / 模型自动标注」，或对一个子集做人工金标准评估。
- **细粒度 synset 标签也来自查询关键词，非人工核验**：图是按 "Egyptian Mau in living room" 这样的 query 抓的，类标的可靠性取决于 CLIP 真实性过滤 + YOLO-World 对粗父类的检出，**没有**像 ImageNet 那样让人工核对每张图是否真是埃及猫而非别的猫种。这是与 ImageNet 一类金标准数据集的实质差距，必须人工质检后再宣称细粒度可靠性。

---

## 6. 结论

**唯一站得住脚的差异**是「ImageNet-1k 细粒度 synset 标签 × 单图多目标共存框」这一组合，公开数据集中确实没有同时满足这两点的方案。继续维护 `collect_scene.py` 自建流水线是合理的，但宣传这一数据集时必须只主张这一项创新，**不要**把工程上的过滤/格式差异包装成学术贡献。

下一步建议：

- **人工质检（前置必做）**：对当前自动产物逐类过一遍，剔除 CLIP/YOLO-World 误判，并在质检中显式核对**细粒度类标**（这张图真的是埃及猫而非别的猫种吗？），否则「ImageNet 级细粒度」的卖点站不住。
- 合并 `egyptian_mau_cats` 与 `egyptian_mau_scenes` 去重。
- 对**共存物体框**抽样做人工金标准评估，公布 precision/recall，否则只能宣称「弱监督共存标注」。
- 等人工质检完成后再决定扩采、阈值调整、query 增补。
- 统计共存物体类别分布（人工筛后），避免「person 出现率 > 80%」这种过度集中。

---

## 参考

- ImageNet Object Localization Challenge (Kaggle): https://www.kaggle.com/c/imagenet-object-localization-challenge/data
- ImageNet BBox 下载: https://image-net.org/download-bboxes.php
- COCO: https://cocodataset.org
- Open Images V7: https://storage.googleapis.com/openimages/web/index.html
- Objects365: https://www.objects365.org
- LVIS: https://www.lvisdataset.org
- Visual Genome: https://homes.cs.washington.edu/~ranjay/visualgenome/
- ILSVRC paper: https://arxiv.org/abs/1409.0575
- Spampinato et al. 2017 (40-class EEG): https://arxiv.org/abs/1609.00344
- Gifford et al. 2022 (THINGS-EEG2): https://www.sciencedirect.com/science/article/pii/S1053811922008758
- EEG-ImageNet (2024, multi-granularity ImageNet stimuli): https://arxiv.org/abs/2406.07151
- NOD MEG/EEG ImageNet-1k stimuli (2025): https://pmc.ncbi.nlm.nih.gov/articles/PMC12102372/
- Open Images V7 boxable categories CSV: https://storage.googleapis.com/openimages/v7/oidv7-class-descriptions-boxable.csv
- LVIS API (categories source): https://github.com/lvis-dataset/lvis-api
