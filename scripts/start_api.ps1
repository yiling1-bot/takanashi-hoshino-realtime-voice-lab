param(
    [string]$ProjectDir = "",
    [string]$HostAddress = "127.0.0.1",
    [int]$Port = 7860,
    [string]$RvcRepoDir = "",
    [string]$RvcModel = "hoshino_jp_daily_rvc_40k_v1.pth",
    [string]$RvcIndex = ""
)

$ErrorActionPreference = "Stop"
if (-not $ProjectDir) {
    $ProjectDir = Split-Path $PSScriptRoot -Parent
}
if (-not $RvcRepoDir) {
    $RvcRepoDir = Join-Path (Split-Path $ProjectDir -Parent) "external\Retrieval-based-Voice-Conversion-WebUI"
}
if (-not $RvcIndex) {
    $RvcIndex = Join-Path $RvcRepoDir "assets\indices\hoshino_jp_daily_rvc_40k_v1_IVF2283_Flat_nprobe_1_hoshino_jp_daily_rvc_40k_v1_v2.index"
}
$Python = Join-Path $ProjectDir ".venv-rvc\Scripts\python.exe"
$VenvScripts = Join-Path $ProjectDir ".venv-rvc\Scripts"

if (-not (Test-Path $Python)) {
    throw "Python environment not found. Run scripts\setup_rvc_env.ps1 first."
}

$env:PATH = "$VenvScripts;$env:PATH"
$env:HOSHINO_PROJECT_DIR = $ProjectDir
$env:HOSHINO_RVC_REPO_DIR = $RvcRepoDir
$env:HOSHINO_RVC_VENV_DIR = Join-Path $ProjectDir ".venv-rvc"
$env:HOSHINO_RVC_MODEL = $RvcModel
$env:HOSHINO_RVC_INDEX = $RvcIndex

Push-Location $ProjectDir
try {
    & $Python -m uvicorn api.server:app --host $HostAddress --port $Port
} finally {
    Pop-Location
}
