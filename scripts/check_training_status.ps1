param(
    [string]$ProjectDir = "E:\Codexworkspace\takanashi-hoshino-voice-api",
    [string]$RepoDir = "E:\Codexworkspace\external\Retrieval-based-Voice-Conversion-WebUI",
    [string]$Experiment = "hoshino_cn_rvc_40k_v1"
)

$LogsDir = Join-Path $ProjectDir "outputs\training_logs"
$PidFile = Join-Path $LogsDir "$Experiment.pid"
$PidValue = if (Test-Path $PidFile) { Get-Content $PidFile -ErrorAction SilentlyContinue | Select-Object -First 1 } else { $null }
$Proc = if ($PidValue) { Get-Process -Id ([int]$PidValue) -ErrorAction SilentlyContinue } else { $null }

Write-Host "process_running=$([bool]$Proc)"
if ($Proc) {
    Write-Host "pid=$($Proc.Id)"
    Write-Host "started=$($Proc.StartTime)"
}

$ExpDir = Join-Path $RepoDir "logs\$Experiment"
if (Test-Path $ExpDir) {
    Get-ChildItem $ExpDir -File |
        Where-Object { $_.Extension -eq ".pth" -or $_.Name -eq "train.log" } |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 10 FullName,Length,LastWriteTime |
        Format-Table -AutoSize
}

$WeightsDir = Join-Path $RepoDir "assets\weights"
if (Test-Path $WeightsDir) {
    Get-ChildItem $WeightsDir -File |
        Where-Object { $_.Name -like "$Experiment*" } |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 10 Name,Length,LastWriteTime |
        Format-Table -AutoSize
}
