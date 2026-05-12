# 研究计划：关键点速览

> 报告日期：2026-05-12  ·  目标：约 4 页 CV 或生理信号会议（非顶会）
> 详细论证、原文核查、对照表请看 [`research_plan_details.md`](research_plan_details.md)

## 三阶段 pipeline

| 阶段 | 数据 | 任务 | 与 EEG 关系 |
|---|---|---|---|
| **Stage 1** | EEG-ImageNet 2024（**公开**，非自采） | EEG → 40 类标签 | 核心 EEG 任务 |
| **Stage 2** | 本工程 `scene_image_collection/` | 场景图 + Stage-1 类标 → bbox | EEG 仅提供 class prior |
| **Stage 3** | bbox 裁出 ROI + VQA 问题 | ROI → MLLM → 答案 | 与 EEG 无关；下游任务 = VQA |

整体故事：**EEG 知道用户看什么 → OD 定位它在场景中的位置 → MLLM 基于 ROI 回答 VQA 问题** = end-to-end BCI VQA 助手。

## 唯一强创新点

**三阶段 EEG-conditioned BCI VQA pipeline**（公开 EEG 文献未见）。其它都是工具性/增量：
- 数据集 = 配套贡献，不主张 "first-of-its-kind"
- Stage 3 ROI vs 全图的效率对比 = 不算 CV 创新（V\*/SEAL/CROP/TEVA/SparseVLM 已饱和），写成 "system-level efficiency evaluation"

## Contribution 列表（3 条）

1. **Three-stage EEG-conditioned BCI VQA pipeline**: extends EEG decoding from "what" (class) to "what + where + answer" (class + bounding box + VQA answer).
2. **Companion dataset** bridging EEG-ImageNet's 40 classes with multi-object scene images and detection annotations.
3. **System-level efficiency evaluation of Stage-3 ROI-to-MLLM**: token / latency / cost reduction vs whole-image input, with **decoupled VQA accuracy reporting** (oracle GT class vs end-to-end EEG) to quantify the Stage-1 bottleneck.

## Stage 3 实验设计（按 4 页篇幅，区分核心/选做）

下游任务 = VQA。**必须解耦评估**——把"架构好不好"和"Stage 1 准不准"分开报告。MLLM 用 1 个代表（如 GPT-4o）即可。

### 核心实验（必做）

1. **效率主轴（Stage 1 无关，铁数字）**：ROI 裁切 vs 全图，MLLM 输入 token 数 / 推理延迟 / 单次成本（USD/req）。一张表搞定
2. **VQA 准确率双轨**：
   - (i) **Oracle**：GT 类标 → Stage 2 → ROI → MLLM 测纯架构 ROI vs 全图差距
   - (ii) **End-to-end**：真实 EEG → Stage 1 → Stage 2 → ROI → MLLM 测真实部署数字
   - 两轨 gap = Stage 1 瓶颈，主动量化 → 写为 limitation + future work
3. **【新增】VQA 准确率随类别数缩放**：在随机子采样的 **10 / 20 / 30 / 40** 类上跑 end-to-end 评估，每个类数随机选 N 次（如 5 次）类别取平均 + 误差棒，画 **VQA acc — 类数** 折线图。预期单调下降；说明 pipeline 在小类数场景下更可用，量化"减少类数"对端到端表现的收益（激励未来减类的 BCI 应用场景设计）
4. **按问题类型分类报告 VQA**：**局部属性**（颜色/数量/材质，ROI 应保持）vs **场景上下文**（室内外/相对位置，ROI 预期降幅）—— 一张分类表

### 选做（4 页放得下就加，否则挪 supplementary / future work）

- OD 框误差对 VQA 的影响：padding ±10/20%、移位
- 跨 MLLM 普适性（≥ 2 个 MLLM）
- Top-K / 置信度 fall back ablation（见下"概念解释"）
- 与 V\*/SEAL 或 SparseVLM 在公开 benchmark 对比

### 概念解释（Stage 1 误差缓解 ablation 是什么意思）

**Top-K 候选传递**：Stage 1 不只输出 top-1 类标，而是 top-K（如 K=5）。Stage 2 OD **对每个候选都跑一遍检测**，保留检测置信度最高者。利用 **EEG top-5 acc 远高于 top-1** 的事实，让视觉检测器做 K-选-1 的 disambiguation。例：top-5 = {埃及猫, 波斯猫, 豹猫, 虎, 山猫} → 只有埃及猫能在图中检出高置信度框 → 选它。

**EEG 置信度阈值 fall back 到全图**：Stage 1 输出 softmax 概率分布；高置信（如 > 0.7）走 ROI 模式（信任 EEG，省 token），低置信（如 < 0.4）直接喂全图（不信 EEG，让 MLLM 自己理解整图）。低置信样本不会把错误传播到下游，代价是这些样本无效率收益。

## Stage 1 准确率门槛（对标 EEG-ImageNet Table 2 平均值）

| 任务 | EEG-ImageNet SOTA | 下限 | 小幅超越 | 明显超越 |
|---|---|---|---|---|
| **40-coarse** | 53.39%（MLP） | ≥ 53% | ≥ 56–58% | ≥ 62% |
| 80-all | 40.50%（RGNN） | ≥ 40.5% | ≥ 43–45% | ≥ 50% |

