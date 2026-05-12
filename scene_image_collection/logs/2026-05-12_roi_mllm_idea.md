# 2026-05-12 候选第三 contribution：ROI crop → MLLM (VQA)

## 任务

用户提议把原 Stage-2 augmentation 实验换成"ROI crop 给 MLLM vs 全图，比 token/latency 节省"，下游任务=VQA。要求严格核查现状。

## 核查方式

并行 4 次 WebSearch：ROI crop / VLM token efficiency / V*-SEAL / tool-augmented MLLM call detector + crop。

## 核查结论

**作为 CV/MLLM 创新点不新**——2024–2025 是密集发表方向：

- V\*/SEAL (CVPR 2024)、CROP (2025)、TEVA (ICCV 2025)、MLLMs Know Where to Look (ICLR 2025)、Visual Perception Token (2025)、AwaRes/ViCrop (2025)、Multi-Agent VQA (2024)、Reinforcing VLMs to Use Tools (2025)、Patch Zoomer/Localized Zoom 等
- 通用 visual-token reduction：LLaVA-PruMerge、SparseVLM、PACT、ATP-LLaVA、IVTP、TopV、DivPrune、FastVLM 等
- 典型报数：SparseVLM 减 54% FLOPs / 37% CUDA time，准确率保持 97%

**但放到本工程的 BCI VQA pipeline 里定位不同**：
- 不主张 CV/MLLM 算法创新，写成 system-level efficiency evaluation
- 故事推到 end-to-end "EEG → 定位 → MLLM 回答 VQA"
- 在 NER/EMBC/BHI 等 EEG/biomedical 场所，MLLM 效率话题覆盖远不如 CVPR 饱和，复述基础对比的接受度更高

## 与原候选 (A) 合成数据扩 OD 的对比

| 维度 | (A) 合成数据扩 OD | (B) ROI vs 全图 → MLLM VQA |
|---|---|---|
| CV 创新性 | 0（饱和） | 0（饱和） |
| 与 pipeline 耦合 | 弱 | 强（自然成 Stage 3） |
| 工作量 | 大（训 detector + 多组对照） | 小（调 API 跑两组） |
| 评估指标 | mAP | tokens / latency / $ / VQA acc |
| 端到端故事 | 解耦的训练增强 | BCI VQA 助手完整闭环 |
| 雷区 | 与 EEG 脱节 | OD 框误差传播到 VQA |

**推荐 (B)**——工作量更小、故事更顺。

## (B) 必做对照实验

1. ROI vs 全图：token 数 / 延迟 / $/req
2. VQA 准确率：分**局部属性**（颜色/数量/材质）vs **场景上下文**（室内外/相对位置）两类报告——后者裁切预期降幅
3. OD 框误差敏感性：padding ±10/20%、移位
4. 跨 MLLM 普适性：≥ 2 个 MLLM（GPT-4o / Qwen-VL / Claude）
5. 加分：与 V\*/SEAL 或 SparseVLM 在公开 benchmark 对比

## VQA 数据来源（待用户决定）

- 现成 VQA 数据集子集（VQAv2/GQA/A-OKVQA/ScienceQA）筛选含 Stage-2 类别的问题
- LLM 在 `scene_image_collection/` 图上自动生成围绕 Stage-2 类的 QA 对，小规模人工核验
- 模板化问题（"What color is the [class]?"）

## 论文措辞要点

- 写成 "system-level efficiency characterization of the BCI VQA pipeline"
- 明确不主张 "novel ROI-crop method" / "first to use crop for token reduction"

## 新增/修改

- `docs/research_plan.md`（速览版）：唯一强创新点段落新增"候选第三 contribution 二选一"；对照实验段拆为 (A)/(B)；contribution 列表第 3 条写成二选一；雷区新增禁止宣称 ROI-crop 算法贡献。VQA 已显式标注。
- `docs/research_plan_details.md`：新增 §2.5「候选第三 contribution: ROI crop → MLLM (VQA)」，含想法、CV 圈现状对照表、与 (A) 对比、必做对照、VQA 数据来源建议、论文措辞。
- 长期记忆 `project_research_plan.md` 待补充。
