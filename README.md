# Takanashi Hoshino Realtime Voice Lab

中文名：小鸟游星野 Realtime Voice Lab

A local realtime voice chat project: record speech in the browser, transcribe it, generate a Japanese reply, then output a Hoshino-style voice through TTS + RVC voice conversion.

中文说明：这是一个本地实时语音对话项目。浏览器录音后，服务会识别语音、生成日文回复，再通过 TTS + RVC 输出偏“小鸟游星野风格”的语音。

This repository does not include training data, official assets, model weights, API keys, or generated audio.

中文说明：仓库不包含训练数据、官方素材、模型权重、API key 或生成音频。

## Features

- Realtime web UI: `http://127.0.0.1:7860/realtime`
- REST APIs for text-to-speech, character replies, and voice-to-voice chat
- OpenAI-compatible TTS endpoint: `POST /v1/audio/speech`
- Persistent RVC inference to avoid reloading the converter on every request
- Whisper ASR with default `tiny` + `cpu/int8`
- Local file based configuration for DeepSeek, persona prompt, RVC model, and RVC index

中文说明：

- 实时网页入口：`http://127.0.0.1:7860/realtime`
- 支持文本转语音、角色回复、语音输入到日文语音回复
- 兼容 OpenAI TTS 风格接口：`POST /v1/audio/speech`
- 常驻 RVC 推理，减少每次请求重新加载模型的延迟
- Whisper 语音识别默认使用 `tiny` + `cpu/int8`
- DeepSeek、角色提示词、RVC 模型和 index 都从本地文件配置

## Disclaimer

This is an unofficial local research and fan-project template. Use only audio, models, and datasets that you have the right to use. Do not present generated audio as an official release, a real voice actor's performance, or an authorized identity unless you have explicit rights to do so.

中文说明：这是非官方的本地研究/二创工程模板。请只使用你有权使用的音频、模型和训练数据。不要把生成音频声明为官方内容、现实声优本人或任何未经授权身份的真实声音。

## Requirements

- Windows 10/11
- Python 3.10, recommended through `uv`
- NVIDIA GPU, tested on RTX 4060 class hardware
- DeepSeek API access
- Local RVC WebUI model weight and index files

中文说明：

- Windows 10/11
- Python 3.10，推荐使用 `uv`
- NVIDIA 显卡，已在 RTX 4060 级别硬件上测试
- DeepSeek API
- 本地 RVC WebUI 模型权重和 index 文件

## Model Weights

The code repository does not store model weights in Git, but an optional model package is available as a GitHub Release asset:

