param(
    [string]$RepoDir = "E:\Codexworkspace\external\Retrieval-based-Voice-Conversion-WebUI",
    [string]$VenvDir = "E:\Codexworkspace\takanashi-hoshino-voice-api\.venv-rvc"
)

$ErrorActionPreference = "Stop"
$Python = Join-Path $VenvDir "Scripts\python.exe"

if (-not (Test-Path $Python)) {
    throw "RVC environment not found. Run scripts\setup_rvc_env.ps1 first."
}

if (-not (Test-Path (Join-Path $RepoDir "tools\download_models.py"))) {
    throw "RVC repo not found. Run scripts\setup_rvc_env.ps1 first."
}

Push-Location $RepoDir
try {
    & $Python .\tools\download_models.py
} finally {
    Pop-Location
}
