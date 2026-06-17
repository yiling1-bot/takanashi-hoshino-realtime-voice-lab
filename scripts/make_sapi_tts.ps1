param(
    [string]$Text = "你好",
    [string]$Output = "E:\Codexworkspace\takanashi-hoshino-voice-api\outputs\samples\base_hello.wav",
    [string]$Voice = "Microsoft Huihui Desktop",
    [int]$Rate = 0,
    [int]$Volume = 100
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Speech

$OutDir = Split-Path $Output
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$Synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$Synth.SelectVoice($Voice)
$Synth.Rate = $Rate
$Synth.Volume = $Volume
$Synth.SetOutputToWaveFile($Output)
$Synth.Speak($Text)
$Synth.SetOutputToNull()
$Synth.Dispose()

Write-Host "output=$Output"