⚠ EEG-ImageNet 的 "fine 81%" 是 5×8 不是 40-way，**不能拿来对标**。

> Stage 1 50–60% 对 Stage 3 的传播：效率指标完全不影响（裁切大小/推理时间/计费与类标对错无关）；VQA 准确率端到端会被拖累，靠双轨报告化解。

## split 现状

- EEG-ImageNet：30 train / 20 test（无 val），有隐性 test-set tuning
- 本工程：30 train / 5 val / 15 test ← val 独立更干净，但**块污染没解决**，test 缩到 15 方差更大需多 seed 平均
- 写论文时只说 "extends with held-out validation"，**不要写 "stricter"**

## Stage 1 块污染（核心局限）

EEG-ImageNet 是块设计 + RSVP（同类 50 张连续呈现），train/val/test 都在同一时间块内。Li 2018 批判的污染未消除，作者自己承认。本工程也未解决。**必须在 limitations 中诚实交代**，并附 cross-subject 评测作为 stress test。

## 论文雷区

- ❌ "first-of-its-kind dataset" / "novel real-photo filter" / "EEG-friendly metadata"
- ❌ 引 Spampinato 94% 当基线（必须配 Li 2018 警告）
- ❌ 宣称 "提出 ROI-crop MLLM 加速新方法"（V\*/SEAL/CROP/TEVA 等已饱和，必须说 "system-level efficiency evaluation"，不主张算法贡献）
- ❌ 写 "our split is stricter than EEG-ImageNet"（招攻击）
- ❌ 拿 fine 81% 当 40-way SOTA

## 下一步

1. 数据集人工质检（细粒度类标 + 共存框金标子集）—— Stage 2/3 一切结果的前提
2. Stage 1 跑通，目标 40-coarse top-1 ≥ 53%
3. Stage 3：定 VQA 数据来源（现成 VQA 子集 / LLM 自动生成 / 模板化问题），定 1 个 MLLM（如 GPT-4o），跑核心实验 1–4（效率主轴 / VQA 双轨 / VQA-acc-vs-类数 / 按问题类型分类）
4. 选做酌情：OD 框误差敏感性 / Top-K / 置信度 fall back（4 页放得下就加）

## 关键参考

- **Stage 1**: EEG-ImageNet 2024 (arXiv:2406.07151)、Li 2018 (arXiv:1812.07697)、Palazzo 2020 (arXiv:2012.03849)
- **Stage 3**: V\*/SEAL (CVPR 2024)、CROP (2025)、TEVA (ICCV 2025)、SparseVLM、Multi-Agent VQA (2024)

完整参考列表见 [`research_plan_details.md`](research_plan_details.md) §参考。

---

## 候选投稿会议（按"4 页论文格式"筛选，已上网核实页数限制）

> 不限定截稿时间窗口，按论文页数硬约束筛选。CV/ML 主流（WACV / AAAI / BMVC / ACM MM / ICDM / ICPR / SMC）均为 6–14 页，**不符合 4 页目标**，已排除。

### 4 页（含参考）格式可用

| 会议 | 页数 | 与本工程契合度 | 官网 |
|---|---|---|---|
| **IEEE NER**（Neural Engineering） | **4 页含参考**（或 6 页全文） | ✅✅✅ EEG/BCI 最对口，整套 pipeline 正面可写 | https://ieee-ner.org/ |
| **IEEE EMBC** | **4–7 页**（4 页起步） | ✅✅ 广泛 biomedical engineering，EEG 大量发表 | https://embc.embs.org/ |
| **IEEE ICASSP** | **4 页技术 + 1 页仅参考** | ✅✅ Signal processing 顶 tier-2，但 4 页紧；OJSP-ICASSP 走 8+1 页另算 | https://2026.ieeeicassp.org/paper-submission-instructions/ |
| **IEEE BHI**（Biomedical Health Informatics） | **4–7 页** | ✅ Health informatics 视角下整套 pipeline 可投 | https://bhi.embs.org/ |
| **IEEE ISBI** | **4 页 + 1 页仅非技术** | ⚠ 偏医学影像（CT/MR/病理），EEG 非主流 | https://biomedicalimaging.org/ |
| **IEEE ICIP** | **5 页技术 + 1 页仅参考** | ⚠ 5 页非严格 4 页；OD 部分契合，EEG 部分不太相关 | https://2026.ieeeicip.org/ |
| **IEEE BIBM 短文/扩展摘要** | **2–4 页** | ⚠ 偏 bioinformatics（基因/蛋白），EEG 是 minority | https://ieeebibm.org/ |

### 推荐排序（按 4 页 + 契合度）

1. **IEEE NER** —— 4 页且 EEG/BCI 主战场，整套 pipeline 正面叙述
2. **IEEE EMBC** —— 4 页起步，biomedical engineering 范围广
3. **IEEE ICASSP** —— signal processing 顶 tier-2，4+1 页较紧需取舍
4. **IEEE BHI** —— health informatics 视角后备
5. **ICIP / ISBI / BIBM 短文** —— 进一步后备

> 各会议年份与截稿日期会变化，定下首选后再去对应年度官网核对该年具体 deadline。
