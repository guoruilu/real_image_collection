# 2026-05-12 Stage 1 准确率对候选 (B) 的传播效应分析

## 任务

用户提出：Stage 1 EEG 分类只有 50–60%，会对下游 Stage 3 (MLLM VQA) 形成误导，且短期内难以显著提高 EEG 准确率。重新评估候选 (B) 是否还值得做，并给出处理方案。

## 关键洞察

(B) 的两个评估维度对 Stage 1 的依赖完全不同：

| 评估指标 | 是否依赖 Stage 1 准确率 |
|---|---|
| Token 数 / 延迟 / 成本 | ❌ 完全不依赖（裁切大小、推理时间、API 计费与类标对错无关） |
| VQA 准确率 | ✅ 依赖（错类标 → 问错问题 → VQA 错） |

所以效率主轴是 Stage-1-immune 的，铁数字。问题只在 VQA acc 一项。

## 处理方案：解耦评估（decoupled evaluation）

报两套 VQA 数字：
- **Oracle pipeline**：GT 类标，测纯架构效果（ROI vs 全图）
- **End-to-end**：真实 EEG → Stage 1，测真实部署数字
- 两套差距 = Stage 1 瓶颈，主动量化为 limitation + future work

这种双轨报告把 Stage 1 瓶颈做成可写的发现，审稿人通常加分。

## 缓解 Stage 1 误差的可选 ablation

1. Top-K 候选传递（top-5 比 top-1 高很多）
2. EEG 置信度阈值 fall back 到全图
3. VQA 问题筛选（仅用对类别错误鲁棒的问题，但削弱 BCI 故事，慎用）

## 三个候选的最终对比

| 候选 | Stage 1 影响 | 工作量 | 与 pipeline 耦合 |
|---|---|---|---|
| (A) 合成数据扩 OD | ❌ 完全免疫 | 大 | 弱 |
| (B) ROI → MLLM VQA | 部分（已可解耦） | 小 | 强 |
| (C) 只做 pipeline + 数据集 | — | 0 | — |

## 决策建议

- 时间够：选 (B) + 双轨评估
- 时间紧或不愿处理双轨：(A)（更稳但工作量大）或 (C)（只做 2 个贡献）

## 新增/修改

- `docs/research_plan.md`：候选第三 contribution 表加入 "(C) 不做" 选项 + Stage 1 依赖性列；contribution list 改为三选一；Stage-2 对照实验段落 (B) 改为强制双轨报告 + 可选 ablation
- `docs/research_plan_details.md`：§2.5 新增 §2.5.5–2.5.9（Stage 1 风险、解耦方案、缓解 ablation、综合判断、修订措辞），原 §2.5.5–2.5.6 重编号
