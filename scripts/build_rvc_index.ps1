param(
    [string]$RepoDir = "E:\Codexworkspace\external\Retrieval-based-Voice-Conversion-WebUI",
    [string]$VenvDir = "E:\Codexworkspace\takanashi-hoshino-voice-api\.venv-rvc",
    [string]$ProjectDir = "E:\Codexworkspace\takanashi-hoshino-voice-api",
    [string]$Experiment = "hoshino_cn_rvc_40k_v1"
)

$ErrorActionPreference = "Stop"
$Python = Join-Path $VenvDir "Scripts\python.exe"

if (-not (Test-Path $Python)) {
    throw "RVC environment not found. Run scripts\setup_rvc_env.ps1 first."
}

& $Python (Join-Path $ProjectDir "scripts\build_rvc_index.py") --repo $RepoDir --exp $Experiment --version v2
if ($LASTEXITCODE -ne 0) { throw "RVC index build failed." }
