# 研究计划详情（完整论证版）

> 这是 [`research_plan.md`](research_plan.md) 的扩展。`research_plan.md` 是关键点速览，本文档保留所有论证细节、原文摘录、对照表、措辞模板与参考列表。
>
> 报告日期：2026-05-12（用户多轮 review 后修订）
> 目标会议：约 4 页的普通计算机或生理信号方向会议论文（非顶会）。

---

## 1. 三阶段 pipeline 定位（按用户澄清，最终方案）

| 阶段 | 输入 | 输出 | 数据集来源 | 与 EEG 的关系 |
|---|---|---|---|---|
| **Stage 1** | 被试 EEG 信号 | 40 类中的一个类标 | **EEG-ImageNet 公开数据集**（不是我们采集的） | 核心 EEG 任务 |
| **Stage 2** | 多目标场景图 + Stage-1 类标 | 该类目标的 bounding box | **本工程 `scene_image_collection/` 自建** | 仅把 Stage-1 类标作为 prior；本质是普通 OD 任务 |
| **Stage 3** | bbox 裁出 ROI + VQA 问题 | VQA 答案 | 现成 VQA 子集 / LLM 自动生成 / 模板化问题（待定） | 与 EEG 无关；下游任务 = VQA |

整体故事：**EEG 知道用户看什么 → OD 定位它在场景中的位置 → MLLM 基于 ROI 回答 VQA 问题** = end-to-end BCI VQA 助手。

关键澄清：
- 我们的多目标场景数据集 **不是 EEG 数据集**，是 **OD 数据集**，用于支撑 Stage 2。
- 数据集存在的理由是：EEG-ImageNet 没有多目标场景图，Stage 2/3 没有现成数据可用，所以我们自建。

## 1.1 已舍弃的备选方案（历史记录）

曾考虑过另外两个方向作为第三 contribution，**已确定不走**：
- **「真实 + LLM 生成训练 → OD 提升」**：CV 圈 X-Paste / GeoDiffusion / MosaicFusion 等已饱和；与 EEG 故事弱耦合；工作量大。舍。
- **「只做 pipeline + 数据集，2 个贡献」**：4 页能填但贡献略薄。舍。

最终方案 = 上方的三阶段 pipeline，第三 contribution 用 ROI→MLLM VQA + 双轨评估处理 Stage 1 误差传播。

---

## 2. 创新点核查（按阶段重新定位）

### 2.1 数据集本身（工具性贡献，非强创新）

之前曾论证「ImageNet-1k 细粒度 synset × 多目标共存框」是空白（[`dataset_landscape.md`](dataset_landscape.md) §5）。这一描述事实上仍然成立，但它的**定位是工具性贡献**——它是为支撑 Stage 2 而构造，自身不具备独立强创新性。

> 修正：先前文档把它描述为 "first-of-its-kind 数据集" 是过度包装。它确实在公开数据集中不存在，但只是因为之前没人需要 "把 EEG-ImageNet 的 40 个细粒度类放进多目标场景做 OD"。诉求够小众的话，"未被覆盖" 不等于 "强创新"。

应称为：**配套数据集 (companion dataset)**——为 Stage 2 实验提供必要载体，不在论文中作为独立贡献主张。

### 2.2 Stage 1（EEG → 类别）

- 数据集：复用 EEG-ImageNet 2024，没有数据集创新。
- 算法：EEGNet 或更新架构，**创新点在模型架构与训练策略**，不在数据。
- 这一阶段的可发表性看准确率（见 §3）和模型设计的差异化，与本工程的数据集无关。

### 2.3 Stage 2（场景图中按类定位）

整体 pipeline（EEG → 类别 → 场景定位 → MLLM VQA）公开 EEG 文献未见，这是把 BCI 从 "what" 推到 "what + where + answer" 的方向性贡献，**强创新**。

Stage 2 本身是普通 OD 任务，模型选型（YOLO-World / Grounding DINO / OWL-ViT 等）是工程选择，不算创新。

> 注：曾考虑过「真实+LLM 生成训练 → OD 提升」作为第三 contribution，但 CV 圈 X-Paste (ICML 2023) / GeoDiffusion (ICLR 2024) / MosaicFusion (IJCV 2024) / InstaGen / DiffusionEngine / AeroGen (CVPR 2025) / SOC / Controllable Diffusion (WACV 2024) / Beyond Objects 等已饱和；与 EEG 故事弱耦合、工作量大；**已舍弃**。详见 §1.1。

