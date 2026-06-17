# RVC First Run Settings

Use these settings in RVC WebUI for the first training pass.

## Dataset

```text
E:\Codexworkspace\takanashi-hoshino-voice-api\data\processed\rvc_train\wavs
```

## Experiment

```text
hoshino_cn_rvc_40k_v1
```

## Training Settings

- Target sample rate: 40k
- Version: v2 if available
- Use F0: enabled
- F0 method: rmvpe if available, otherwise harvest
- Batch size: 4
- Epochs: 200
- Save interval: 25
- Cache dataset in GPU: disabled for 8GB VRAM
- Train feature index: enabled after model training

## Fallback Settings

If CUDA out-of-memory occurs:

- Batch size: 2
- Epochs: 150
- Cache dataset in GPU: disabled

## First Test Sentences

Generate base TTS audio for:

```text
你好
今天有点累呢
老师，要一起休息一下吗
```

Then convert with the trained RVC model.
