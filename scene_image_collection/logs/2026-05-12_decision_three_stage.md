# 2026-05-12 最终方案确定：三阶段 pipeline

## 决定

经过多轮讨论，最终方案确定为**三阶段 pipeline**（Stage 1 EEG → Stage 2 OD → Stage 3 MLLM VQA），第三 contribution 用 oracle vs end-to-end 的双轨评估处理 Stage 1 误差传播。

舍弃备选方案：
- **(A) 真实+LLM 生成训练 → OD 提升**：CV 圈饱和，与 EEG 故事弱，工作量大。
- **(C) 只做 pipeline + 数据集**：4 页填得过薄。

最终 3 条 contribution：
1. Three-stage EEG-conditioned BCI VQA pipeline (what → what + where + answer)
2. Companion dataset (EEG-ImageNet 40 类 × 多目标场景 + 框)
3. System-level efficiency evaluation of Stage-3 ROI-to-MLLM-VQA + decoupled VQA accuracy (oracle vs end-to-end)

## 修改

- `docs/research_plan.md`（速览）：完全重写
  - "两阶段定位" → "三阶段 pipeline"，含 Stage 3 行
  - "唯一强创新点" → 三阶段 pipeline
  - 删除"候选第三 contribution 二选一/三选一"全部内容
  - "推荐 contribution 列表" → 固定 3 条（不再二选一）
  - "Stage 2 必做对照实验" → "Stage 3 必做对照实验"，含双轨评估强制要求
  - "下一步" 第 4 条改为 Stage 3 工作
  - "关键参考" Stage 2 部分换成 Stage 3 (V*/SEAL/CROP/TEVA/SparseVLM/Multi-Agent VQA)
  - 论文雷区：删除 "提出合成数据 OD 新方法" 一条
- `docs/research_plan_details.md`：
  - §1 → 三阶段表，新增 §1.1 历史记录已舍弃备选方案
  - §2.3 → 大幅缩减 Stage 2，移除 (A) 详尽对比表，把整个 OD 增强部分压成一句"已舍弃见 §1.1"
  - §2.4 核心强创新点 → 三阶段
  - §2.5 标题 "候选第三 contribution" → "第三 contribution（已确定）"
  - §2.5.4 "与候选 (A) 对比" → 删除，直接进入 Stage 1 误差传播分析
  - §2.5 内子节重新编号 §2.5.1–§2.5.8（去掉了 (A) 对比、综合判断段落）
- 长期记忆 `project_research_plan.md`：
  - 更新 contribution 列表为固定 3 条 + 显式列出已舍弃方案
  - landmines 列表去掉 "synthetic-data OD" 一条，新增 "Stage-3 VQA 必须双轨评估" 一条

## 备注

候选投稿会议清单（NER / EMBC / ICASSP / BHI / ISBI / ICIP / BIBM 短文）不变，4 页约束依然有效。
