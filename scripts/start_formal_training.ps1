param(
    [string]$ProjectDir = "E:\Codexworkspace\takanashi-hoshino-voice-api",
    [string]$Experiment = "hoshino_cn_rvc_40k_v1",
    [int]$Epochs = 200,
    [int]$BatchSize = 4,
    [int]$SaveEveryEpoch = 25
)

$ErrorActionPreference = "Stop"
$LogsDir = Join-Path $ProjectDir "outputs\training_logs"
New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Stdout = Join-Path $LogsDir "$Experiment`_$Timestamp.out.log"
$Stderr = Join-Path $LogsDir "$Experiment`_$Timestamp.err.log"
$Script = Join-Path $ProjectDir "scripts\run_rvc_train_only.ps1"

$Args = @(
    "-ExecutionPolicy", "Bypass",
    "-File", "`"$Script`"",
    "-Experiment", $Experiment,
    "-Epochs", $Epochs,
    "-BatchSize", $BatchSize,
    "-SaveEveryEpoch", $SaveEveryEpoch
)

$Process = Start-Process `
    -FilePath "powershell.exe" `
    -ArgumentList $Args `
    -WindowStyle Hidden `
    -RedirectStandardOutput $Stdout `
    -RedirectStandardError $Stderr `
    -PassThru

$PidFile = Join-Path $LogsDir "$Experiment.pid"
$Process.Id | Set-Content -Encoding ascii $PidFile

Write-Host "started_pid=$($Process.Id)"
Write-Host "stdout=$Stdout"
Write-Host "stderr=$Stderr"
Write-Host "pid_file=$PidFile"