### 2.4 核心强创新点（总结）

✅ **唯一真正的强创新**：**三阶段 EEG → 多目标场景定位 → MLLM VQA pipeline**。

其它都是工具性 / 增量 / 复现：
- 数据集：配套贡献，不独立主张
- Stage 1：算法创新看模型，与数据集无关
- Stage 3 ROI→MLLM VQA：方向已被广泛验证，定位为 system-level evaluation；详见 §2.5

### 2.5 第三 contribution（已确定）：Stage 3 ROI → MLLM VQA

#### 2.5.1 想法

下游任务 = **VQA**（用户已确认 2026-05-12）。把 Stage 2 框出的 ROI 区域裁剪后喂给下游 MLLM 做 VQA，对比喂全图的：
- 输入 visual token 数
- 端到端延迟
- 单次调用成本（如 GPT-4o $/image）
- 下游任务质量是否保持

整体故事推到："**EEG 知道用户看什么 → OD 定位它在场景中的位置 → MLLM 基于 ROI 回答 VQA 问题**"——end-to-end BCI 视觉助手。

**VQA 数据来源选项**（定下后再细化）：
- 用现成 VQA 数据集（VQAv2、GQA、A-OKVQA、ScienceQA），筛选问题主体在 Stage-2 类别表里的子集
- 用 LLM 在 `scene_image_collection/` 图上自动生成围绕 Stage-2 类别的 VQA 问答对（需小规模人工核验质量）
- 配合 Stage-2 的 40 类，构造类似 "What color is the [class]?" / "What is the [class] doing?" 这样的模板化问题

#### 2.5.2 在 CV/MLLM 圈是否新颖

❌ **不新**。2024–2025 这是密集发表的方向：

| 工作 | 年份 | 路线 | 来源 |
|---|---|---|---|
| **V\* / SEAL** | CVPR 2024 | 引导式视觉搜索 → 高分辨率裁切再输入 | https://vstar-seal.github.io/ |
| **CROP** | 2025 | Contextual Region-Oriented Visual Token Pruning | arXiv:2505.21233 |
| **TEVA** | ICCV 2025 | Token-Efficient VLM via Dynamic Region Proposal | ICCV 2025 |
| **MLLMs Know Where to Look** | ICLR 2025 | training-free 小细节感知 | ICLR 2025 |
| **Visual Perception Token** | 2025 | Region selection token 触发裁切+重编码 | arXiv:2502.17425 |
| **AwaRes / ViCrop** | 2025 | 边缘端先定位再请求高分辨率 ROI | arXiv:2512.16349 |
| **Multi-Agent VQA** | 2024 | MLLM 调 detector → 裁剪 → 并行 LVLM | arXiv:2403.14783 |
| **Reinforcing VLMs to Use Tools** | 2025 | GRPO 训练 zoom-in 工具使用 | arXiv:2506.14821 |
| **Patch Zoomer / Localized Zoom** | 多篇 | 标准 ROI 裁剪+zoom 模式 | — |
| LLaVA-PruMerge / SparseVLM / PACT / ATP-LLaVA / IVTP / TopV / DivPrune / FastVLM | 2024–2025 | 各路 visual token 剪枝/合并/池化/重采样 | CVPR/ECCV/ICLR/NeurIPS 多篇 |

典型报数（SparseVLM）：减 54% FLOPs / 37% CUDA time、保持 97% 准确率。"裁切→省 token→保性能" 的实证已被反复验证。

#### 2.5.3 但在本工程语境下定位不同

不主张为 CV 创新，**写成 system-level efficiency evaluation**：作为 BCI pipeline 端到端部署成本的工程量化。在 NER / EMBC / BHI 这种 EEG/biomedical 场所，MLLM 效率话题的覆盖远不如 CVPR 饱和，复述此类对比的接受度更高。

#### 2.5.4 关键风险：Stage 1 准确率（50–60%）对 Stage 3 的传播效应

**用户 2026-05-12 提出的担心**：Stage 1 EEG 分类只有 50–60% top-1，若 Stage 1 错了，Stage 3 MLLM 就在问错问题（"What color is the [wrong class]?"），整套 pipeline 端到端 VQA acc 会被拖到 ~50% × VQA-given-correct-class，看起来很差。

