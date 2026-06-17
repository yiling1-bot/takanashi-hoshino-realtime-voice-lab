param(
    [string]$RepoDir = "E:\Codexworkspace\external\Retrieval-based-Voice-Conversion-WebUI",
    [string]$VenvDir = "E:\Codexworkspace\takanashi-hoshino-voice-api\.venv-rvc"
)

$ErrorActionPreference = "Stop"
$Python = Join-Path $VenvDir "Scripts\python.exe"
$VenvScripts = Join-Path $VenvDir "Scripts"

if (-not (Test-Path $Python)) {
    throw "RVC environment not found. Run scripts\setup_rvc_env.ps1 first."
}

if (-not (Test-Path (Join-Path $RepoDir "infer-web.py"))) {
    throw "RVC repo not found. Run scripts\setup_rvc_env.ps1 first."
}
if (Test-Path (Join-Path $VenvScripts "ffmpeg.exe")) {
    $env:PATH = "$VenvScripts;$env:PATH"
}

Push-Location $RepoDir
try {
    & $Python .\infer-web.py
} finally {
    Pop-Location
}
