# 2026-05-12 研究计划创新性核查（多轮修订）

## 任务

用户给出完整研究计划，要求核查三件事：
1. 「真实数据 + LLM 生成数据训练，真实数据测试」这一思路是否已有先例？创新性多强？
2. 阶段二「EEG 分类 → 在多目标场景图中框出对应类别」是否已有先例？
3. 当前 EEG 分类被试所看类别的准确率 SOTA 是多少？本工程要到多高才能站得住脚？

## 用户后续澄清

- **Stage 1（EEG 分类）**：用 **EEG-ImageNet 公开数据集**（不是我们采集的）。准确率门槛属于这一阶段。
- **Stage 2（OD）**：用我们的多目标场景数据集，本质是普通 OD 任务，EEG 只提供类别 prior。「真实+生成」训练范式属于这一阶段，与 EEG 无直接关系。
- **数据集**不是强创新，是为支撑 Stage 2 而构造的配套数据集。
- **目标会议**：约 4 页普通计算机或生理信号会议（**非顶会**）。

## 核查方式

并行多次 WebSearch：
- Stage 1：EEG-ImageNet, THINGS-EEG2, NICE, ATM, CrossPT-EEG, Spampinato 块设计争议（Li 2018, Palazzo 2020, NSF Perils paper）。
- Stage 2：X-Paste (ICML 2023), GeoDiffusion (ICLR 2024), MosaicFusion (IJCV 2024), InstaGen, DiffusionEngine, AeroGen (CVPR 2025), SOC, Controllable Diffusion (WACV 2024), Beyond Objects 等 2023–2025 OD 合成数据扩充工作。

## 结论

| 主张 | 强度 | 4 页会议论文里能否当贡献 |
|---|---|---|
| **两阶段 EEG → 多目标场景定位 pipeline** | ✅ 强 | ✅ 主推贡献（公开 EEG 文献未见） |
| **配套数据集**（细粒度 × 多目标） | ⚠ 工具性 | ✅ 次要贡献（明确为 Stage 2 服务，不包装成"first-of-its-kind"） |
| **Stage 1 EEG 分类**（用 EEG-ImageNet） | 看模型 | 沿用复现，达 §3.3 门槛（top-1 ≥ 50% 下限，60% 同行接受） |
| **Stage 2 合成数据扩充 OD** | ❌ 顶会上不算创新（X-Paste/GeoDiffusion/MosaicFusion 等已密集发表） | ✅ 增量实证贡献（"在 EEG-条件 OD + 细粒度 synset + 多目标场景设定下评估"） |

## 关键提醒

- Stage 1 必须避开 Spampinato 块设计陷阱（Li 2018 证伪 ~94%）；用 rapid-event 设计或 cross-block-time 拆分。
- Stage 1 准确率制约 Stage 2 mAP 上界；建议 Stage 2 接受 top-K 候选而非 top-1。
- Stage 2 对照实验：等样本量、合成比例扫描、EEG vs 人工类标 mAP gap（必做前三项）；与现成 OD 合成数据方法对标（能做最好）。
- 论文里不能出现「first-of-its-kind dataset」「novel real-photo filter」「EEG-friendly metadata」这类描述；不能引 Spampinato 94% 当基线；不能宣称"提出合成数据 OD 新方法"。

## 新增/修改

- 新增 `docs/research_plan.md`：完整核查报告（按用户多轮澄清重写：两阶段定位、各阶段创新核查、Stage-1 准确率门槛、Stage-2 OD 合成数据扩充现状对照表、4 页会议论文级 contribution 列表与雷区清单）。
- 更新 `README.md` 文档地图：加入 `research_plan.md` 入口。
- 长期记忆同步：见 `project_research_plan.md`、`feedback_real_novelty.md` 已更新。