**关键洞察：Stage 3 的两个评估维度对 Stage 1 的依赖完全不同**：

| 评估指标 | 是否依赖 Stage 1 |
|---|---|
| Token 数 / 延迟 / 成本 | ❌ 完全不依赖——不管类标对错，"ROI 裁切 vs 全图" 的输入大小、推理时间、API 计费都是确定的 |
| VQA 准确率 | ✅ 依赖——Stage 1 错 → 问错问题 → VQA 错 |

所以 Stage 3 的**效率主轴是 Stage-1-immune** 的，这部分数字不会被 EEG 准确率拖。问题只在 VQA accuracy 一项。

#### 2.5.5 解耦评估方案（处理 Stage 1 瓶颈）

报两套 VQA 数字，把"架构好不好"和"Stage 1 准不准"分开：

| 评估模式 | 类标来源 | 测的是什么 |
|---|---|---|
| **Oracle pipeline** | Ground truth 类标 | ROI vs 全图给 MLLM 的纯效率/质量差异；架构上界 |
| **End-to-end** | 真实 EEG → Stage 1 输出 | 当前真实 BCI 的 VQA 表现；现实部署数字 |

论文措辞示例：
> "We report VQA accuracy under two settings: (i) **oracle pipeline** with ground-truth class label, isolating the effect of ROI cropping vs whole-image input; (ii) **end-to-end** with EEG-decoded class, characterizing realistic deployment. The gap between (i) and (ii) quantifies the Stage-1 bottleneck and motivates future EEG decoding improvements."

这种双轨报告**反而把 Stage 1 瓶颈做成了一个可写的发现**——"架构是好的，瓶颈在 EEG，未来工作方向明确"——审稿人通常吃这套（"honest analysis" 加分）。

#### 2.5.6 缓解 Stage 1 误差的可选 ablation（详解）

这两个 ablation 是把 Stage 1 误差对下游传播降到最低的两条不同路径，可叠加，论文里挑 1–2 个做。

##### (a) Top-K 候选传递（top-K candidate passing）

**做法**：
- Stage 1 不只输出 top-1 类标，而是输出 softmax 概率最高的 K 个候选（如 K=3 或 5）
- Stage 2 OD **对这 K 个候选每个都跑一遍检测**（K 次 forward）
- 比较 K 个检测结果的最高置信度，**保留置信度最高那一支**作为最终类标 + 框

**为什么有用**：
- EEG top-1 可能 53%，但 top-5 通常远高（参考 CLIP 蒸馏 top-5 87%）——正确答案大概率在 top-K 里
- 视觉检测器扮演 K-选-1 的 "oracle"：错的候选在图里检不出高置信度框，对的能检出
- 等价于把 Stage 1 的不确定性外包给 Stage 2 的视觉证据来 disambiguate

**举例**：
用户看的是埃及猫。
- top-1 模式：EEG 输出 "波斯猫" → Stage 2 找波斯猫 → 找不到或乱框 → Stage 3 答错
- top-5 模式：EEG 输出 {埃及猫, 波斯猫, 豹猫, 虎, 山猫} → Stage 2 对 5 个都跑 → 只有 "埃及猫" 在图里检出高置信度框 → 选它 → Stage 3 答对

**代价**：Stage 2 推理量 ×K；如果错的候选恰好在图里有相似目标（如背景里有一只豹猫纹路的玩具）会被误判。

##### (b) EEG 置信度阈值 fall back 到全图

**做法**：
- Stage 1 输出不只是类标，还有 softmax 概率分布
- 取 top-1 概率作为置信度
- **高置信**（如 > 0.7）：信任 EEG → 走 Stage 2 + ROI 裁切 → 喂 MLLM（省 token）
- **低置信**（如 < 0.4）：不信 EEG → 跳过 Stage 2 / 不裁切 → **直接把全图喂 MLLM**，让 MLLM 自己理解整图回答 VQA

**为什么有用**：
- 高置信样本走 ROI 路径，省 token + 高准确率
- 低置信样本走全图路径，牺牲效率但避免错误传播——避免 "EEG 错了 → ROI 框错地方 → MLLM 答错" 的连锁反应
- 是个动态路由方案，效率与正确性的折衷

**代价**：需要选合适的阈值（用 val set 调）；低置信样本无效率收益；论文里要解释清楚阈值怎么选的。

##### (c) VQA 问题筛选（消极方案，**不推荐当主路径**）

