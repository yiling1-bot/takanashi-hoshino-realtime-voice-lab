# Open WebUI 接入教程

这篇文档说明如何把小鸟游星野 Realtime Voice Lab 接到 Open WebUI，作为一个本地 OpenAI-compatible TTS 服务使用。

## 目标

Open WebUI 负责聊天界面和大模型回复，本项目负责把文本回复转成“小鸟游星野风格”的语音。

```text
Open WebUI
  -> OpenAI-compatible TTS request
  -> 小鸟游星野 Realtime Voice Lab
  -> Edge TTS base audio
  -> local RVC voice conversion
  -> audio response
```

## 准备

先启动本项目服务：

```powershell
cd E:\Codexworkspace\takanashi-hoshino-voice-api
.\scripts\start_api.ps1
```

确认服务健康：

```powershell
Invoke-RestMethod http://127.0.0.1:7860/api/v1/health
```

至少确认：

- `status` 是 `ok`
- `index_exists` 是 `true`
- `rvc_warmed` 最好是 `true`
- `rvc_backend` 最好显示 `persistent:cuda`

## Open WebUI 里怎么填

进入 Open WebUI 的设置页面，找到语音或 TTS 设置。

如果它提供 OpenAI-compatible TTS 配置，优先这样填：

```text
TTS Engine: OpenAI 或 OpenAI-compatible
API Base URL: http://127.0.0.1:7860/v1
API Key: local
Model: hoshino-rvc-tts
Voice: alloy
Response Format: mp3
```

说明：

- `API Key` 可以随便填占位字符串，本项目目前不校验 key。
- `Voice` 填 `alloy` 是为了兼容 OpenAI 风格字段，最终仍会走本项目的 RVC 音色。
- 如果想指定基础 TTS 声线，可以填 `ja-JP-NanamiNeural`。
- 如果 Open WebUI 要求拉取模型或声音列表，本项目提供了 `GET /v1/models` 和 `GET /v1/audio/voices`。

## 手动测试

先不用 Open WebUI，直接测试接口是否能返回音频：

```powershell
Invoke-WebRequest `
  -Uri "http://127.0.0.1:7860/v1/audio/speech" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"model":"hoshino-rvc-tts","voice":"alloy","input":"せんせー……今日もゆっくり始めよっか。","response_format":"mp3","speed":1.0}' `
  -OutFile "outputs\samples\open_webui_test.mp3"
```

如果 `open_webui_test.mp3` 能正常播放，再接 Open WebUI。

## 常见问题

### Open WebUI 连接不上

先确认本项目服务在运行：

```powershell
Invoke-RestMethod http://127.0.0.1:7860/v1/models
Invoke-RestMethod http://127.0.0.1:7860/v1/audio/voices
```

如果 Open WebUI 跑在 Docker 里，`127.0.0.1` 指的是容器自己，不是 Windows 主机。可以尝试把 Base URL 改成：

```text
http://host.docker.internal:7860/v1
```

### 第一次生成很慢

第一次请求通常会初始化 CUDA、RVC、音频编码缓存。建议先访问一次 `/api/v1/health`，等 `rvc_warmed=true` 后再测试。

### 声音不是很自然

Open WebUI 只负责调用 TTS，声音自然度主要由本项目控制。可以从这些地方调：

- 输入文本是否太长
- `speed` 是否太快
- `index_rate` 是否过高
- 基础 TTS 是否一字一顿
- RVC 模型和 index 是否匹配

### 需要流式 TTS 吗

当前不支持 `stream_format=sse`。本项目会先生成完整音频，再一次性返回。

## 可以发到 Open WebUI Discussion 的草稿

```markdown
I built a local OpenAI-compatible TTS server using Edge TTS + RVC voice conversion.

Repo: https://github.com/yiling1-bot/takanashi-hoshino-realtime-voice-lab

It exposes:

- `POST /v1/audio/speech`
- `GET /v1/models`
- `GET /v1/audio/voices`

It can be used as a local TTS backend for Open WebUI's custom/OpenAI-compatible TTS settings.
The project is focused on local character voice experiments and does not include any voice data, model weights, generated audio, or API keys.

Feedback is welcome. I would like to know which fields/endpoints Open WebUI expects from OpenAI-compatible TTS servers so I can improve compatibility.
```
