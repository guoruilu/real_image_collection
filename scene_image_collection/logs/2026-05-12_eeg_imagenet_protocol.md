# 2026-05-12 EEG-ImageNet 协议确认与门槛订正

## 任务

用户提示 EEG-ImageNet 同样是块设计但训练时打乱，让我读原论文（`/mnt/e/wps/Projects/EEG_Obj_Detection/EEG-ImageNet.pdf`）确认范式与准确率门槛。

## 读原文确认（§3.4 / §4.3 / §5.1 Table 2 / §6）

**采集范式**：块设计 + RSVP
- 每被试随机一个 seed 决定 80 个类别的呈现顺序
- 进入某类后，该类 50 张图按 RSVP 连续呈现（500 ms/张）
- 一类全部呈现完才进入下一类 → 同类 50 trial 连续聚成时间块

**train/test split**（§4.3）：块-内时间切分
- 每个类别块内：image index 1–30 → train，31–50 → test
- 训练 trial 内部打乱（用户做的对的）
- 但 train/test 仍同处一个时间块内、毗邻

**作者承认**（§6 Limitation）：
> "we were unable to eliminate it completely"

## 准确率（Table 2，所有被试平均）

| 任务 | 类数 | 最佳模型 | Acc |
|---|---|---|---|
| all | 80 | RGNN | 40.50% |
| **coarse** | **40** | **MLP** | **53.39%** ← 本工程 Stage 1 直接对标 |
| fine | 40（实为 5×8） | MLP | 81.63% |
| 单被试 best (80-all) | — | — | 60.88% |

## 关键订正

之前文档把「~60%」当作 EEG-ImageNet 40-class SOTA → **错误**。
- 60.88% 是单被试在 80 类任务上的最佳成绩
- 81.63% 是 5 个 8 类任务的平均（chance=12.5%），不是真正 40-way
- **真正的 40-coarse 平均 SOTA = ~53%**

之前的门槛建议（≥50/60/65）也据此修正：

| 任务 | 下限 | 小幅超越 | 明显超越 |
|---|---|---|---|
| 40-coarse | ≥ 53% | ≥ 56–58% | ≥ 62% |
| 80-all | ≥ 40.5% | ≥ 43–45% | ≥ 50% |

## 新增/修改

- 更新 `docs/research_plan.md` §3.1.5 → §3.1.6（EEG-ImageNet 实测范式 + 对本工程的硬要求），新增 §3.2 EEG-ImageNet 实际数字表（含「fine 81% 是 5×8 不是 40-way」澄清），重写 §3.4 门槛建议（按 40-coarse / 80-all 分别给）。
- 更新 §6 下一步建议中 Stage 1 目标准确率为 ≥53%（不再是 ≥50%/60%）。
- 长期记忆 `project_research_plan.md` 待同步。