只用对类别错误鲁棒的问题（如 "How many objects in the image?" / "What is the dominant color?"）。但会削弱 BCI 助手故事——明显是为避错而避错。仅适合做对照实验说明问题类型敏感性，不适合作为主结果。

#### 2.5.7 论文措辞建议

> "We add a Stage-3 MLLM-based VQA stage, where the Stage-2 detected ROI is cropped and fed to the MLLM. We do **not** claim a new MLLM efficiency method (the broader visual-token-reduction literature, e.g. V\*/SEAL, CROP, SparseVLM, has saturated this direction). Rather, we report a system-level efficiency characterization of the three-stage BCI VQA pipeline: input token count, end-to-end latency, and per-request cost are reduced by X% compared to whole-image input — these gains are independent of Stage-1 accuracy. We additionally report VQA accuracy under both oracle (ground-truth class) and end-to-end (EEG-decoded class) settings; the gap quantifies the Stage-1 bottleneck and motivates future EEG decoding improvements."

避免出现 "novel ROI-crop method"、"first to use crop for token reduction"、"propose visual-token-reduction approach for BCI" 这类措辞。

#### 2.5.8 实验设计（按 4 页篇幅，区分核心/选做）

**MLLM 用 1 个代表（如 GPT-4o）即可**，不必跨多个，避免实验项目膨胀。

##### 核心实验（必做）

1. **效率主轴（Stage 1 无关，铁数字）**：ROI crop vs 全图，MLLM 输入 token 数 / 端到端延迟 / 单次成本（USD/req）。一张表搞定。
2. **VQA 准确率双轨**：
   - (i) **Oracle**：GT 类标 → Stage 2 → ROI → MLLM。测纯 ROI vs 全图架构差异，是架构上界
   - (ii) **End-to-end**：真实 EEG → Stage 1 → Stage 2 → ROI → MLLM。测真实部署
   - 两轨 gap = Stage 1 瓶颈，主动写为 limitation + future work
3. **【新增】VQA 准确率随类别数缩放（用户 2026-05-12 提议）**：
   - 在随机子采样的 **10 / 20 / 30 / 40** 类上跑 end-to-end VQA 评估
   - 每个类数大小随机选 N 次类别（如 N=5）取平均 + 误差棒
   - 画 **VQA accuracy — number of classes** 折线图
   - 预期单调下降：类越少 → Stage 1 准确率越高 → 端到端 VQA 越好
   - 学术意义：(a) 量化"减少类数"对端到端表现的收益曲线；(b) 暗示在小类数 BCI 应用（如 yes/no、3–5 类指令）下 pipeline 已实用；(c) 给未来 EEG 改进的潜在收益空间画上界
   - 注意：每个 K 必须在**相同的 VQA 测试问题集**上评估，否则不可比
4. **按问题类型分类报告 VQA**：
   - **局部属性**（颜色 / 数量 / 材质 / 形状）：ROI 裁切应基本保持
   - **场景上下文**（室内外 / 相对位置 / 与其它物体关系）：ROI 裁切预期降幅，必须诚实报告
   - 一张分类表，是 honest reporting 必需

##### 选做（4 页放得下就加，否则挪 supplementary 或 future work）

- **OD 框误差敏感性**：故意 perturb 框（padding ±10/20%、移位）看 VQA 表现退化曲线
- **跨 MLLM 普适性**：≥ 2 个 MLLM（如 GPT-4o + Qwen-VL/Claude）
- **Top-K 候选传递 ablation**：K=1, 3, 5 对 end-to-end VQA 的影响（见 §2.5.6 (a)）
- **置信度阈值 fall back ablation**：阈值 0.4 / 0.5 / 0.7 等的扫描（见 §2.5.6 (b)）
- **与 V\*/SEAL 或 SparseVLM 对比**：在公开 benchmark 上小规模验证

##### 4 页篇幅预估

核心实验 1+2+3+4 大致占 1.5 页（含图表）；如果都做核心 + 1 个选做（如 OD 误差敏感性），约 2 页；剩余 2 页给方法、相关工作、限制和参考。


---

## 3. Stage 1 EEG 分类的准确率门槛（沿用前次核查）

### 3.1 必须避开的陷阱：块设计 (block design) 污染

#### 3.1.1 什么是块设计 vs 非块（rapid-event）设计

