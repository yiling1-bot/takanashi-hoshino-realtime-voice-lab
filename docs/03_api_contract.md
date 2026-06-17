# API 契约

默认服务地址：

```text
http://127.0.0.1:7860
```

## 健康检查

```http
GET /api/v1/health
```

返回当前构建号、Whisper 预热状态、RVC 预热状态和后端信息。

```json
{
  "status": "ok",
  "api_build": "chat_tts_persistent_rvc_warm_20260617_024",
  "whisper_warmed": true,
  "rvc_warmed": true,
  "rvc_backend": "persistent:cuda/half=True"
}
```

## 文本转语音

### OpenAI-compatible

```http
POST /v1/audio/speech
Content-Type: application/json
```

请求体：

```json
{
  "model": "gpt-4o-mini-tts",
  "voice": "alloy",
  "input": "せんせー……まだ起きてたの？",
  "response_format": "mp3",
  "speed": 1.0
}
```

字段兼容 OpenAI TTS 常用参数：

- `model`：兼容字段，会写入响应头，不改变本地模型
- `input`：要合成的文本
- `voice`：兼容字段；传 OpenAI voice 名称时仍输出本项目音色，传 Edge voice id 时作为基础 TTS 声线
- `instructions`：兼容字段，当前不改变推理
- `response_format`：`mp3`、`opus`、`aac`、`flac`、`wav`、`pcm`
- `speed`：`0.25` 到 `4.0`，会映射到基础 TTS 语速
- `stream_format`：当前只支持 `audio`，不支持 `sse`

响应体是音频二进制。

OpenAI SDK 示例：

```python
from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:7860/v1", api_key="local")

with client.audio.speech.with_streaming_response.create(
    model="gpt-4o-mini-tts",
    voice="alloy",
    input="せんせー……まだ起きてたの？",
    response_format="mp3",
) as response:
    response.stream_to_file("hoshino.mp3")
```

为了兼容 Open WebUI 这类前端，还提供：

```http
GET /v1/models
GET /v1/audio/voices
```

`/v1/models` 返回本地 TTS 模型占位信息，`/v1/audio/voices` 返回可填写的 voice 名称列表。

### 原生接口

```http
POST /api/v1/tts
Content-Type: application/json
```

请求体：

```json
{
  "text": "せんせー……まだ起きてたの？",
  "format": "wav",
  "index_rate": 0.42,
  "auto_split": true,
  "pause_ms": 180,
  "rate": "-22%",
  "volume": "+0%",
  "lazy_style": true
}
```

响应：

```json
{
  "request_id": "ad6830f3d9da462ba975e24b48d563fa",
  "text": "せんせー……まだ起きてたの？",
  "voice": "ja-JP-NanamiNeural",
  "audio_url": "/api/v1/audio/ad6830f3d9da462ba975e24b48d563fa"
}
```

## 角色文本回复

```http
POST /api/v1/chat
Content-Type: application/json
```

请求体：

```json
{
  "text": "你好",
  "reply_language": "ja",
  "scene": "quiet lofi night study room",
  "max_chars": 60,
  "temperature": 0.45
}
```

响应：

```json
{
  "reply": "せんせー……おはよ。今日もゆっくり始めよっか。",
  "model": "deepseek-v4-flash",
  "prompt_file": "configs/hoshino_lofi_prompt.txt"
}
```

## 角色回复并生成语音

```http
POST /api/v1/chat-tts
Content-Type: application/json
```

请求体：

```json
{
  "text": "你好",
  "reply_language": "ja",
  "scene": "quiet lofi night study room",
  "max_chars": 60,
  "temperature": 0.45,
  "index_rate": 0.42,
  "auto_split": true,
  "lazy_style": true
}
```

响应为 WAV 二进制，生成的角色文本会放在 `X-Hoshino-Reply` 响应头里，使用 URL 编码的 UTF-8。

## 实时语音对话

```http
POST /api/v1/voice-chat
Content-Type: multipart/form-data
```

字段：

- `audio`：语音文件，浏览器默认上传 `audio/webm`
- `input_language`：`auto`、`zh`、`ja`
- `reply_language`：默认 `ja`
- `scene`：场景提示
- `max_chars`：回复最大字符数
- `temperature`：回复随机度

响应：

```json
{
  "transcript": "你好",
  "transcript_language": "zh",
  "reply": "せんせー……おはよ。今日もゆっくり始めよっか。",
  "audio_url": "/api/v1/audio/ad6830f3d9da462ba975e24b48d563fa",
  "request_id": "ad6830f3d9da462ba975e24b48d563fa",
  "chat_model": "deepseek-v4-flash",
  "whisper_model": "tiny",
  "timings": {
    "transcribe_sec": 0.7,
    "chat_sec": 1.2,
    "tts_sec": 3.5,
    "total_sec": 5.4
  }
}
```

## 音频文件

```http
GET /api/v1/audio/{request_id}
```

返回对应请求生成的 WAV 文件。
