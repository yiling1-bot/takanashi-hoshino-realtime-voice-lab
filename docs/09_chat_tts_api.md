# Chat TTS API

这一层先把用户输入交给 DeepSeek，生成符合角色和场景的短句，再送进本地 TTS + RVC 管线。

## 本地文件

- `configs/chat_tts_config.json`：DeepSeek endpoint、模型、key 文件路径和默认参数
- `configs/hoshino_lofi_prompt.txt`：本地角色与 lofi 场景提示词
- `configs/deepseek_api_key.txt`：本地 DeepSeek API key，不提交到 Git

服务端会在请求时读取这些文件。更新 prompt 后通常不需要重启服务。

## 文本调试

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

这个接口只返回文本，适合先调角色回复，不用等待音频。

## 文本到角色语音

```http
POST /api/v1/chat-tts
Content-Type: application/json
Accept: audio/wav
```

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

响应体是 WAV 音频。生成的回复文本放在 `X-Hoshino-Reply` 响应头里。

## 示例流程

1. 用户输入：`你好`
2. DeepSeek 生成：`せんせー……おはよ。今日もゆっくり始めよっか。`
3. Edge TTS 生成基础日文语音
4. 本地 RVC 转换成目标音色
5. API 返回 WAV