**块设计 (block design)**：按类别分块呈现刺激。例如要采集 40 类 × 50 张图的 EEG，整个实验流程是
"50 张猫 → 休息 → 50 张狗 → 休息 → 50 张飞机 → ……"
同一类的所有刺激连续出现在一个时间块里。这是 Spampinato 2017 的做法。

**非块 / rapid-event 设计 (event-related, randomized order)**：刺激按**随机顺序**呈现，相邻 trial 通常不同类。例如
"猫 → 飞机 → 狗 → 猫 → 钢琴 → 飞机 → ……"
THINGS-EEG2、Gifford 2022、CrossPT-EEG 都用这种。

#### 3.1.2 块设计为什么会污染分类结果

EEG 信号本身有强烈的**时间自相关**——相邻几秒钟内，被试的脑电状态（注意力、清醒度、肌电基线、电极接触阻抗、皮肤电、被试坐姿微动等）几乎不变。这些都是与"看到了什么"**无关**的低频漂移和噪声，但它们会在每个时间块内保持稳定、在不同块之间变化。

在块设计里，"同一时间块" 等价于 "同一类别"。所以一个分类器即使**完全不看视觉相关的脑信号**，只要能识别"现在是哪个时间块"就能猜对类别——它学的是"被试现在的清醒度 / 阻抗水平 / 心情"，不是"被试看到了什么"。

Li et al. 2018 的实证：把 Spampinato 的数据按时间随机重排（同一时间块内的 trial 重新分到不同类），分类准确率立刻崩到 chance 附近——证明 ~94% 完全是时间块标签泄露。

#### 3.1.3 怎么判断一个数字"被块污染"

- 整个数据集只有一次连续录制 + 按类别分块 → 高危
- 准确率 >90% on 40-class（远超信息论可信上界）→ 高危
- 没有报告 cross-block-time / cross-session 验证 → 不可信
- 用 rapid-event 设计 → 安全
- 同一类的刺激被打散到多个时间窗、且评测做了 cross-window 拆分 → 安全

#### 3.1.4 文献坐标

- Spampinato 2017 报 93.91% on 40-class、后续 ~97% —— **被 Li et al. 2018 (arXiv:1812.07697) 证伪**：模型学的是 trial 时间块的时序相关性，不是视觉内容。
- Palazzo 2020 (arXiv:2012.03849) 部分反驳但承认问题真实存在；正式批判见 NSF "Perils and Pitfalls of Block Design" (2020)。
- **任何 >90% on 40-class 都需怀疑块污染**（如 EEG2IM 报 99.95% on ImageNet-40）。

#### 3.1.5 EEG-ImageNet 2024 的实验范式（已读原文确认）

来源：EEG-ImageNet 论文 §3.4 + §4.3 + §6（PDF 在 `/mnt/e/wps/Projects/EEG_Obj_Detection/EEG-ImageNet.pdf`）。

**采集范式 = 块设计 + RSVP**：
- 每被试随机一个 seed 决定 80 个类别的呈现**顺序**
- 进入某个类别后，该类的 **50 张图按 RSVP 连续呈现**（每张 500 ms）
- 一个类别全部呈现完才进入下一个类别 → 同类 50 trial 连续聚成一个时间块

**他们的污染缓解（block-内时间切分）**（§4.3）：
> "all our experimental setups strictly adhere to a dataset split methodology where the **first 30 images of each category are used as the training set, and the last 20 images of each category are used as the test set**"

每个类别块内：早期 30 trial → train，晚期 20 trial → test。训练时 trial 打乱，但 train / test **仍在同一时间块内毗邻**，只是块内早晚不同段。

**作者自己承认未消除干净**（§6 Limitation）：
> "we were unable to eliminate it completely"

#### 3.1.6 对本工程 Stage 1 的硬要求

1. **必须沿用 EEG-ImageNet 的 block-内时间切分思路**（按 image index 切 train/val/test），不要随机打乱整体 train/test，否则数字与论文不可比，且污染会更严重。
2. **训练 trial 内部可以打乱** —— 这个用户已经做了，是对的。但要意识到 train/test 切分本身仍然是块内的，不是真正的 cross-block-time。
3. **论文写作时必须说明这一限制**：诚实交代 EEG-ImageNet 的块设计 + 块内时间切分缓解 + 残留污染，参照原论文的措辞。
4. **强烈建议附加一个 cross-subject 评测**（用其它被试的 trial 做 test）——能部分对冲块内时间污染，也是 CrossPT-EEG 2024 的 stress test 思路。

