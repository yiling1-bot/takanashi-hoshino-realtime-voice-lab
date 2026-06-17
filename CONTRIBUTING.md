# Contributing

欢迎提交改进，但请保持这个项目的边界清楚：仓库只放代码、脚本、文档和示例配置。

不要提交：

- API key、token、cookie 或任何私密配置
- 训练数据、官方素材、模型权重或 index 文件
- 生成音频、录音缓存、日志和实验输出
- 未确认授权来源的第三方素材

提交前建议运行：

```powershell
.\.venv-rvc\Scripts\python.exe -m py_compile api\server.py
[scriptblock]::Create((Get-Content -Raw scripts\start_api.ps1)) | Out-Null
[scriptblock]::Create((Get-Content -Raw scripts\setup_rvc_env.ps1)) | Out-Null
git status --short
```

如果改动会影响实时交互，请同时检查：

- `/api/v1/health` 里的 `whisper_warmed`
- `/api/v1/health` 里的 `rvc_warmed`
- `/api/v1/voice-chat` 响应里的 `timings`
- 浏览器实时页面是否能录音、自动停止、播放返回音频
