# 2026-05-11 scene_image_collection 工程初始化

## 任务

新建一个采集流水线：给定 `img_list.txt` 中的目标类别，从互联网下载图片 → 过滤出真实拍摄的「大图」（包含目标 + 至少一个其它物体的场景图），保留**整张原图**和**JSON 元数据**，并提供画框可视化工具。

## 目录重组

原 `real_image_collection/` 顶层下的「小图采集」相关文件全部下沉到 `small_image_collection/` 子目录：
- `git mv collect.py run_all.py environment.yml requirements.txt docs logs → small_image_collection/`
- 未跟踪的 `images/`、`yolov8s-worldv2.pt`、`yolov8n.pt` 用普通 `mv` 移入
- 顶层保留 `CLAUDE.md`、`README.md`（改写为总览）、`img_list.txt`（两子工程共享）、`.gitignore`

## 新建文件

- `scene_image_collection/collect_scene.py` — 主流水线
- `scene_image_collection/draw_boxes.py` — JSON → 画框图可视化
- `scene_image_collection/run_all.py` — 30 类批量驱动（场景化 query + 通用 target）
- `scene_image_collection/README.md`
- `scene_image_collection/docs/usage.md`、`pipeline.md`、`tech_stack.md`
- `small_image_collection/README.md`（移植自旧顶层 README）

## 流水线设计要点

1. icrawler Bing+Baidu 下载（场景化关键词，`min_size=(600,600)`）
2. PIL 分辨率过滤（`--min-side` 默认 800）
3. CLIP-ViT-L/14 真实性过滤（real vs fake 多模板 softmax，阈值 0.55）
4. YOLO-World 单类目标定位
5. 目标占比过滤（`--target-max-ratio` 默认 0.5）
6. 共存物体检测：**双检测器并联** = YOLOv8s COCO + YOLO-World (LVIS_COMMON 110 词)
7. 框合并去重（IoU>0.5 greedy NMS），剔除与目标重叠（IoU>0.5）的框
8. 至少 1 个共存物体（`--co-conf-thresh` 默认 0.25）才保存
9. 输出：`<class>_NNN.jpg` + `<class>_NNN.json`（含 source_path/image_size/real_score/target/co_objects）

## 关键参数（默认值）

- `--n 80`：候选池大小（下载 n×6 张），最终输出**不限**
- `--min-side 800`、`--target-max-ratio 0.5`
- `--real-thresh 0.55`、`--co-conf-thresh 0.25`

## 验证

- `python -c "import collect_scene; import draw_boxes; import run_all"` 全部通过
- `python collect_scene.py --help` 输出正常，参数齐全
- `LVIS_COMMON` 110 词，`run_all.CONFIG` 30 类

## 产出位置

- 代码：`scene_image_collection/`
- 图像产出（待运行）：`scene_image_collection/images/<class>/`
- 可视化（待运行）：`scene_image_collection/images_annotated/<class>/`

## 单类试跑

`egyptian_mau_cats` --n 30：138 下载 → 121 过分辨率 → 94 过 CLIP → 23 张保存。画框可视化人眼核验：场景识别和共存物体识别按预期工作；偶有雕塑漏网（real=0.55 阈值的预期权衡），用户接受。

## 全 40 类批量结果

`run_all.py` 一次过，全部 ok 退出。`img_list.txt` 在批量前由用户扩充到 40 类（新增 10 类：德国牧羊犬/马/大熊猫/移动电话/咖啡杯/折叠椅/高尔夫球/山地自行车/香蕉/披萨）。

**总计 1963 张大图 + 1963 份 JSON 元数据**，分布如下（按 SUMMARY 表）：