#### 3.1.7 本工程使用的 30/5/15 split 与 EEG-ImageNet 的 30/20 对比

本工程在 EEG-ImageNet 数据上采用 **30 train / 5 val / 15 test**（按每类 image index 切分），EEG-ImageNet 论文用 **30 train / 20 test**（无显式 val）。

| 维度 | EEG-ImageNet 30/20 | 本工程 30/5/15 |
|---|---|---|
| 显式 validation set（避免在 test 上选超参） | ❌ 没有 | ✅ 有 ← **方法论更严谨** |
| 块设计内时间切分（块污染根因） | within-block | within-block ← **同样未解决** |
| Test set 大小 | 20 张/类 | 15 张/类 ← 方差更大、单 seed 不稳 |

**你确实严谨的地方**：
- val 独立 → 超参/早停/模型选择不污染 test
- EEG-ImageNet 的 "best model X%" 实际上是在 test 上选出来的，存在轻度 test-set tuning。本工程避免了这一隐性泄露。

**你没改善的地方**：
- 块设计 + 块-内时间切分的**根本污染未动**——train/val/test 三段都来自同一类别块、同一连续录制段，时间上毗邻
- Li 2018 / Palazzo 2020 批判的"分类器学时间块内的清醒度/阻抗/姿势"问题，在 30/5/15 下与 30/20 下**严重程度相同**

**可能更差的地方**：
- Test 缩到 15 张/类 → **统计方差更大**。单被试 40 类 15 张测试集，分对/错 0.4 张 ≈ 1 个百分点。**论文必须报多次随机 seed 平均 + 标准差**，不能单次数字。

**论文里推荐的措辞（避免过度宣称）**：

> "We adopt a 30/5/15 train/val/test split per category, extending [EEG-ImageNet]'s 30/20 split with a held-out validation fold for hyperparameter selection and early stopping. Like [EEG-ImageNet], we acknowledge that the within-block temporal split does not eliminate the temporal contamination identified by [Li et al. 2018]; we therefore additionally report cross-subject results in §X as a stress test."

避免直接写"our split is stricter than EEG-ImageNet"——审稿人会立刻追问"那块污染你怎么处理的"，反而被动。

### 3.2 EEG-ImageNet 论文中报告的准确率（Table 2，所有被试平均；已读原文修正）

| 任务 | 类数 | 最佳模型 | Acc | 备注 |
|---|---|---|---|---|
| **all** | **80** | RGNN | **40.50%** | 全部 80 类 |
| **coarse** | **40** | MLP | **53.39%** | 40 个粗类 ← **本工程 Stage 1 直接对标** |
| fine | 40（**实为 5×8**） | MLP | 81.63% | **不是单个 40-way 任务**，是 5 组每组 8 类，组内分类后平均 |
| 单被试 best | 80 | — | 60.88% | 只是最强单被试，不可作为整体 SOTA |

**重要订正**：之前文档里说的「~60%」其实是单被试在 80 类任务上的最佳成绩，**不是 40 类平均水平**。真正与本工程可对标的数字是 **40-coarse ~53%**。

「fine 81%」也具误导性——它是把 40 类先分成 5 组（每组共享 WordNet 父节点，如所有乐器一组），然后每组做**组内 8 类分类**，再把 5 组准确率平均。这相对 40-way 是更容易的任务（chance = 12.5% vs 2.5%），不能拿来主张 "40-way 细粒度 81%"。

### 3.3 其它可比基线

| 工作 | 数据集 / 任务 | 准确率 | 备注 |
|---|---|---|---|
| 随机基线 | 40-way | 2.5% | 必须显著超过 |
| Palazzo 2020 | Spampinato 40-way（修复后） | ~50% | rapid-event |
| THINGS-EEG2 / NICE 2024 | 200-way zero-shot | top-1 15.6% / top-5 42.8% | rapid-event 严格设计 |
| CLIP 知识蒸馏 (2024) | 40-way | top-5 87% | 用 CLIP 教师 |

### 3.4 本工程门槛建议（按 EEG-ImageNet 公开切分对标，修正后）

假设本工程做 **40-coarse 任务**（与 EEG-ImageNet Table 2 第二列对比）：

