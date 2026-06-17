param(
    [string]$RepoDir = "E:\Codexworkspace\external\Retrieval-based-Voice-Conversion-WebUI",
    [string]$VenvDir = "E:\Codexworkspace\takanashi-hoshino-voice-api\.venv-rvc",
    [string]$Experiment = "hoshino_cn_rvc_40k_v1",
    [int]$Epochs = 200,
    [int]$BatchSize = 4,
    [int]$SaveEveryEpoch = 25
)

$ErrorActionPreference = "Stop"
$Python = Join-Path $VenvDir "Scripts\python.exe"
$VenvScripts = Join-Path $VenvDir "Scripts"
$ExpLogDir = Join-Path $RepoDir "logs\$Experiment"

if (-not (Test-Path $Python)) {
    throw "RVC environment not found. Run scripts\setup_rvc_env.ps1 first."
}
if (-not (Test-Path (Join-Path $VenvScripts "ffmpeg.exe"))) {
    throw "ffmpeg.exe not found in RVC environment. Run scripts\setup_rvc_env.ps1 first."
}
if (-not (Test-Path (Join-Path $ExpLogDir "filelist.txt"))) {
    throw "RVC filelist not found. Run scripts\run_rvc_training.ps1 once first."
}
if (-not (Test-Path (Join-Path $ExpLogDir "config.json"))) {
    throw "RVC config not found. Run scripts\run_rvc_training.ps1 once first."
}

$env:PATH = "$VenvScripts;$env:PATH"

Push-Location $RepoDir
try {
    & $Python .\infer\modules\train\train.py `
        -e $Experiment `
        -sr 40k `
        -f0 1 `
        -bs $BatchSize `
        -g 0 `
        -te $Epochs `
        -se $SaveEveryEpoch `
        -pg .\assets\pretrained_v2\f0G40k.pth `
        -pd .\assets\pretrained_v2\f0D40k.pth `
        -l 1 `
        -c 0 `
        -sw 1 `
        -v v2
} finally {
    Pop-Location
}
