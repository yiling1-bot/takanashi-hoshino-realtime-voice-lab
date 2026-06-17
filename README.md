# 小鸟游星野 Realtime Voice Lab

一个本地运行的实时语音对话项目：浏览器录音识别，AI 生成日文回复，再用 TTS + RVC 输出“小鸟游星野风格”的语音。

Realtime Hoshino-style voice chat: record speech in the browser, transcribe it locally, generate a Japanese reply, then output speech through TTS + RVC voice conversion.

项目目标是做一个低延迟、偏慵懒、柔软、日常对话感的“小鸟游星野风格”语音接口。仓库不包含训练数据、官方素材、模型权重、API key 或生成音频。

## 功能

- 实时网页入口：`http://127.0.0.1:7860/realtime`
- REST API：文本转语音、角色回复、语音输入转日文回复
- OpenAI-compatible TTS：`POST /v1/audio/speech`
- 常驻 RVC 推理：服务启动后预热模型，避免每次请求重新启动转换脚本
- Whisper 语音识别：默认 `tiny` + `cpu/int8`，优先保证启动和交互稳定
- 本地配置读取：DeepSeek key、角色提示词、RVC 模型路径都从本地文件或环境变量读取

## 免责声明

这是非官方的本地研究/二创工程模板。请只使用你有权使用的音频、模型和训练数据。不要把输出声明为官方角色、现实声优本人或任何未经授权身份的真实声音。

## 快速开始

要求：

- Windows 10/11
- Python 3.10，推荐使用 `uv`
- NVIDIA GPU，已测试 RTX 4060 级别显卡
- 可访问 DeepSeek API
- 本地 RVC WebUI 权重和索引文件

安装依赖：

```powershell
cd E:\Codexworkspace\takanashi-hoshino-voice-api
.\scripts\setup_rvc_env.ps1
```

准备 API key：

```powershell
Copy-Item configs\deepseek_api_key.txt.example configs\deepseek_api_key.txt
notepad configs\deepseek_api_key.txt
```

启动服务：

```powershell
.\scripts\start_api.ps1
```

打开实时页面：

```text
http://127.0.0.1:7860/realtime
```

## 配置

主要配置文件：

- `configs/chat_tts_config.json`：DeepSeek endpoint、模型名、key 文件路径、默认回复参数
- `configs/hoshino_lofi_prompt.txt`：角色和场景提示词
- `configs/deepseek_api_key.txt`：本地 API key，不提交到 Git

关键环境变量：

- `HOSHINO_PROJECT_DIR`：项目目录
- `HOSHINO_CHAT_CONFIG`：聊天配置文件路径
- `HOSHINO_RVC_REPO_DIR`：RVC WebUI 仓库路径
- `HOSHINO_RVC_VENV_DIR`：Python 虚拟环境路径
- `HOSHINO_RVC_MODEL`：RVC 模型文件名或路径
- `HOSHINO_RVC_INDEX`：RVC index 文件路径
- `HOSHINO_RVC_PERSISTENT`：是否启用常驻 RVC，默认启用
- `HOSHINO_WHISPER_MODEL`：Whisper 模型名，默认 `tiny`

## API

OpenAI-compatible 文本转语音：

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

外部工具通常这样填：

```text
Base URL: http://127.0.0.1:7860/v1
Endpoint: /audio/speech
API Key: 任意占位字符串
```

支持的 `response_format`：`mp3`、`opus`、`aac`、`flac`、`wav`、`pcm`。当前只支持非流式音频返回，`stream_format=sse` 会返回错误。

健康检查：

```http
GET /api/v1/health
```

文本直接转语音：

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

文本生成角色回复：

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

语音输入到日文回复音频：

```http
POST /api/v1/voice-chat
Content-Type: multipart/form-data
```

字段：

- `audio`：录音文件，浏览器默认 `audio/webm`
- `input_language`：`auto`、`zh`、`ja`
- `reply_language`：默认 `ja`
- `scene`：场景提示
- `max_chars`：回复最大字符数
- `temperature`：回复随机度

## 项目结构

```text
api/          FastAPI 服务和推理编排
configs/      本地配置、提示词和依赖清单
docs/         训练、接口、调参和实时语音说明
scripts/      环境安装、训练、索引、启动脚本
web/          实时语音网页
data/         本地训练数据，默认不提交
models/       本地模型权重，默认不提交
outputs/      生成音频和日志，默认不提交
```

## 开发说明

当前主路径是 `TTS -> RVC voice conversion`，所以自然度主要受基础 TTS、停顿切分、语速、音高和 RVC index rate 影响。低延迟交互优先使用常驻 RVC；如果显存不够，可以设置 `HOSHINO_RVC_PERSISTENT=false` 回退到命令行转换。

更多细节见 [docs/10_realtime_voice.md](docs/10_realtime_voice.md)。

## 接入其他项目

- [Open WebUI 中文接入教程](docs/11_open_webui_cn.md)
