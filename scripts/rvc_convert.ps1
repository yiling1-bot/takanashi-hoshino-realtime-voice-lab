param(
    [string]$InputPath = "E:\Codexworkspace\takanashi-hoshino-voice-api\outputs\samples\base_hello.wav",
    [string]$Output = "E:\Codexworkspace\takanashi-hoshino-voice-api\outputs\samples\hoshino_hello.wav",
    [string]$RepoDir = "E:\Codexworkspace\external\Retrieval-based-Voice-Conversion-WebUI",
    [string]$VenvDir = "E:\Codexworkspace\takanashi-hoshino-voice-api\.venv-rvc",
    [string]$ModelName = "hoshino_jp_daily_rvc_40k_v1.pth",
    [string]$IndexPath = "E:\Codexworkspace\external\Retrieval-based-Voice-Conversion-WebUI\assets\indices\hoshino_jp_daily_rvc_40k_v1_IVF2283_Flat_nprobe_1_hoshino_jp_daily_rvc_40k_v1_v2.index",
    [string]$F0Method = "rmvpe",
    [double]$IndexRate = 0.48
)

$ErrorActionPreference = "Stop"
$Python = Join-Path $VenvDir "Scripts\python.exe"
$VenvScripts = Join-Path $VenvDir "Scripts"

if (-not (Test-Path $Python)) { throw "RVC environment not found." }
if (-not (Test-Path $InputPath)) { throw "Input audio not found: $InputPath" }
if (-not (Test-Path $IndexPath)) { throw "Index not found: $IndexPath" }

New-Item -ItemType Directory -Force -Path (Split-Path $Output) | Out-Null
$env:PATH = "$VenvScripts;$env:PATH"

Push-Location $RepoDir
try {
    & $Python .\tools\infer_cli.py `
        --f0up_key 0 `
        --input_path $InputPath `
        --index_path $IndexPath `
        --f0method $F0Method `
        --opt_path $Output `
        --model_name $ModelName `
        --index_rate $IndexRate `
        --device cuda `
        --is_half True `
        --filter_radius 3 `
        --resample_sr 0 `
        --rms_mix_rate 1 `
        --protect 0.33
    if ($LASTEXITCODE -ne 0) { throw "RVC conversion failed." }
} finally {
    Pop-Location
}

Write-Host "output=$Output"
