param(
    [string]$ProjectDir = "E:\Codexworkspace\takanashi-hoshino-voice-api",
    [string]$HostAddress = "127.0.0.1",
    [int]$Port = 7860
)

$ErrorActionPreference = "Stop"
$Python = Join-Path $ProjectDir ".venv-rvc\Scripts\python.exe"
$VenvScripts = Join-Path $ProjectDir ".venv-rvc\Scripts"

if (-not (Test-Path $Python)) {
    throw "Python environment not found. Run scripts\setup_rvc_env.ps1 first."
}

$env:PATH = "$VenvScripts;$env:PATH"
$env:HOSHINO_PROJECT_DIR = $ProjectDir
$env:HOSHINO_RVC_REPO_DIR = "E:\Codexworkspace\external\Retrieval-based-Voice-Conversion-WebUI"
$env:HOSHINO_RVC_VENV_DIR = Join-Path $ProjectDir ".venv-rvc"
$env:HOSHINO_RVC_MODEL = "hoshino_jp_daily_rvc_40k_v1.pth"
$env:HOSHINO_RVC_INDEX = "E:\Codexworkspace\external\Retrieval-based-Voice-Conversion-WebUI\assets\indices\hoshino_jp_daily_rvc_40k_v1_IVF2283_Flat_nprobe_1_hoshino_jp_daily_rvc_40k_v1_v2.index"

Push-Location $ProjectDir
try {
    & $Python -m uvicorn api.server:app --host $HostAddress --port $Port
} finally {
    Pop-Location
}
