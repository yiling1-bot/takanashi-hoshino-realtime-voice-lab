param(
    [string]$ProjectDir = ""
)

$ErrorActionPreference = "Stop"
if (-not $ProjectDir) {
    $ProjectDir = Split-Path $PSScriptRoot -Parent
}

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

function Check-Path {
    param(
        [string]$Label,
        [string]$Path,
        [switch]$Required
    )
    if ($Path -and (Test-Path $Path)) {
        Write-Host "[OK]   $Label`: $Path"
        return $true
    }
    if ($Required) {
        Write-Host "[MISS] $Label required missing: $Path"
    } else {
        Write-Host "[WARN] $Label missing: $Path"
    }
    return (-not $Required)
}

Push-Location $ProjectDir
try {
    Import-DotEnv (Join-Path $ProjectDir ".env")

    $ok = $true
    $python = Join-Path $ProjectDir ".venv-rvc\Scripts\python.exe"
    $ffmpeg = Join-Path $ProjectDir ".venv-rvc\Scripts\ffmpeg.exe"
    $rvcRepo = if ($env:HOSHINO_RVC_REPO_DIR) {
        $env:HOSHINO_RVC_REPO_DIR
    } else {
        Join-Path (Split-Path $ProjectDir -Parent) "external\Retrieval-based-Voice-Conversion-WebUI"
    }
    $rvcModel = if ($env:HOSHINO_RVC_MODEL) { $env:HOSHINO_RVC_MODEL } else { "hoshino_jp_daily_rvc_40k_v1.pth" }
    $rvcModelPath = if ([System.IO.Path]::IsPathRooted($rvcModel)) {
        $rvcModel
    } else {
        Join-Path $rvcRepo "assets\weights\$rvcModel"
    }
    $rvcIndex = if ($env:HOSHINO_RVC_INDEX) {
        $env:HOSHINO_RVC_INDEX
    } else {
        Join-Path $rvcRepo "assets\indices\hoshino_jp_daily_rvc_40k_v1_IVF2283_Flat_nprobe_1_hoshino_jp_daily_rvc_40k_v1_v2.index"
    }

    $ok = (Check-Path "Project" $ProjectDir -Required) -and $ok
    $ok = (Check-Path ".env" (Join-Path $ProjectDir ".env")) -and $ok
    $ok = (Check-Path "DeepSeek key file" (Join-Path $ProjectDir "configs\deepseek_api_key.txt")) -and $ok
    $ok = (Check-Path "Python venv" $python -Required) -and $ok
    $ok = (Check-Path "ffmpeg" $ffmpeg -Required) -and $ok
    $ok = (Check-Path "RVC repo" $rvcRepo -Required) -and $ok
    $ok = (Check-Path "RVC model" $rvcModelPath -Required) -and $ok
    $ok = (Check-Path "RVC index" $rvcIndex -Required) -and $ok

    $keyPath = Join-Path $ProjectDir "configs\deepseek_api_key.txt"
    if (Test-Path $keyPath) {
        $key = (Get-Content -Raw $keyPath).Trim()
        if (-not $key -or $key.StartsWith("sk-your-")) {
            Write-Host "[WARN] DeepSeek key still looks like a placeholder."
        } else {
            Write-Host "[OK]   DeepSeek key is present."
        }
    }

    if (Test-Path $python) {
        Write-Host ""
        Write-Host "Python runtime check:"
        & $python -c "import fastapi, edge_tts, faster_whisper, soundfile, scipy; print('api_imports=ok')"
        if ($LASTEXITCODE -ne 0) { $ok = $false }
        & $python -c "import torch; print('torch=' + torch.__version__); print('cuda=' + str(torch.cuda.is_available())); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu')"
        if ($LASTEXITCODE -ne 0) { $ok = $false }
    }

    Write-Host ""
    if ($ok) {
        Write-Host "Doctor result: OK"
        exit 0
    }
    Write-Host "Doctor result: missing required items"
    exit 1
} finally {
    Pop-Location
}
