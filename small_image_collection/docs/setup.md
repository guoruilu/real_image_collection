# 环境搭建

本项目已在以下环境验证：
- Linux (WSL2 Ubuntu)
- NVIDIA GPU + CUDA 12.6 driver
- Python 3.10
- 主要包：PyTorch 2.6.0+cu126、ultralytics 8.4.48、open_clip_torch 3.3.0、icrawler 0.6.10

显存需求：≥4 GB（峰值出现在 CLIP-L 加载时）。CPU 也能跑，但 CLIP-L 推理会很慢。

## 方式 A：conda（推荐）

仓库根目录已带 `environment.yml`，一行建好：
```bash
conda env create -f environment.yml
conda activate eh
```

> `eh` 是默认环境名，可在 `environment.yml` 顶部改 `name`。

完成后做一次健康检查：
```bash
python -c "
import torch, open_clip
from ultralytics import YOLO
from icrawler.builtin import BingImageCrawler
print('CUDA:', torch.cuda.is_available(),
      torch.cuda.get_device_name(0) if torch.cuda.is_available() else '')
print('torch:', torch.__version__)
print('open_clip:', open_clip.__version__)
"
```
应输出 `CUDA: True ...` 和各包版本号。

## 方式 B：纯 pip / venv

```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip

# 先装 PyTorch（CUDA 12.6 轮子）
pip install --index-url https://download.pytorch.org/whl/cu126 \
    torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0

# 再装其它依赖
pip install -r requirements.txt
```

## 方式 C：从已有环境克隆
如果你机器上已有可用的 PyTorch 环境，只需补三个核心包：
```bash
pip install ultralytics==8.4.48 open_clip_torch==3.3.0 icrawler==0.6.10
```
其它依赖（pillow / pi-heif / opencv / huggingface_hub / timm / safetensors / ftfy / tqdm / numpy）大多是 PyTorch 生态默认装上的，缺什么补什么。

## 不同 CUDA 版本

把 PyTorch 安装命令中的 `cu126` 换成你驱动支持的版本即可（PyTorch 2.6 支持 `cu118` / `cu121` / `cu124` / `cu126`）。其它包不受 CUDA 版本影响。

CPU-only：
```bash
pip install --index-url https://download.pytorch.org/whl/cpu \
    torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0
```

## 模型权重

代码首次运行会自动下载，无需手动操作。位置和大小见 [docs/models.md](models.md)。如果机器不能联网，参照那篇先把权重 `wget` / `huggingface-cli download` 拉下来。

## 常见问题

- **`ModuleNotFoundError: No module named 'transformers'`**：本项目不需要 transformers，用的是 `open_clip_torch`。如果撞到这个，多半是误装了走 transformers 的 CLIP 实现，按 `requirements.txt` 重装即可。
- **首次跑 ultralytics 提示自动升级 pillow / 安装 pi-heif**：让它装就行，已经写进依赖。
- **YOLO 权重下载失败**：网络不通时手动 `wget` 到工作目录（命令见 `docs/models.md`）。
- **CLIP-L 拉不下来**：设代理 `HF_ENDPOINT=https://hf-mirror.com` 或用 `huggingface-cli download timm/vit_large_patch14_clip_224.openai` 预拉。
- **`QuickGELU mismatch` 警告**：open_clip 的提示信息，不影响结果，可忽略。
