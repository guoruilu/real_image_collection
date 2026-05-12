# 模型下载与缓存

三个权重都由代码**首次运行时自动下载**，无需手动操作。下表说明位置和占用，方便你换机器、清缓存、做离线打包。

## 权重清单

| 模型 | 触发下载的代码 | 下载到 | 大小 | 来源 |
|---|---|---|---|---|
| YOLOv8n（v1 遗留，可删） | `YOLO("yolov8n.pt")` | **当前工作目录**，即运行 `collect.py` 时所在路径 | 6 MB | github.com/ultralytics/assets |
| YOLO-World v2-s | `YOLO("yolov8s-worldv2.pt")` | **当前工作目录** | 25 MB | github.com/ultralytics/assets |
| CLIP ViT-L/14 (openai) | `open_clip.create_model_and_transforms("ViT-L-14", pretrained="openai")` | `~/.cache/huggingface/hub/models--timm--vit_large_patch14_clip_224.openai/` | ~1.6 GB（含元数据；权重本体 338 MB） | HuggingFace Hub |

## 离线/手动下载
```bash
# YOLO-World（如果首次自动下载失败）
wget -P ~/prjs/EEG_Obj_Detection \
  https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8s-worldv2.pt

# CLIP-L 用 huggingface-cli 预拉
pip install huggingface_hub
huggingface-cli download timm/vit_large_patch14_clip_224.openai
```

## 注意事项
- **YOLO 系列只看当前工作目录**，不是脚本目录。如果换目录跑 `collect.py`，要么把 `.pt` 复制过去，要么先 `cd ~/prjs/EEG_Obj_Detection`。
- CLIP 缓存可设环境变量 `HF_HOME` 或 `HUGGINGFACE_HUB_CACHE` 重定向（磁盘紧张时用）。
- 想换更准的检测器：`--yolo-world yolov8l-worldv2.pt`（~92 MB，自动下载）。
- 想换不同 CLIP 权重：改 `collect.py` 里 `load_clip()` 的 `"ViT-L-14", "openai"` 二元组，可选项见 `open_clip.list_pretrained()`。
