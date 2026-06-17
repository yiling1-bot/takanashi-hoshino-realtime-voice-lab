# Chat TTS API

This layer turns a user message into an in-character line first, then sends that line to the existing local voice pipeline.

## Local Files

- `configs/chat_tts_config.json`: DeepSeek endpoint, model, key file path, and prompt file path.
- `configs/hoshino_lofi_prompt.txt`: local persona and lofi scene prompt.
- `configs/deepseek_api_key.txt`: local DeepSeek API key. Create this file yourself from `configs/deepseek_api_key.txt.example`.

The server reads these local files at request time. Do not put the API key in source control.

## Endpoints

`POST /api/v1/chat`

Returns generated text only. Use this to debug the persona response before waiting for audio.

```json
{
  "text": "你好",
  "reply_language": "zh",
  "scene": "lofi study room",
  "max_chars": 80,
  "temperature": 0.8
}
```

`POST /api/v1/chat-tts`

Returns a WAV file. The generated reply text is also placed in the `X-Hoshino-Reply` response header as URL-encoded UTF-8.

```json
{
  "text": "你好",
  "reply_language": "zh",
  "scene": "lofi study room",
  "max_chars": 80,
  "temperature": 0.8,
  "index_rate": 0.42,
  "auto_split": true
}
```

Example flow:

1. User input: `你好`
2. DeepSeek generates something like: `早上好，老师。要开始今天的工作了吗？先把音乐放轻一点，我们慢慢来。`
3. Local TTS/RVC returns the WAV.
