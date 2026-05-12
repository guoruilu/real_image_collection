# 2026-05-12 本工程 30/5/15 split 与 EEG-ImageNet 30/20 对比

## 任务

用户提示本工程使用 30 train / 5 val / 15 test（按每类 image index 切分），询问是否比 EEG-ImageNet 的 30/20 更严谨。

## 结论

**部分对，但不要在论文里夸大**。

| 维度 | EEG-ImageNet 30/20 | 本工程 30/5/15 |
|---|---|---|
| 显式 val（避免在 test 上选超参） | ❌ | ✅ 更严谨 |
| 块-内时间切分（块污染根因） | within-block | within-block，同样未解决 |
| Test set 大小 | 20 | 15，方差更大 |

- **更严谨的点**：独立 val 防止 test-set tuning。EEG-ImageNet Table 2 的"best model"很可能是在 test 上选出来的，本工程避免了这一隐性泄露。
- **没解决的点**：块设计 + 块-内时间切分这个根本污染未动；Li 2018 批判的污染在两种 split 下严重程度相同。
- **可能更差的点**：test 从 20 缩到 15，统计方差更大，必须多 seed 平均 + 标准差报告。

## 论文措辞建议

不要写"our split is stricter than EEG-ImageNet"——会被追问块污染。
推荐写法：
> "We adopt a 30/5/15 train/val/test split, extending [EEG-ImageNet]'s 30/20 with a held-out validation fold for hyperparameter selection. Like [EEG-ImageNet], we acknowledge that within-block temporal splits do not eliminate the temporal contamination identified by [Li 2018]; we additionally report cross-subject results as a stress test."

## 新增/修改

- 更新 `docs/research_plan.md` §3.1.7：新增本工程 30/5/15 与 EEG-ImageNet 30/20 对比表、各自优劣分析、推荐论文措辞。
