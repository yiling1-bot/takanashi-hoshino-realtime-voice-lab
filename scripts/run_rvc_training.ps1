param(
    [string]$RepoDir = "E:\Codexworkspace\external\Retrieval-based-Voice-Conversion-WebUI",
    [string]$VenvDir = "E:\Codexworkspace\takanashi-hoshino-voice-api\.venv-rvc",
    [string]$DatasetDir = "E:\Codexworkspace\takanashi-hoshino-voice-api\data\processed\rvc_train\wavs",
    [string]$Experiment = "hoshino_cn_rvc_40k_v1",
    [int]$Epochs = 200,
    [int]$BatchSize = 4,
    [int]$SaveEveryEpoch = 25,
    [int]$NumProcesses = 4
)

$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path $PSScriptRoot -Parent
$Python = Join-Path $VenvDir "Scripts\python.exe"
$VenvScripts = Join-Path $VenvDir "Scripts"
$ExpLogDir = Join-Path $RepoDir "logs\$Experiment"

if (-not (Test-Path $Python)) {
    throw "RVC environment not found. Run scripts\setup_rvc_env.ps1 first."
}
if (-not (Test-Path $DatasetDir)) {
    throw "Dataset directory not found: $DatasetDir"
}
if (-not (Test-Path (Join-Path $VenvScripts "ffmpeg.exe"))) {
    throw "ffmpeg.exe not found in RVC environment. Run scripts\setup_rvc_env.ps1 first."
}

$env:PATH = "$VenvScripts;$env:PATH"

New-Item -ItemType Directory -Force -Path $ExpLogDir | Out-Null

Push-Location $RepoDir
try {
    Write-Host "Step 1/5: preprocessing dataset..."
    & $Python .\infer\modules\train\preprocess.py $DatasetDir 40000 $NumProcesses ".\logs\$Experiment" False 3.7
    if ($LASTEXITCODE -ne 0) { throw "RVC preprocessing failed." }

    Write-Host "Step 2/5: extracting F0 with RMVPE..."
    & $Python .\infer\modules\train\extract\extract_f0_rmvpe.py 1 0 0 ".\logs\$Experiment" True
    if ($LASTEXITCODE -ne 0) { throw "RVC F0 extraction failed." }

    Write-Host "Step 3/5: extracting HuBERT features..."
    & $Python .\infer\modules\train\extract_feature_print.py cuda 1 0 0 ".\logs\$Experiment" v2 True
    if ($LASTEXITCODE -ne 0) { throw "RVC feature extraction failed." }

    Write-Host "Step 4/5: generating filelist and config..."
    & $Python (Join-Path $ProjectDir "scripts\make_rvc_filelist.py") --repo $RepoDir --exp $Experiment --sr 40k --version v2 --speaker-id 0
    if ($LASTEXITCODE -ne 0) { throw "RVC filelist generation failed." }

    Write-Host "Step 5/5: training model..."
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
    if ($LASTEXITCODE -ne 0) { throw "RVC training failed." }

    Write-Host "Training complete. Build the feature index in WebUI or run train_index from infer-web.py."
} finally {
    Pop-Location
}
