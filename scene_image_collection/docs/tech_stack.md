# 技术路线（scene_image_collection）

## 总体思路

「场景大图」=「真实拍摄 ∧ 分辨率达标 ∧ 包含目标 ∧ 目标占比适中 ∧ 包含其它物体」。这五个条件无法用一个模型一步到位，所以采取**多阶段过滤** + **多检测器并联**。

## 角色分工

| 阶段 | 模型 | 角色 |
|---|---|---|
| 1. 来源 | icrawler (Bing + Baidu) | 中英混合场景化关键词，从两个搜索引擎拉候选 |
| 2. 分辨率 | PIL | 廉价快速筛选大图 |
| 3. 真实性 | CLIP-ViT-L/14 (open_clip, openai 权重) | 零样本图文相似度，把「real photo」类模板和「cartoon/drawing/3D render/...」类模板做对比 softmax |
| 4. 目标定位 | YOLO-World v2-s (ultralytics) | 开放词表检测，单类，用通用词（"cat"/"car"）召回稳 |
| 5. 共存检测 A | YOLOv8s COCO (ultralytics) | 80 类常见物体，速度快、准确 |
| 5. 共存检测 B | YOLO-World v2-s (相同权重，第二实例) | 用 LVIS 风格 ~100 词扩展词表，补 COCO 没有的物体（沙发、枕头、电视等已在 COCO；床、毛巾、灯具、植物盆等需要扩展） |

## 替代方案对比

| 方案 | 优点 | 缺点 | 是否采用 |
|---|---|---|---|
| Grounding DINO 替代 YOLO-World | 召回更全 | 推理慢、显存大 | 否，YOLO-World 速度优先 |
| Detic（LVIS 1200 类） | 类目最全 | 部署麻烦，模型大 | 否，用 YOLO-World 给 prompt 列表近似 |
| 单个 OWL-ViT v2 同时做目标和共存 | 一次推理 | 速度慢，对大词表延迟显著 | 否 |
| 把目标和 LVIS 词表合到一次 YOLO-World 推理 | 省一遍前向 | 单次太多类的话会降召回 | **可后续优化** |

## LVIS 词表

`collect_scene.py:LVIS_COMMON` 嵌入了约 100 个常见物体词，覆盖：
- 人体（person/man/woman/child）
- 家具（chair/sofa/bed/table/desk/...）
- 厨房（cup/bottle/microwave/refrigerator/...）
- 家电（tv/laptop/phone/camera/...）
- 衣物配饰（backpack/hat/shoes/...）
- 交通（car/truck/bus/bicycle/...）
- 自然（tree/plant/grass/rock/...）
- 动物（dog/cat/bird/...）
- 室内结构（wall/door/window/...）

词表保守，可在 `collect_scene.py` 顶部直接修改。

## 显存调度

CLIP 用完即释放（`del clip_model; torch.cuda.empty_cache()`），之后三个 YOLO 实例同时在显存。在 RTX 4070 Laptop 8GB 上实测峰值约 5 GB。

如果显存吃紧，可以把两个 YOLO-World 实例合并为一个（每张图前 `set_classes(...)` 切换），代价是每张图多一次 set_classes 调用。
