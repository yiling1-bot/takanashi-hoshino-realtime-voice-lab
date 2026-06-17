# 可复现部署说明

这份文档面向第一次 clone 项目的用户，目标是让环境问题尽早暴露，而不是启动后才报错。

## 一句话流程

```powershell
git clone https://github.com/yiling1-bot/takanashi-hoshino-realtime-voice-lab.git
cd takanashi-hoshino-realtime-voice-lab
.\scripts\bootstrap.ps1
notepad .env
notepad configs\deepseek_api_key.txt
.\scripts\setup_rvc_env.ps1
.\scripts\doctor.ps1
.\scripts\start_api.ps1
```

## 本地文件

`bootstrap.ps1` 会创建：

- `.env`
- `configs\deepseek_api_key.txt`
- `outputs\api`
- `outputs\samples`
- `outputs\voice_input`
- `outputs\warmup`

`.env` 和 `configs\deepseek_api_key.txt` 都被 `.gitignore` 排除，不会进入仓库。

## 模型包下载

如果你要复现当前默认的日文 RVC 音色，可以下载 GitHub Release 模型包：

- Release: [Hoshino JP Daily RVC 40k v1 model package](https://github.com/yiling1-bot/takanashi-hoshino-realtime-voice-lab/releases/tag/model-hoshino-jp-daily-rvc-40k-v1)
- Download: [hoshino_jp_daily_rvc_40k_v1.zip](https://github.com/yiling1-bot/takanashi-hoshino-realtime-voice-lab/releases/download/model-hoshino-jp-daily-rvc-40k-v1/hoshino_jp_daily_rvc_40k_v1.zip)
- SHA256: `969AAD13BFE3F4462DCDB4A995DE682320BFCF5CB00EF7B55B20E8E4975E1ABD`

下载后解压：

```text
hoshino_jp_daily_rvc_40k_v1.pth
  -> <RVC WebUI>\assets\weights\

hoshino_jp_daily_rvc_40k_v1_IVF2283_Flat_nprobe_1_hoshino_jp_daily_rvc_40k_v1_v2.index
  -> <RVC WebUI>\assets\indices\
```

## .env 需要改什么

最重要的是这三项：

```text
HOSHINO_RVC_REPO_DIR=E:\Codexworkspace\external\Retrieval-based-Voice-Conversion-WebUI
HOSHINO_RVC_MODEL=hoshino_jp_daily_rvc_40k_v1.pth
HOSHINO_RVC_INDEX=E:\Codexworkspace\external\Retrieval-based-Voice-Conversion-WebUI\assets\indices\hoshino_jp_daily_rvc_40k_v1_IVF2283_Flat_nprobe_1_hoshino_jp_daily_rvc_40k_v1_v2.index
```

模型文件默认按 RVC WebUI 的约定放在：

```text
<RVC repo>\assets\weights\
```

index 文件默认按 RVC WebUI 的约定放在：

```text
<RVC repo>\assets\indices\
```

## doctor.ps1 会检查什么

- 项目目录
- `.env`
- DeepSeek key 文件
- `.venv-rvc\Scripts\python.exe`
- `.venv-rvc\Scripts\ffmpeg.exe`
- RVC WebUI 仓库
- RVC `.pth` 模型
- RVC `.index` 文件
- API 依赖导入
- PyTorch CUDA 状态

如果 `doctor.ps1` 通过，再启动服务会省很多排错时间。

## 常见复现问题

### GitHub clone 后没有模型

正常。仓库不包含训练数据、模型权重、index、生成音频或 API key。你需要自己准备这些本地文件。

### .env 写了路径但启动没生效

确认使用的是：

```powershell
.\scripts\start_api.ps1
```

不要直接运行 `uvicorn api.server:app`，否则 `.env` 不会由启动脚本加载。

### Open WebUI 跑在 Docker 里连不上

把 Open WebUI 里的 Base URL 从：

```text
http://127.0.0.1:7860/v1
```

改成：

```text
http://host.docker.internal:7860/v1
```

### 要不要提交 .env

不要。`.env` 是本机路径配置，可能暴露你的目录结构。真实 API key 更不能提交。
