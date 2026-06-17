param(
    [string]$RepoDir = "",
    [string]$VenvDir = ""
)

$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path $PSScriptRoot -Parent
if (-not $RepoDir) {
    $RepoDir = Join-Path (Split-Path $ProjectDir -Parent) "external\Retrieval-based-Voice-Conversion-WebUI"
}
if (-not $VenvDir) {
    $VenvDir = Join-Path $ProjectDir ".venv-rvc"
}

Write-Host "Preparing Python 3.10 with uv..."
uv python install 3.10
if (-not (Test-Path $VenvDir)) {
    uv venv --python 3.10 $VenvDir
    if ($LASTEXITCODE -ne 0) { throw "Failed to create Python 3.10 virtual environment." }
} else {
    Write-Host "Reusing existing virtual environment: $VenvDir"
}

$Python = Join-Path $VenvDir "Scripts\python.exe"

Write-Host "Cloning RVC WebUI..."
if (-not (Test-Path $RepoDir)) {
    New-Item -ItemType Directory -Force -Path (Split-Path $RepoDir) | Out-Null
    git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git $RepoDir
} else {
    git -C $RepoDir pull --ff-only
}

Write-Host "Installing CUDA PyTorch..."
uv pip install --python $Python --upgrade pip wheel setuptools
if ($LASTEXITCODE -ne 0) { throw "Failed to install pip tooling." }
uv pip install --python $Python torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cu121
if ($LASTEXITCODE -ne 0) { throw "Failed to install CUDA PyTorch." }

Write-Host "Installing Windows fairseq wheel..."
uv pip install --python $Python "https://github.com/BlueAmulet/fairseq-win-whl/releases/download/ci_build/fairseq-0.12.2-cp310-cp310-win_amd64.whl"
if ($LASTEXITCODE -ne 0) { throw "Failed to install fairseq Windows wheel." }

Write-Host "Installing RVC requirements..."
$FilteredRequirements = Join-Path (Split-Path $PSScriptRoot -Parent) "configs\rvc_requirements_no_fairseq.txt"
Get-Content (Join-Path $RepoDir "requirements.txt") |
    Where-Object { $_ -notmatch "^fairseq" } |
    Set-Content -Encoding utf8 $FilteredRequirements

uv pip install --python $Python -r $FilteredRequirements
if ($LASTEXITCODE -ne 0) { throw "Failed to install RVC requirements." }

Write-Host "Pinning RVC-compatible dependency versions..."
uv pip install --python $Python gradio_client==0.2.6 omegaconf==2.0.6 hydra-core==1.0.7 matplotlib==3.7.5
if ($LASTEXITCODE -ne 0) { throw "Failed to pin RVC-compatible dependencies." }

Write-Host "Installing ffmpeg binary..."
uv pip install --python $Python imageio-ffmpeg
if ($LASTEXITCODE -ne 0) { throw "Failed to install imageio-ffmpeg." }
$FfmpegSource = & $Python -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"
Copy-Item -Force $FfmpegSource (Join-Path $VenvDir "Scripts\ffmpeg.exe")
if (-not (Test-Path (Join-Path $VenvDir "Scripts\ffmpeg.exe"))) { throw "Failed to prepare ffmpeg.exe." }

Write-Host "Verifying CUDA..."
& $Python -c "import torch; print(torch.__version__); print('cuda=', torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu')"
if ($LASTEXITCODE -ne 0) { throw "CUDA verification failed." }

Write-Host "Verifying RVC imports..."
& $Python -c "import torch, fairseq, gradio, librosa, pyworld, faiss, soundfile; print('rvc_imports=ok')"
if ($LASTEXITCODE -ne 0) { throw "RVC import verification failed." }

Write-Host "Installing API runtime dependencies..."
$ApiRequirements = Join-Path $ProjectDir "requirements-api.txt"
uv pip install --python $Python -r $ApiRequirements
if ($LASTEXITCODE -ne 0) { throw "Failed to install API dependencies." }

Write-Host "Environment ready:"
Write-Host "  Repo: $RepoDir"
Write-Host "  Python: $Python"
Write-Host "Run the WebUI with:"
Write-Host "  & `"$Python`" `"$RepoDir\infer-web.py`""
