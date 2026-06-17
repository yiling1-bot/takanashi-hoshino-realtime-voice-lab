param(
    [string]$ProjectDir = "",
    [string]$HostAddress = "127.0.0.1",
    [int]$Port = 7860,
    [string]$RvcRepoDir = "",
    [string]$RvcModel = "",
    [string]$RvcIndex = ""
)

$ErrorActionPreference = "Stop"

function Import-DotEnv {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return }
    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#") -or $line -notmatch "=") { return }
        $name, $value = $line.Split("=", 2)
        $name = $name.Trim()
        $value = $value.Trim().Trim('"').Trim("'")
        if ($name) {
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}

if (-not $ProjectDir) {
    $ProjectDir = Split-Path $PSScriptRoot -Parent
}
Import-DotEnv (Join-Path $ProjectDir ".env")
if (-not $PSBoundParameters.ContainsKey("HostAddress") -and $env:HOSHINO_HOST) {
    $HostAddress = $env:HOSHINO_HOST
}
if (-not $PSBoundParameters.ContainsKey("Port") -and $env:HOSHINO_PORT) {
    $Port = [int]$env:HOSHINO_PORT
}
if (-not $RvcRepoDir) {
    $RvcRepoDir = if ($env:HOSHINO_RVC_REPO_DIR) {
        $env:HOSHINO_RVC_REPO_DIR
    } else {
        Join-Path (Split-Path $ProjectDir -Parent) "external\Retrieval-based-Voice-Conversion-WebUI"
    }
}
if (-not $RvcModel) {
    $RvcModel = if ($env:HOSHINO_RVC_MODEL) {
        $env:HOSHINO_RVC_MODEL
    } else {
        "hoshino_jp_daily_rvc_40k_v1.pth"
    }
}
if (-not $RvcIndex) {
    $RvcIndex = if ($env:HOSHINO_RVC_INDEX) {
        $env:HOSHINO_RVC_INDEX
    } else {
        Join-Path $RvcRepoDir "assets\indices\hoshino_jp_daily_rvc_40k_v1_IVF2283_Flat_nprobe_1_hoshino_jp_daily_rvc_40k_v1_v2.index"
    }
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
