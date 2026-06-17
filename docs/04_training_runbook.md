# Two-Day Training Runbook

## Current Dataset Result

Source:

```text
E:\Codexworkspace\voice
```

Audit result:

- Files: 213 `.ogg`
- Total duration: about 17m 4s
- Prepared training candidates: 131 `.wav`
- Prepared training duration: about 10m 25s
- Channels: mono
- Original sample rates: 44.1kHz and 48kHz
- Prepared sample rate: 40kHz

Prepared data:

```text
data/processed/rvc_train/wavs/
data/processed/rvc_train/rvc_filelist.txt
data/processed/rvc_train/prepare_summary.csv
```

## Decision

Use RVC first.

Reason:

- The dataset is pure voice and around 10 minutes after filtering, which is enough for a first RVC model.
- No transcript file is present in the provided folders, so direct text-to-speech fine-tuning is not the fastest first route.
- The target API can still accept text by using this pipeline:

```text
text -> base Chinese TTS -> RVC voice conversion -> returned audio
```

## Hardware Budget

Detected GPU:

```text
NVIDIA GeForce RTX 4060 Laptop GPU, 8188 MiB VRAM
```

Current system Python has CPU-only PyTorch, so training needs a separate CUDA environment.

## Time Budget

Limit: under 2 days.

Recommended first run:

- Sample rate: 40k
- Epochs: 200
- Batch size: start with 4
- Save interval: 25 epochs
- F0: enabled
- Index: enabled after model training

Fallback if VRAM is insufficient:

- Batch size: 2
- Keep 40k sample rate
- Reduce epoch to 150 for first pass

Expected work plan:

| Step | Target time |
| --- | ---: |
| Environment setup | 30m to 2h |
| Preprocessing and feature extraction | 10m to 40m |
| First RVC training | 1h to 6h |
| Index training and inference test | 15m to 1h |
| Base TTS + API wrapper | 1h to 3h |
| Parameter retest | remaining time |

## Commands Already Run

Audit:

```powershell
python .\scripts\audit_dataset.py `
  --input E:\Codexworkspace\voice `
  --manifest .\data\processed\manifest.csv `
  --report .\data\processed\audit_report.md
```

Prepare:

```powershell
python .\scripts\prepare_voice_dataset.py `
  --manifest .\data\processed\manifest.csv `
  --output .\data\processed\rvc_train `
  --sample-rate 40000
```

## Next Execution Steps

1. Create a Python 3.10 CUDA environment.
2. Install RVC WebUI or compatible RVC training implementation.
3. Download RVC base weights.
4. Import/copy `data/processed/rvc_train/wavs/` as the dataset.
5. Train the first RVC model.
6. Generate test conversions using:

```text
你好
今天有点累呢
老师，要一起休息一下吗
```

7. Add a FastAPI endpoint:

```text
POST /api/v1/tts
```

## Local Environment Status

Created environment:

```text
E:\Codexworkspace\takanashi-hoshino-voice-api\.venv-rvc
```

RVC repo:

```text
E:\Codexworkspace\external\Retrieval-based-Voice-Conversion-WebUI
```

CUDA verification:

```text
torch 2.12.0+cu126
cuda=True
NVIDIA GeForce RTX 4060 Laptop GPU
```

RVC WebUI:

```text
http://127.0.0.1:7865
```

Base model weights were downloaded with:

```powershell
.\scripts\download_rvc_models.ps1
```

## Quality Notes

- This data appears to contain many short game voice lines. Short expressive clips are useful for voice color, but they can overfit emotion and pacing.
- The first API version should be treated as a practical demo, not a final production TTS model.
- If you later provide transcripts, a GPT-SoVITS route can be added for more direct text-to-speech control.