| 门槛 | top-1 | 备注 |
|---|---|---|
| **下限**（显著超过 chance + 论文可发表） | ≥ 53% | 追平 EEG-ImageNet 2024 best (MLP) |
| **小幅超越 SOTA** | ≥ 56–58% | 比 MLP 高几个点，可写"improved over best baseline" |
| **明显超越 SOTA** | ≥ 62% | 比单被试 best (60.88%) 还要高，比较有说服力 |

如果做 **80-all 任务**：

| 门槛 | top-1 | 备注 |
|---|---|---|
| 下限 | ≥ 40.5% | 追平 RGNN |
| 小幅超越 | ≥ 43–45% | |
| 明显超越 | ≥ 50% | |

**额外硬要求**：
- 用 EEG-ImageNet 的官方 split（image index 1–30 train / 31–50 test），与论文 baseline 直接可比。
- 报告 top-1 / top-5 / per-class / chance 全套指标。
- **诚实标注块设计 + 块内时间切分**的局限性，在 limitations 一节中说明（参照 EEG-ImageNet §6 的措辞），不要假装是 rapid-event 干净评测。
- **强烈建议附加 cross-subject 评测**（用其它被试 trial 做 test，对冲块内时间污染，也呼应 CrossPT-EEG 2024 的 stress test 思路）。
- 不要拿 "fine 81%" 作为对标——那是 5×8 而不是 40-way。

> Stage 1 的准确率最终也制约 Stage 2 的 mAP 上界——若 Stage 1 top-1 = 60%，Stage 2 mAP 上界 ≈ 0.6 × （视觉 detector mAP）。建议 Stage 2 接受 **top-K 候选**而非 top-1，由视觉 detector 在 K 个候选类中挑置信度最高的，可大幅放宽对 Stage 1 的依赖。

---

## 4. Stage 2 OD 的对照实验要求

为让 Stage-2 的合成数据增强结论可信，必须做：

1. **等样本量对照**：「真实 N + 合成 M 训练」vs「真实 (N+M) 训练」（如真实够多）或「真实 N 训练」三组，证明提升来自合成数据带来的多样性而非样本量。
2. **数据泄露检查**：生成模型（CLIP / SD 等）的训练集与测试集真实图分布交叉，需检查生成图是否"记住"测试图（CLIP retrieval 相似度阈值过滤）。
3. **合成比例扫描**：M/(N+M) 在 0%/25%/50%/75% 处的曲线，证明存在最优比例。
4. **EEG 在 Stage 2 的真实贡献**：「人工类标 + 同 detector」mAP 是上界；「EEG 类标 + 同 detector」mAP 是实际。两者差距说明 Stage 1 误差对 Stage 2 的影响。
5. **与现有合成数据 OD 工作对标**：至少与 X-Paste / MosaicFusion / GeoDiffusion 中的一种在相同设定下对比，否则审稿人会问"为什么不用现成方法"。

---

## 5. 综合定位（最终，按 4 页会议论文目标）

会议论文（非顶会）对创新强度的要求远低于顶会，可以接受**一个方向性新意 + 一两个增量实证贡献**的组合。本工程足够支撑：

| 主张 | 顶会标准下 | 4 页会议论文里能否当贡献写 |
|---|---|---|
| 两阶段 EEG → 多目标场景定位 pipeline | ✅ 强 | ✅ **主推贡献**——任务设定本身在 EEG 文献中没人做过 |
| 配套数据集（细粒度 × 多目标） | ⚠ 工具性 | ✅ **可作为次要贡献写入**——明确说明是为支撑 Stage 2 而构造、衔接 EEG-ImageNet 的 40 个细粒度类目，并提供检测框元数据；不必硬包装成"first-of-its-kind" |
| Stage 1 EEG 分类（用 EEG-ImageNet） | 看模型 | ✅ 沿用 EEG-ImageNet，复现/对比即可，达到 §3.3 的门槛 |
| Stage 2 合成数据扩充 OD | ❌ 顶会上不算创新 | ✅ **可作为增量实证贡献**——"首次在 EEG-条件 OD + ImageNet 细粒度 synset + 多目标场景设定下评估合成数据扩充效果"，写法保守，配套对照实验 §4 |

