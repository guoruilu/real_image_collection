# 使用指南

## 环境
- conda 环境 `eh`（torch 2.6 + CUDA 12.6，RTX 4070 Laptop 验证通过）
- 已装依赖：`ultralytics`、`icrawler`、`open_clip_torch`、`pi-heif`

## 激活
```bash
source ~/miniconda3/etc/profile.d/conda.sh && conda activate eh
cd ~/prjs/EEG_Obj_Detection
```

## 最小示例（COCO 内常见类，如猫/马/吉他）
```bash
python collect.py \
  --queries "acoustic guitar" "原声吉他" "wooden guitar" \
  --detect "guitar" \
  --out guitars \
  --n 50
```

## 带细类过滤（如品种、亚种）
```bash
python collect.py \
  --queries "giant panda" "大熊猫" "panda cub" \
  --detect "panda" \
  --out giant_pandas \
  --n 50 \
  --category-pos "giant panda" \
  --category-neg "red panda" "panda plush toy" "panda cartoon"
```

## 完整参数
| 参数 | 必填 | 说明 |
|---|---|---|
| `--queries` | ✓ | 搜索关键词列表，可中英混合 |
| `--detect` | ✓ | YOLO-World 检测词，**建议用通用类**（"cat","guitar","horse"），细类用 `--category-*` |
| `--out` | ✓ | 输出子目录名（最终路径为 `images/<out>/`） |
| `--n` | | 候选池**目标量**（用于估算下载数），默认 50。**最终输出不设上限**——所有通过过滤的图都会保存 |
| `--category-pos` | | CLIP 细类正样本 prompt 列表 |
| `--category-neg` | | CLIP 细类负样本 prompt 列表 |
| `--real-thresh` | | 真实性概率阈值，默认 0.7；噪声多的关键词可降至 0.55 |
| `--cat-thresh` | | 细类概率阈值，默认 0.5；细类边界模糊可降至 0.2~0.3 |
| `--yolo-world` | | YOLO-World 权重，默认 `yolov8s-worldv2.pt`；要更准可换 `yolov8l-worldv2.pt` |
| `--detect-fallback` | | 若 YOLO-World 找不到目标框，则保存整张图。适合小众/抽象类（如扫帚、熨斗、射电望远镜）——这些类的图通常是紧凑的产品/物品照，整张就是目标 |
| `--keep-raw` | | 调试用，不删 `_raw/` |

## 输出策略
**最终图片数量不设上限**：所有通过 CLIP 过滤 + YOLO-World 能定位到目标的图都会被保存，过滤出多少就存多少。`--n` 只用于估算候选池大小（默认下载 `n × 6` 张候选）。想要更多产出就加大 `--n` 和 `--queries`。

## 调阈值的经验
- 想多拿一点产出：增大 `--n`，加更多 `--queries`，再适当降 `--cat-thresh` / `--real-thresh`。
- **CLIP 通过的图很多，但最终保存数极少**（个位数）：YOLO-World 对该 detect prompt 召回弱，加 `--detect-fallback`；或换个更贴近物体几何形状的 detect 词（如射电望远镜用 "satellite dish"）。
- 产出有卡通/手办漏网：提高 `--real-thresh`（如 0.75）。
- 产出混了别的子类：补充 `--category-neg` 把易混项明确列出。
- `--detect` 不要写得太细（如 "egyptian mau cat"），YOLO-World 召回会跌——细类靠 CLIP，定位靠通用类。
