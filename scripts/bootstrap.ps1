param(
    [string]$ProjectDir = ""
)

$ErrorActionPreference = "Stop"
if (-not $ProjectDir) {
    $ProjectDir = Split-Path $PSScriptRoot -Parent
}

function Copy-ExampleIfMissing {
    param(
        [string]$Example,
        [string]$Target
    )
    if (Test-Path $Target) {
        Write-Host "Exists: $Target"
        return
    }
    Copy-Item -LiteralPath $Example -Destination $Target
    Write-Host "Created: $Target"
}

Push-Location $ProjectDir
try {
    Copy-ExampleIfMissing ".env.example" ".env"
    Copy-ExampleIfMissing "configs\deepseek_api_key.txt.example" "configs\deepseek_api_key.txt"
    New-Item -ItemType Directory -Force -Path "outputs\samples", "outputs\api", "outputs\voice_input", "outputs\warmup" | Out-Null

    Write-Host ""
    Write-Host "Bootstrap complete."
    Write-Host "Next:"
    Write-Host "  1. Edit .env and set your RVC paths."
    Write-Host "  2. Edit configs\deepseek_api_key.txt and put your DeepSeek API key there."
    Write-Host "  3. Run scripts\doctor.ps1."
    Write-Host "  4. Run scripts\setup_rvc_env.ps1 if the Python environment is missing."
    Write-Host "  5. Run scripts\start_api.ps1."
} finally {
    Pop-Location
}