- Release: [Hoshino JP Daily RVC 40k v1 model package](https://github.com/yiling1-bot/takanashi-hoshino-realtime-voice-lab/releases/tag/model-hoshino-jp-daily-rvc-40k-v1)
- Download: [hoshino_jp_daily_rvc_40k_v1.zip](https://github.com/yiling1-bot/takanashi-hoshino-realtime-voice-lab/releases/download/model-hoshino-jp-daily-rvc-40k-v1/hoshino_jp_daily_rvc_40k_v1.zip)
- Size: 145.29 MB
- SHA256: `969AAD13BFE3F4462DCDB4A995DE682320BFCF5CB00EF7B55B20E8E4975E1ABD`

After downloading, unzip the package and place:

```text
hoshino_jp_daily_rvc_40k_v1.pth
  -> <RVC WebUI>\assets\weights\

hoshino_jp_daily_rvc_40k_v1_IVF2283_Flat_nprobe_1_hoshino_jp_daily_rvc_40k_v1_v2.index
  -> <RVC WebUI>\assets\indices\
```

Then set these values in `.env`:

```text
HOSHINO_RVC_MODEL=hoshino_jp_daily_rvc_40k_v1.pth
HOSHINO_RVC_INDEX=<RVC WebUI>\assets\indices\hoshino_jp_daily_rvc_40k_v1_IVF2283_Flat_nprobe_1_hoshino_jp_daily_rvc_40k_v1_v2.index
```

中文说明：代码仓库本身不把模型权重放进 Git，但现在提供了 GitHub Release 模型包。下载 zip 后，把 `.pth` 放到 RVC WebUI 的 `assets\weights\`，把 `.index` 放到 `assets\indices\`，再在 `.env` 里配置 `HOSHINO_RVC_MODEL` 和 `HOSHINO_RVC_INDEX`。

## Quick Start

### 1. Clone

```powershell
git clone https://github.com/yiling1-bot/takanashi-hoshino-realtime-voice-lab.git
cd takanashi-hoshino-realtime-voice-lab
```

中文说明：先克隆仓库并进入项目目录。

### 2. Create local config files

```powershell
.\scripts\bootstrap.ps1
```

Then edit:

- `.env`: set your local RVC WebUI path, RVC model name, and RVC index path
- `configs\deepseek_api_key.txt`: put your DeepSeek API key here

These files are ignored by Git.

中文说明：运行 `bootstrap.ps1` 会生成 `.env` 和本地 key 文件。然后编辑 `.env` 填 RVC 路径、模型名和 index 路径；编辑 `configs\deepseek_api_key.txt` 填 DeepSeek API key。这些文件不会提交到 Git。

### 3. Install dependencies

```powershell
.\scripts\setup_rvc_env.ps1
```

中文说明：这个脚本会准备 Python 3.10 环境、RVC WebUI、CUDA PyTorch、RVC 依赖和 API 依赖。

### 4. Check the environment

```powershell
.\scripts\doctor.ps1
```

The doctor script checks Python, ffmpeg, RVC repo, model weight, index file, DeepSeek key, CUDA, and key Python imports.

中文说明：`doctor.ps1` 会检查 Python、ffmpeg、RVC 仓库、模型权重、index、DeepSeek key、CUDA 和关键 Python 包。如果缺东西，会直接指出来。

### 5. Start the API server

```powershell
.\scripts\start_api.ps1
```

Open:

```text
http://127.0.0.1:7860/realtime
```

中文说明：启动后打开实时语音页面即可测试。

## Configuration

Main local files:

- `.env`: machine-specific paths and runtime options, ignored by Git
- `configs/chat_tts_config.json`: DeepSeek endpoint, model, key file path, and defaults
- `configs/hoshino_lofi_prompt.txt`: persona and lofi scene prompt
- `configs/deepseek_api_key.txt`: local DeepSeek API key, ignored by Git

Important environment variables:

- `HOSHINO_PROJECT_DIR`: project directory
- `HOSHINO_CHAT_CONFIG`: chat config path
- `HOSHINO_RVC_REPO_DIR`: RVC WebUI repository path
- `HOSHINO_RVC_VENV_DIR`: Python environment path
- `HOSHINO_RVC_MODEL`: RVC model file name or path
- `HOSHINO_RVC_INDEX`: RVC index path
- `HOSHINO_RVC_PERSISTENT`: enable persistent RVC, enabled by default
- `HOSHINO_WHISPER_MODEL`: Whisper model name, default `tiny`

中文说明：通常只需要改 `.env` 和 `configs/deepseek_api_key.txt`。如果你不确定路径是否正确，先跑 `scripts\doctor.ps1`。

## API

### OpenAI-compatible TTS

```http
POST /v1/audio/speech
Content-Type: application/json
```

```json
{
  "model": "gpt-4o-mini-tts",
  "voice": "alloy",
  "input": "せんせー……まだ起きてたの？",
  "response_format": "mp3",
  "speed": 1.0
}
```

For external tools:

```text
Base URL: http://127.0.0.1:7860/v1
Endpoint: /audio/speech
API Key: any placeholder string
```

Supported `response_format`: `mp3`, `opus`, `aac`, `flac`, `wav`, `pcm`. Streaming with `stream_format=sse` is not supported yet.

中文说明：外部工具可以把本项目当成 OpenAI-compatible TTS 服务。Base URL 填 `http://127.0.0.1:7860/v1`，API Key 可以填任意占位字符串。当前只支持非流式音频返回。

### Native endpoints

Health:

```http
GET /api/v1/health
```

Text to speech:

```http
POST /api/v1/tts
Content-Type: application/json
```

```json
{
  "text": "先生、まだ起きてたの？",
  "format": "wav",
  "index_rate": 0.42,
  "auto_split": true,
  "lazy_style": true
}
```

Text to character reply:

```http
POST /api/v1/chat
Content-Type: application/json
```

```json
{
  "text": "你好",
  "reply_language": "ja",
  "scene": "quiet lofi night study room",
  "max_chars": 60,
  "temperature": 0.45
}
```

Voice input to Japanese voice reply:

```http
POST /api/v1/voice-chat
Content-Type: multipart/form-data
```

Fields:

- `audio`: uploaded recording, browser default is `audio/webm`
- `input_language`: `auto`, `zh`, or `ja`
- `reply_language`: default `ja`
- `scene`: scene prompt
- `max_chars`: max reply length
- `temperature`: reply randomness

中文说明：`/v1/audio/speech` 适合接 Open WebUI 等外部工具；`/api/v1/*` 是本项目自己的原生接口，适合调试完整流程。

## Switching to Chinese Output

If you want Chinese replies instead of Japanese replies, change `reply_language` from `ja` to `zh`.

For `/api/v1/chat` or `/api/v1/chat-tts`:

```json
{
  "text": "你好",
  "reply_language": "zh",
  "scene": "quiet lofi study room",
  "max_chars": 80,
  "temperature": 0.6
}
```

For the realtime browser page, edit `web/realtime.html` and change:

```js
form.append("reply_language", "ja");
```

to:

```js
form.append("reply_language", "zh");
```

For project defaults, edit `configs/chat_tts_config.json`:

```json
"chat_defaults": {
  "reply_language": "zh"
}
```

For the OpenAI-compatible TTS endpoint, there is no separate reply language setting. It only speaks the `input` text. If `input` is Chinese, it will synthesize Chinese speech:

```json
{
  "model": "hoshino-rvc-tts",
  "voice": "alloy",
  "input": "老师，今天也慢慢来吧。",
  "response_format": "mp3"
}
```

中文说明：如果想输出中文回复，把 `reply_language` 从 `ja` 改成 `zh` 即可。实时网页要改 `web/realtime.html` 里的 `form.append("reply_language", "ja")`。OpenAI-compatible TTS 接口没有回复语言设置，它只是把 `input` 读出来；输入中文就会输出中文语音。

## Project Structure

```text
api/          FastAPI server and inference orchestration
configs/      Local configs, prompts, and dependency lists
docs/         Training, API, tuning, and integration docs
scripts/      Setup, training, index, and launch scripts
web/          Realtime browser UI
data/         Local training data, ignored by default
models/       Local model weights, ignored by default
outputs/      Generated audio and logs, ignored by default
```

中文说明：开源仓库只放代码、脚本、文档和示例配置。训练数据、模型权重、生成音频和日志默认不提交。

## Notes

The current pipeline is:

```text
base TTS -> RVC voice conversion
```

Naturalness mainly depends on base TTS quality, text splitting, pauses, speed, pitch, and RVC index rate. Low-latency interaction is best with persistent RVC enabled. If VRAM is limited, set `HOSHINO_RVC_PERSISTENT=false` to fall back to CLI conversion.

中文说明：当前主路径是 `基础 TTS -> RVC 变声`。自然度主要受基础 TTS、停顿切分、语速、音高和 RVC index rate 影响。显存足够时建议启用常驻 RVC。

More details:

- [Realtime voice architecture](docs/10_realtime_voice.md)
- [Open WebUI integration guide in Chinese](docs/11_open_webui_cn.md)
- [Reproducible local setup in Chinese](docs/12_reproducible_setup_cn.md)

## Helper Scripts

- `scripts/bootstrap.ps1`: create `.env`, local key file, and output directories
- `scripts/doctor.ps1`: check Python, ffmpeg, RVC repo, model, index, DeepSeek key, and key Python packages
- `scripts/start_api.ps1`: start the service and load `.env`

中文说明：

- `scripts/bootstrap.ps1`：生成 `.env` 和本地 key 文件，占位初始化输出目录
- `scripts/doctor.ps1`：检查 Python、ffmpeg、RVC 仓库、模型、index、DeepSeek key 和关键依赖
- `scripts/start_api.ps1`：启动服务，并自动读取 `.env`