| 类别 | 张数 | 类别 | 张数 |
|---|---|---|---|
| coffee_mugs | 157 | grand_pianos | 23 |
| mobile_phones | 130 | mailbags | 13 |
| horses | 120 | boletes | 13 |
| bananas | 108 | parachutes | 11 |
| pizzas | 89 | mittens | 10 |
| golf_balls | 85 | pool_tables | 7 |
| mountain_bikes | 83 | missiles | 6 |
| mountain_tents | 79 | revolvers | 3 |
| desktop_computers | 74 | brooms | 2 |
| folding_chairs | 74 | clothes_irons | 0 |
| giant_pandas | 66 | radio_telescopes | 0 |
| asian_elephants | 65 | (其它 18 类 30–60 张) | — |
| convertibles | 64 | | |
| running_shoes | 60 | | |
| pajamas | 51 | | |
| electric_trains | 51 | | |
| german_shepherds | 46 | | |
| digital_watches | 45 | | |
| reflex_cameras | 45 | | |
| espresso_machines | 44 | | |
| capuchin_monkeys | 42 | | |
| egyptian_mau_cats | 41 | | |
| jack_o_lanterns | 40 | | |
| lycaenid_butterflies | 38 | | |
| electric_guitars | 37 | | |
| clownfish | 36 | | |
| airliners | 34 | | |
| canoes | 31 | | |
| daisies | 17 | | |

## 低产/零产类的原因分析

- **clothes_irons (0)**：YOLO-World 对 "iron" prompt 召回极低，且场景里几乎没有其它可识别物体（多为白色熨衣板）。
- **radio_telescopes (0)**：射电望远镜远景图主体是天空/山地，几乎没有 COCO 或 LVIS 词表中的其它物体；近景图被目标占比过滤掉。
- **brooms (2) / missiles (6) / revolvers (3) / pool_tables (7) / mittens (10) / parachutes (11) / mailbags (13) / boletes (13) / daisies (17)**：这些类天然不与多物体共现，或目标占比常 >50%，是预期行为。

如后续需要补：
- 放宽 `--target-max-ratio` 到 0.7
- 降低 `--co-conf-thresh` 到 0.15
- 扩充 `LVIS_COMMON` 词表（如加 "ironing board" 给 clothes_irons、"sky" / "mountain" / "antenna" 给 radio_telescopes）

## 产出位置

- 图像 + JSON：`scene_image_collection/images/<class>/<class>_NNN.{jpg,json}`
- 完整运行日志：`scene_image_collection/logs/run_all_2026-05-11.log`

## 低产/零产类补救（remediate.py）

针对 11 个低产类做了第二轮采集，策略：
1. **扩展 LVIS_COMMON 词表**（110 → 137 词）：加入 ironing board / hanger / antenna / satellite dish / cue stick / billiard ball / scarf / envelope / letter / mailbox / log / leaf / moss / holster / launcher / military truck / mushroom 等。
2. **放宽阈值**：`--target-max-ratio 0.7`、`--co-conf-thresh 0.15`、`--real-thresh 0.5`、`--n 120`。
3. **场景化 query 显式提共存物体**：如 "broom and dustpan"、"missile on truck launcher"、"daisies in vase"、"mailman with letters at mailbox"。
4. `collect_scene.py` 增加 `--start-index` 参数，按现有文件数续编号，新结果合并到既有目录而非覆盖。

**结果（+delta）**：

| 类别 | before | after | +delta |
|---|---|---|---|
| daisies | 17 | 85 | **+68** |
| boletes | 13 | 39 | +26 |
| pool_tables | 7 | 31 | +24 |
| missiles | 6 | 28 | +22 |
| parachutes | 11 | 33 | +22 |
| mailbags | 13 | 28 | +15 |
| brooms | 2 | 9 | +7 |
| mittens | 10 | 16 | +6 |
| radio_telescopes | 0 | 4 | +4 |
| revolvers | 3 | 7 | +4 |
| clothes_irons | 0 | 0 | +0 |

11 类共 +198 张。`clothes_irons` 仍是 0，原因是 YOLO-World 对 "iron" prompt 的召回近乎为零；改 detect prompt 至 "clothes iron" 或换 OWL-ViT 可能能解，未在本轮处理。

**新总计**：2161 张大图 + 2161 份 JSON 元数据。完整日志：`logs/remediate_2026-05-11.log`。

## 资源消耗

- 显存峰值 ≈ 5 GB（RTX 4070 Laptop 8GB）
- 单类耗时 3–10 分钟（多数花在下载）
- 全 40 类总耗时约 4 小时
