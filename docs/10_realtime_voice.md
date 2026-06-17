# 实时语音架构

## 请求链路

```text
Browser MediaRecorder
  -> POST /api/v1/voice-chat
  -> faster-whisper transcription
  -> DeepSeek character reply
  -> Edge TTS base Japanese audio
  -> persistent RVC conversion
  -> /api/v1/audio/{request_id}
```

OpenAI-compatible TTS 入口走更短的链路：

```text
POST /v1/audio/speech
  -> Edge TTS base audio
  -> persistent RVC conversion
  -> mp3/opus/aac/flac/wav/pcm response
```

## 为什么使用常驻 RVC

普通命令行 RVC 每次请求都要启动 Python、加载模型、加载 HubERT/RMVPE，再执行转换。这个启动成本会让一次对话轻易超过几十秒。

当前服务在 FastAPI 启动时后台预热：

- Whisper 识别模型
- RVC `VC` 实例
- 目标 RVC 模型
- f0 推理相关资源

预热后每次请求只做实际音频转换，延迟会稳定很多。

## 默认参数

实时页面默认传入：

- `reply_language=ja`
- `max_chars=60`
- `temperature=0.45`
- `scene=quiet lofi night study room, lazy soft Hoshino-like senpai tone, short complete reply`

服务端日文 TTS 的自然度控制点主要在：

- 语速上限，避免过快
- 句间停顿，默认偏短但保留呼吸感
- 最低音高限制，避免开头压得太低
- 尾音延长，尤其是 `な`、`ね`、`よ`、`かな`
- RVC `index_rate`，避免音色死板或咬字变脏

## 低延迟建议

1. 服务启动后先访问 `/api/v1/health`，确认 `whisper_warmed=true` 和 `rvc_warmed=true`。
2. 首次请求通常比后续请求慢，因为系统还会初始化音频和 CUDA 缓存。
3. 如果 LLM 响应慢，优先降低 `max_chars`，并保持 `temperature` 在 `0.35` 到 `0.55`。
4. 如果 RVC 慢，确认使用的是 `HOSHINO_RVC_PERSISTENT=true`，并且 `rvc_backend` 显示为 `persistent:cuda`。
5. 如果显存不足，可以关闭常驻 RVC，但实时性会明显下降。

## 本地文件约定

不提交到仓库：

- `configs/deepseek_api_key.txt`
- `data/raw/`
- `data/processed/`
- `models/checkpoints/`
- `models/exported/`
- `outputs/`

需要用户自己准备：

- DeepSeek API key
- RVC WebUI 仓库
- RVC `.pth` 模型
- RVC `.index` 文件

## 常见问题

### 一直显示识别中

通常是浏览器录音没有触发 `MediaRecorder.onstop`、Whisper 初始化慢，或请求在后端异常。先看终端日志，再检查 `/api/v1/health`。

### 生成时间太长

先确认不是 DeepSeek 慢。响应 JSON 里有 `timings.transcribe_sec`、`timings.chat_sec` 和 `timings.tts_sec`，分别对应识别、LLM 和语音生成。

### 听起来一字一顿

优先调基础 TTS 的停顿、语速和文本切分。RVC 只能改变音色，不能完全修复基础 TTS 的语气问题。

### 音色太死板

降低或微调 `index_rate`，并增加更自然的基础 TTS 起伏。过高的 index rate 容易让音色稳定但表情僵硬。
