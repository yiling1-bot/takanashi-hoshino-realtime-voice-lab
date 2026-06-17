# API 契约

## 服务目标

提供一个本地 HTTP 接口，从文本生成语音。

默认地址：

```text
http://127.0.0.1:7860
```

## 生成语音

```http
POST /api/v1/tts
Content-Type: application/json
Accept: audio/wav
```

请求体：

```json
{
  "text": "你好",
  "language": "zh",
  "format": "wav",
  "speed": 1.0,
  "seed": 1234
}
```

字段说明：

- `text`：必填，要合成的文本。
- `language`：可选，`zh`、`jp`、`en`、`mixed`。
- `format`：可选，`wav` 或 `mp3`，默认 `wav`。
- `speed`：可选，语速，默认 `1.0`。
- `seed`：可选，用于复现结果。

响应：

```http
200 OK
Content-Type: audio/wav
```

响应体为音频二进制。

## JSON 响应模式

如果请求头为：

```http
Accept: application/json
```

则返回：

```json
{
  "audio_path": "outputs/samples/20260614_120000.wav",
  "duration_ms": 1830,
  "model": "gpt-sovits",
  "language": "zh"
}
```

## 健康检查

```http
GET /api/v1/health
```

返回：

```json
{
  "status": "ok",
  "model_loaded": true,
  "device": "cuda",
  "model_name": "hoshino"
}
```

## 模型信息

```http
GET /api/v1/model
```

返回：

```json
{
  "name": "hoshino",
  "backend": "gpt-sovits",
  "languages": ["zh", "jp"],
  "sample_rate": 32000
}
```

## 错误格式

```json
{
  "error": {
    "code": "TEXT_EMPTY",
    "message": "text cannot be empty"
  }
}
```

常见错误码：

- `TEXT_EMPTY`
- `MODEL_NOT_LOADED`
- `UNSUPPORTED_LANGUAGE`
- `SYNTHESIS_FAILED`
- `AUDIO_EXPORT_FAILED`

## 最小调用示例

```powershell
Invoke-WebRequest `
  -Uri "http://127.0.0.1:7860/api/v1/tts" `
  -Method POST `
  -ContentType "application/json" `
  -Headers @{ Accept = "audio/wav" } `
  -Body '{"text":"你好","language":"zh","format":"wav"}' `
  -OutFile "outputs/samples/hello.wav"
```