**4 页论文里推荐的 contribution 列表（3 条）**：
1. We propose a two-stage EEG-conditioned object localization framework that extends EEG visual decoding from "what" (class) to "what + where" (class + bounding box in scene).
2. We construct a companion dataset bridging the 40-class EEG-ImageNet taxonomy with multi-object scene images and detection annotations, enabling stage-2 evaluation.
3. We empirically evaluate the use of LLM-generated images with human-annotated boxes as an augmentation source for stage-2 detector training, characterizing the real/synthetic mixing ratio under fine-grained synset and multi-object-scene conditions.

这三条**全部站得住**，不会过度包装、也不会被审稿人说"重新发明轮子"。

---

## 6. 下一步建议（按 4 页会议论文工作量）

1. **数据集人工质检**（细粒度类标 + 共存框金标子集），是 Stage 2 一切结果的前提。
2. **Stage 1**：复用 EEG-ImageNet 公开数据 + 官方块内 30/20 split。目标 top-1 ≥ 53%（追平 MLP）；冲 ≥ 56% 更稳。块设计局限性必须在 limitations 一节诚实交代。**不是论文成败关键**——论文主推 Stage 2 框架。
3. **Stage 2 输入接口**：建议接受 top-K 候选（K=3–5）而不是 top-1，让 Stage 1 的误差不至于卡死 Stage 2 上界。
4. **Stage 2 对照实验**：4 页论文里至少做 §4 的前 3 项（等样本量、合成比例扫描、EEG vs 人工类标的 mAP gap）；§4.5（与 X-Paste/MosaicFusion 对标）能做最好，做不动可在 related work 里引述说明而非实验对比。
5. **论文骨架**：主推两阶段 pipeline；数据集和合成数据扩充作为支撑性 contribution，**不在 abstract 里夸大**。
6. **避免的雷区**：
   - 不要在论文里出现 "first-of-its-kind dataset" / "novel real-photo filter" / "EEG-friendly metadata" 这类描述。
   - 不要引用 Spampinato 94% 作为基线，不出问题就不挑出来；引用必须配 Li 2018 警告。
   - 不要主张 "我们提出了用合成数据扩充 OD 的新方法"——必须明确说"沿用合成数据扩充范式 (X-Paste/GeoDiffusion 等)，在新设定下评估"。

---

## 参考

### Stage 1（EEG）
- Li et al. 2018, "Training on the test set? An analysis of Spampinato et al.": https://arxiv.org/abs/1812.07697
- Palazzo et al. 2020, "Correct block-design experiments mitigate temporal correlation bias in EEG classification": https://arxiv.org/abs/2012.03849
- "Perils and Pitfalls of Block Design for EEG Classification" (NSF/IEEE, 2020): https://par.nsf.gov/servlets/purl/10284053
- EEG-ImageNet (2024): https://arxiv.org/abs/2406.07151
- CrossPT-EEG benchmark (2024): https://arxiv.org/html/2406.07151v2
- NICE / Decoding Natural Images from EEG: https://arxiv.org/abs/2308.13234
- ATM / Visual Decoding via EEG Embeddings + Guided Diffusion (NeurIPS 2024): https://arxiv.org/abs/2403.07721
- THINGS-EEG2 (Gifford 2022): https://www.sciencedirect.com/science/article/pii/S1053811922008758

### Stage 2（OD 合成数据扩充）
- X-Paste (ICML 2023): https://github.com/bk11052/X-Paste-for-Object-Detection
- GeoDiffusion (ICLR 2024): https://arxiv.org/abs/2306.04607
- MosaicFusion (IJCV 2024): https://arxiv.org/html/2309.13042
- InstaGen (2024): https://arxiv.org/html/2402.05937v3
- DiffusionEngine (2024): https://www.sciencedirect.com/science/article/abs/pii/S0031320325008015
- AeroGen (CVPR 2025): https://openaccess.thecvf.com/content/CVPR2025/papers/Tang_AeroGen_Enhancing_Remote_Sensing_Object_Detection_with_Diffusion-Driven_Data_Generation_CVPR_2025_paper.pdf
- SOC – Synthetic Object Compositions (2025): https://arxiv.org/html/2510.09110
- Controllable Diffusion for OD Augmentation (WACV 2024): https://openaccess.thecvf.com/content/WACV2024/papers/Fang_Data_Augmentation_for_Object_Detection_via_Controllable_Diffusion_Models_WACV_2024_paper.pdf
- Beyond Objects (fine-grained synthetic, 2025): https://arxiv.org/html/2510.24078
- Synthetic data review (2025): https://link.springer.com/article/10.1007/s10462-025-11116-x
