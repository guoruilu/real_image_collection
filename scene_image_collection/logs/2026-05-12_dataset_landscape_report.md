# 2026-05-12 现有数据集综述报告

## 任务

调研公开目标检测/定位数据集，确认是否已存在能覆盖 `img_list.txt` 全部 40 类且满足本工程需求（细粒度 + 单图多目标共存 + 检测框元数据）的数据集，并把结论沉淀为子工程文档。

## 调研结论

公开数据集**不存在**同时满足「ImageNet 细粒度 synset」+「单图多目标共存」的组合：

- 细粒度 + 单主体：ImageNet-Loc / ImageNet BBox（覆盖 40/40，但单主体）
- 粗粒度 + 多目标：COCO / Open Images / Objects365 / LVIS（场景密集，但无 ImageNet 级品种细分）
- 细粒度 + 多目标：**空白**

EEG 视觉刺激相关数据集（Spampinato 2017 / THINGS-EEG2 / BOLD5000）也都不带「细粒度 + 共存物体检测框」的组合标注。

因此本工程 `scene_image_collection/` 的产物在公开领域属于 first-of-its-kind。

## 与已有自动产物的关系

`scene_image_collection/images/` 下的 41 个子目录已覆盖全部 40 类（含 `egyptian_mau_scenes/` + `egyptian_mau_cats/` 两轮重复采集，待合并去重）。**这些都是流水线自动产物，未经人工质检**：CLIP 真实性、YOLO-World 目标定位、共存扫描都可能误判，最终人工筛后留量预计远低于当前自动数字。本报告**不**用自动产物的张数判断「类别足够 / 不足」，所有平衡/扩采决策待人工质检后再定。

抓取来源是 Bing/Baidu 实时搜索，标注全部由本工程自动生成，不复用任何外部数据集的图或标注，与现有公开数据集无系统性重复。

## 新增/修改

- 新增 `docs/dataset_landscape.md`：现有数据集对照表（10+ OD 数据集 + 3 个 EEG 视觉刺激数据集）、关键差距分析、本数据集必要性、下一步建议。
- 更新 `README.md` 文档地图：加入 `dataset_landscape.md` 入口。
- 用户反馈：自动产物张数不可作为类别充足性判断依据，已写入报告与 Claude 长期记忆。

## 后续修订（同日，用户二轮 review）

用户挑战「真实性过滤 / EEG 友好元数据」是否真的算创新点。重新核查（抓取 Open Images V7 boxable CSV、LVIS 类目、ILSVRC DET 文档、Visual Genome 对齐策略、EEG-ImageNet 2024 / NOD MEG-EEG 2025）后确认：

- **唯一站得住脚的创新点是「ImageNet-1k 细粒度 synset × 单图多目标共存框」**。
- CLIP 真实性过滤、JSON 字段定制、过滤口径组合都不是学术创新；公开数据集的人工采集等价于真实性过滤。
- 共存框是 YOLO-World/COCO YOLOv8 自动生成、非 ground truth；细粒度类标也未经人工核验——这两点必须诚实交代为局限。

报告 §5 重写为「真正的创新点 + 不成立的伪创新点 + 必须交代的局限」三段，§6 结论也相应缩窄。新增 EEG-ImageNet / NOD / Open Images CSV / LVIS API 参考链接。

记忆同步更新：见 `feedback_real_novelty.md`。

## 产出位置

- 报告：`scene_image_collection/docs/dataset_landscape.md`
- 本日志：`scene_image_collection/logs/2026-05-12_dataset_landscape_report.md`
