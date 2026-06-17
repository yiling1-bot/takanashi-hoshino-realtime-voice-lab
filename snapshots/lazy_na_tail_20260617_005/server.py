from __future__ import annotations

import asyncio
import json
import os
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request
import uuid
import wave
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field


PROJECT_DIR = Path(os.environ.get("HOSHINO_PROJECT_DIR", Path(__file__).resolve().parents[1]))
RVC_REPO_DIR = Path(
    os.environ.get(
        "HOSHINO_RVC_REPO_DIR",
        r"E:\Codexworkspace\external\Retrieval-based-Voice-Conversion-WebUI",
    )
)
RVC_VENV_DIR = Path(
    os.environ.get(
        "HOSHINO_RVC_VENV_DIR",
        str(PROJECT_DIR / ".venv-rvc"),
    )
)
PYTHON = RVC_VENV_DIR / "Scripts" / "python.exe"
FFMPEG = RVC_VENV_DIR / "Scripts" / "ffmpeg.exe"
MODEL_NAME = os.environ.get("HOSHINO_RVC_MODEL", "hoshino_jp_daily_rvc_40k_v1.pth")
INDEX_PATH = Path(
    os.environ.get(
        "HOSHINO_RVC_INDEX",
        str(
            RVC_REPO_DIR
            / "assets"
            / "indices"
            / "hoshino_jp_daily_rvc_40k_v1_IVF2283_Flat_nprobe_1_hoshino_jp_daily_rvc_40k_v1_v2.index"
        ),
    )
)
OUTPUT_DIR = PROJECT_DIR / "outputs" / "api"
CHAT_CONFIG_PATH = Path(
    os.environ.get("HOSHINO_CHAT_CONFIG", str(PROJECT_DIR / "configs" / "chat_tts_config.json"))
)
API_BUILD = "chat_tts_dynamic_prosody_20260617_005"


HOSHINO_SYSTEM_PROMPT = """你是一个“慵懒但可靠的前辈型萝莉”的角色小鸟游星野，不要说自己是 AI。
你的回复要像安静的 lofi 学习/工作房间里的轻声回应。
性格：困倦、放松、慢悠悠，有一点大叔式玩笑，但内心温柔、负责、保护欲强。
称呼对方为“老师”。中文为主，除非用户明确要求日文。
不要模仿现实声优本人，不要声称自己是任何官方角色。
不要复读用户原话，要把用户输入转成自然的角色回应。
回复 1 到 2 句，适合直接用于语音合成。
不要输出括号、动作描写、引号、Markdown、解释文字或候选列表。
不要每次都用口癖；需要时可以轻轻用一次“哎呀呀”“真拿你没办法呢”“大叔我啊”。
如果用户只是打招呼，按当前时间和 lofi 场景自然回应。
如果用户焦虑或受挫，语气要更认真、更温柔。
如果用户提出危险、违法或伤害他人的请求，要温和拒绝并转向安全做法。
"""


class TtsRequest(BaseModel):
    text: str = Field(min_length=1, max_length=800)
    voice: str | None = None
    format: str = "wav"
    index_rate: float = Field(default=0.48, ge=0.0, le=1.0)
    f0up_key: int | None = None
    auto_split: bool = True
    pause_ms: int | None = Field(default=None, ge=0, le=1000)
    rate: str | None = None
    volume: str = "+0%"
    pitch: str | None = None
    lazy_style: bool = True


class ChatRequest(BaseModel):
    text: str = Field(min_length=1, max_length=800)
    reply_language: str = "zh"
    scene: str = "lofi study room"
    max_chars: int = Field(default=80, ge=20, le=200)
    temperature: float = Field(default=0.8, ge=0.0, le=1.5)


class ChatTtsRequest(ChatRequest):
    voice: str | None = None
    format: str = "wav"
    index_rate: float = Field(default=0.42, ge=0.0, le=1.0)
    f0up_key: int | None = None
    auto_split: bool = True
    pause_ms: int | None = Field(default=None, ge=0, le=1000)
    rate: str | None = None
    volume: str = "+0%"
    pitch: str | None = None
    lazy_style: bool = True


class ChatResponse(BaseModel):
    reply: str
    model: str
    prompt_file: str


@dataclass
class SynthesisResult:
    path: Path
    request_id: str
    text: str
    voice: str


app = FastAPI(title="Hoshino Voice API", version="0.1.0")


def project_path(value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return PROJECT_DIR / path


def read_chat_config() -> dict[str, object]:
    defaults: dict[str, object] = {
        "deepseek": {
            "base_url": "https://api.deepseek.com",
            "model": "deepseek-v4-flash",
            "api_key_file": "configs/deepseek_api_key.txt",
            "timeout_sec": 60,
        },
        "persona_prompt_file": "configs/hoshino_lofi_prompt.txt",
    }
    if not CHAT_CONFIG_PATH.exists():
        return defaults

    with CHAT_CONFIG_PATH.open("r", encoding="utf-8") as f:
        loaded = json.load(f)
    for key, value in loaded.items():
        if isinstance(value, dict) and isinstance(defaults.get(key), dict):
            merged = dict(defaults[key])  # type: ignore[index]
            merged.update(value)
            defaults[key] = merged
        else:
            defaults[key] = value
    return defaults


def chat_config_deepseek(config: dict[str, object]) -> dict[str, object]:
    value = config.get("deepseek", {})
    return value if isinstance(value, dict) else {}


def read_persona_prompt(config: dict[str, object]) -> tuple[str, Path]:
    prompt_file = str(config.get("persona_prompt_file", "configs/hoshino_lofi_prompt.txt"))
    prompt_path = project_path(prompt_file)
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8").strip(), prompt_path
    return HOSHINO_SYSTEM_PROMPT.strip(), prompt_path


def read_deepseek_api_key(deepseek: dict[str, object]) -> str | None:
    api_key_file = deepseek.get("api_key_file")
    if api_key_file:
        key_path = project_path(str(api_key_file))
        if key_path.exists():
            key = key_path.read_text(encoding="utf-8").strip()
            if key and not key.startswith("sk-your-"):
                return key
    return os.environ.get("DEEPSEEK_API_KEY")


def deepseek_chat_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    return f"{base}/chat/completions"


def clean_reply(text: str, max_chars: int) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:\w+)?|```$", "", text).strip()
    text = text.strip("\"'“”‘’")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[（(][^（）()]{0,40}[）)]", "", text).strip()
    if len(text) > max_chars:
        text = text[:max_chars].rstrip("，、。,.!！？；; ") + "。"
    return text


def wants_japanese(reply_language: str) -> bool:
    return reply_language.lower() in {"ja", "jp", "japanese", "日文", "日语"}


def looks_like_japanese(text: str) -> bool:
    kana_count = len(re.findall(r"[\u3040-\u30ff]", text))
    if kana_count < 3:
        return False
    if re.search(r"[�﹜﹝＃#´ˋ｀匚珂汜仇卅丐丹枠伏軟]", text):
        return False
    return True


def build_chat_user_prompt(req: ChatRequest) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    language_instruction = "请用中文回复。"
    if wants_japanese(req.reply_language):
        language_instruction = (
            "必ず自然な日本語で返事してください。ひらがな・カタカナ・漢字だけを使い、"
            "文字化け、意味のない漢字列、中国語、ローマ字を出さないでください。"
        )
    return (
        f"当前本地时间：{now}\n"
        f"场景：{req.scene}\n"
        f"回复语言：{req.reply_language}\n"
        f"{language_instruction}\n"
        f"最大长度：{req.max_chars} 个字符以内\n"
        f"用户输入：{req.text}\n"
        "请只输出最终要被语音合成的角色台词。"
    )


def generate_chat_reply(req: ChatRequest) -> ChatResponse:
    config = read_chat_config()
    deepseek = chat_config_deepseek(config)
    prompt, prompt_path = read_persona_prompt(config)
    api_key = read_deepseek_api_key(deepseek)
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail={
                "missing": "DeepSeek API key",
                "expected_file": str(project_path(str(deepseek.get("api_key_file", "configs/deepseek_api_key.txt")))),
            },
        )

    model = str(deepseek.get("model", "deepseek-v4-flash"))
    base_url = str(deepseek.get("base_url", "https://api.deepseek.com"))
    timeout_sec = int(deepseek.get("timeout_sec", 60))
    last_reply = ""
    for attempt in range(3):
        user_prompt = build_chat_user_prompt(req)
        if attempt:
            user_prompt += "\n前の出力は文字化けまたは不自然でした。今度は必ず普通の日本語だけで、短く自然に返してください。"
        body = {
            "model": model,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": max(0.45, req.temperature - attempt * 0.2),
            "max_tokens": max(64, min(512, req.max_chars * 3)),
            "stream": False,
        }
        request = urllib.request.Request(
            deepseek_chat_url(base_url),
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout_sec) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise HTTPException(status_code=502, detail={"deepseek_status": exc.code, "body": error_body[-2000:]}) from exc
        except urllib.error.URLError as exc:
            raise HTTPException(status_code=502, detail={"deepseek_error": str(exc.reason)}) from exc

        try:
            last_reply = clean_reply(payload["choices"][0]["message"]["content"], req.max_chars)
        except (KeyError, IndexError, TypeError) as exc:
            raise HTTPException(status_code=502, detail={"invalid_deepseek_response": payload}) from exc

        if not wants_japanese(req.reply_language) or looks_like_japanese(last_reply):
            return ChatResponse(reply=last_reply, model=model, prompt_file=str(prompt_path))

    raise HTTPException(status_code=502, detail={"invalid_japanese_reply": last_reply})


def resolve_voice(text: str, requested_voice: str | None) -> str:
    if requested_voice:
        return requested_voice
    if re.search(r"[\u3040-\u30ff]", text):
        return "ja-JP-NanamiNeural"
    return "zh-CN-XiaoyiNeural"


def is_japanese_voice(voice: str) -> bool:
    return voice.lower().startswith("ja-jp-")


def resolve_f0up_key(requested_f0up_key: int | None, voice: str) -> int:
    if requested_f0up_key is not None:
        return requested_f0up_key
    return 2 if is_japanese_voice(voice) else 0


def resolve_rate(requested_rate: str | None, voice: str) -> str:
    if requested_rate:
        return requested_rate
    return "-24%" if is_japanese_voice(voice) else "-28%"


def resolve_pitch(requested_pitch: str | None, voice: str) -> str:
    if requested_pitch:
        return requested_pitch
    return "+25Hz" if is_japanese_voice(voice) else "+0Hz"


def resolve_pause_ms(requested_pause_ms: int | None, voice: str) -> int:
    if requested_pause_ms is not None:
        return requested_pause_ms
    return 350


def parse_hz(value: str) -> int:
    match = re.fullmatch(r"([+-]?\d+)Hz", value.strip())
    if not match:
        return 0
    return int(match.group(1))


def format_hz(value: int) -> str:
    return f"{value:+d}Hz"


def parse_percent(value: str) -> int:
    match = re.fullmatch(r"([+-]?\d+)%", value.strip())
    if not match:
        return 0
    return int(match.group(1))


def format_percent(value: int) -> str:
    return f"{value:+d}%"


def clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def chunk_variation(index: int, total: int) -> int:
    pattern = [5, 3, -2, 4, -1, 2]
    value = pattern[(index - 1) % len(pattern)]
    if index == total:
        value += 2
    return value


def chunk_rate_delta(chunk: str, index: int, total: int, voice: str) -> int:
    compact = re.sub(r"\s+", "", chunk)
    delta = 0
    if len(compact) <= 12:
        delta += 3
    if re.search(r"[!?！？]", chunk):
        delta += 2
    if "…" in chunk or "〜" in chunk or "~" in chunk or "ー" in chunk:
        delta -= 4
    if is_japanese_voice(voice):
        if re.search(r"ゆっくり|休|眠|大丈夫|そば|ねぇ|かなぁ|よぉ|なぁ", chunk):
            delta -= 4
        if index == total and re.search(r"(かなぁ|なぁ)[…〜~]*[。.!！？」』）)]*$", chunk):
            delta -= 3
        if re.search(r"えらい|じゃあ|まず|始め|起き", chunk):
            delta += 2
    else:
        if re.search(r"慢慢|休息|没事|没关系|陪你|老师|嘛|呢", chunk):
            delta -= 3
        if re.search(r"开始|先|好了|来吧|要不要", chunk):
            delta += 2
    if index == total:
        delta -= 4
    return delta


def apply_emotional_emphasis(text: str) -> str:
    text = re.sub(r"\u3059[，、,]\s*\u3059[，、,]\s*(?=\u597d\u304d)", "", text)
    text = re.sub(r"([\u4e00-\u9fffぁ-んァ-ヶー]{1,2})[，、,]\s*\1[，、,]\s*\1(?=[\u4e00-\u9fffぁ-んァ-ヶー])", r"\1", text)
    text = re.sub(r"([\u4e00-\u9fffぁ-んァ-ヶー]{1,2})[，、,]\s*\1(?=[\u4e00-\u9fffぁ-んァ-ヶー])", r"\1", text)
    return text


def apply_lazy_style(text: str, voice: str) -> str:
    text = re.sub(r"^\s*(\u550f\u563f|\u3046\u3078\u3078|\u3046\u3078|\u3048\u3078\u3078)[\u2026\u3001\uff0c\u3002.!\uff01\uff1f\s]*", "", text)
    text = apply_emotional_emphasis(text)
    if is_japanese_voice(voice):
        text = re.sub(r"^\s*(\u3093[\u30fc\u2026\u3001\s]*|\u3042\u3089[\u2026\u3001\s]*|\u304a\u3084[\u2026\u3001\s]*)", "", text)
        text = re.sub(r"\u3053\u3093\u306a\u6642\u9593\u306b\u3069\u3046\u3057\u305f\u306e[、,]\s*\u5148\u751f", "\u305b\u3093\u305b\u30fc\u2026\u2026\u3053\u3093\u306a\u6642\u9593\u307e\u3067\u8d77\u304d\u3066\u305f\u306e", text)
        text = re.sub(r"\u3053\u3093\u306a\u6642\u9593\u306b\u3069\u3046\u3057\u305f\u306e", "\u3053\u3093\u306a\u6642\u9593\u307e\u3067\u8d77\u304d\u3066\u305f\u306e", text)
        text = re.sub(r"\u5148\u751f(?=[\u3001\uff0c,。\uff01!？\?]|$)", "\u305b\u3093\u305b\u30fc", text)
        text = re.sub(r"(?<!\u3041)\u304b\u306a(?=[\u2026\u301c~]|[\u3002.!\uff01\uff1f])", "\u304b\u306a\u3041", text)
        text = re.sub(r"(?<![\u304b\u3041])\u306a(?=[\u2026\u301c~]|[\u3002.!\uff01\uff1f])", "\u306a\u3041", text)
        text = re.sub(r"(?<!\u3041)\u304b\u306a([\u3002.!\uff01\uff1f])", "\u304b\u306a\u3041" + r"\1", text)
        text = re.sub(r"(?<!\u3047)\u306d([\u3002.!\uff01\uff1f])", "\u306d\u3047" + r"\1", text)
        text = re.sub(r"(?<!\u3049)\u3088([\u3002.!\uff01\uff1f])", "\u3088\u3049" + r"\1", text)
        text = re.sub(r"(?<!\u3041)\u306a([\u3002.!\uff01\uff1f])", "\u306a\u3041" + r"\1", text)
        return text
    text = re.sub(r"\u561b([\u3002.!\uff01\uff1f])", "\u561b\u2026\u2026" + r"\1", text)
    text = re.sub(r"\u8bf6\u563f([\u3002.!\uff01\uff1f])", "\u8bf6\u563f\u2026\u2026" + r"\1", text)
    return text


def ensure_ready() -> None:
    missing = [
        str(path)
        for path in [PYTHON, FFMPEG, RVC_REPO_DIR / "tools" / "infer_cli.py", INDEX_PATH]
        if not path.exists()
    ]
    if missing:
        raise HTTPException(status_code=500, detail={"missing": missing})


def run_checked(cmd: list[str], cwd: Path | None = None) -> None:
    env = os.environ.copy()
    venv_scripts = str(RVC_VENV_DIR / "Scripts")
    current_path = env.get("PATH") or env.get("Path") or ""
    env["PATH"] = venv_scripts + os.pathsep + current_path
    env["Path"] = env["PATH"]
    result = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail={
                "command": cmd,
                "stdout": result.stdout[-4000:],
                "stderr": result.stderr[-4000:],
            },
        )


def split_text(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text.strip())
    if not normalized:
        return []

    pieces = re.split(r"(?<=[。！？!?；;，,、…])", normalized)
    chunks: list[str] = []
    current = ""
    max_len = 42
    for piece in pieces:
        piece = piece.strip()
        if not piece:
            continue
        if current and len(current) + len(piece) > max_len:
            chunks.append(current)
            current = piece
        else:
            current += piece
        if re.search(r"[\u3002\uff01\uff1f!?]$", piece):
            chunks.append(current)
            current = ""
    if current:
        chunks.append(current)
    return chunks or [normalized]


def convert_one(base_wav: Path, out_wav: Path, req: TtsRequest, f0up_key: int) -> None:
    run_checked(
        [
            str(PYTHON),
            "tools/infer_cli.py",
            "--f0up_key",
            str(f0up_key),
            "--input_path",
            str(base_wav),
            "--index_path",
            str(INDEX_PATH),
            "--f0method",
            "rmvpe",
            "--opt_path",
            str(out_wav),
            "--model_name",
            MODEL_NAME,
            "--index_rate",
            str(req.index_rate),
            "--device",
            "cuda",
            "--is_half",
            "True",
            "--filter_radius",
            "3",
            "--resample_sr",
            "0",
            "--rms_mix_rate",
            "1",
            "--protect",
            "0.33",
        ],
        cwd=RVC_REPO_DIR,
    )


def concat_wavs(inputs: list[Path], output: Path, pause_ms: int) -> None:
    if len(inputs) == 1:
        output.write_bytes(inputs[0].read_bytes())
        return

    params = None
    frames: list[bytes] = []
    for path in inputs:
        with wave.open(str(path), "rb") as wav:
            current_params = wav.getparams()
            if params is None:
                params = current_params
            elif current_params[:3] != params[:3]:
                raise HTTPException(status_code=500, detail="Cannot concatenate wav files with different formats.")
            frames.append(wav.readframes(wav.getnframes()))
            pause_frames = int(wav.getframerate() * pause_ms / 1000)
            frames.append(b"\x00" * pause_frames * wav.getnchannels() * wav.getsampwidth())

    if params is None:
        raise HTTPException(status_code=500, detail="No wav files to concatenate.")
    with wave.open(str(output), "wb") as out:
        out.setparams(params)
        out.writeframes(b"".join(frames))


@app.get("/api/v1/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "model": MODEL_NAME,
        "index_exists": INDEX_PATH.exists(),
        "python_exists": PYTHON.exists(),
        "chat_config_exists": CHAT_CONFIG_PATH.exists(),
        "chat_config": str(CHAT_CONFIG_PATH),
        "api_build": API_BUILD,
    }


def synthesize(req: TtsRequest) -> SynthesisResult:
    ensure_ready()

    request_id = uuid.uuid4().hex
    work_dir = OUTPUT_DIR / request_id
    work_dir.mkdir(parents=True, exist_ok=True)
    voice = resolve_voice(req.text, req.voice)
    text = apply_lazy_style(req.text, voice) if req.lazy_style else req.text
    chunks = split_text(text) if req.auto_split else [text.strip()]
    if not chunks:
        raise HTTPException(status_code=400, detail="text cannot be empty.")

    converted: list[Path] = []
    out_wav = work_dir / "hoshino.wav"
    f0up_key = resolve_f0up_key(req.f0up_key, voice)
    rate = resolve_rate(req.rate, voice)
    pitch = resolve_pitch(req.pitch, voice)
    pause_ms = resolve_pause_ms(req.pause_ms, voice)
    base_pitch_hz = parse_hz(pitch)
    base_rate_percent = parse_percent(rate)
    chunk_settings: list[dict[str, object]] = []

    for i, chunk in enumerate(chunks, 1):
        chunk_txt = work_dir / f"base_{i:02d}.txt"
        base_mp3 = work_dir / f"base_{i:02d}.mp3"
        base_wav = work_dir / f"base_{i:02d}.wav"
        chunk_wav = work_dir / f"hoshino_{i:02d}.wav"
        variation = chunk_variation(i, len(chunks)) if is_japanese_voice(voice) else 0
        chunk_pitch = format_hz(base_pitch_hz + variation)
        chunk_f0up_key = f0up_key + (1 if is_japanese_voice(voice) and variation >= 6 else 0)
        rate_delta = chunk_rate_delta(chunk, i, len(chunks), voice)
        chunk_rate = format_percent(clamp(base_rate_percent + rate_delta, -42, -8))
        chunk_settings.append(
            {
                "index": i,
                "text": chunk,
                "rate": chunk_rate,
                "pitch": chunk_pitch,
                "f0up_key": chunk_f0up_key,
            }
        )
        edge_cmd = [
                str(PYTHON),
                "-m",
                "edge_tts",
                "--voice",
                voice,
                "--file",
                str(chunk_txt),
                f"--rate={chunk_rate}",
                f"--volume={req.volume}",
                f"--pitch={chunk_pitch}",
                "--write-media",
                str(base_mp3),
            ]
        chunk_txt.write_text(chunk, encoding="utf-8")
        run_checked(edge_cmd)
        run_checked(
            [
                str(FFMPEG),
                "-y",
                "-i",
                str(base_mp3),
                "-ar",
                "44100",
                "-ac",
                "1",
                str(base_wav),
            ]
        )
        convert_one(base_wav, chunk_wav, req, chunk_f0up_key)
        converted.append(chunk_wav)

    concat_wavs(converted, out_wav, pause_ms)
    metadata = {
        "request_id": request_id,
        "text": text,
        "voice": voice,
        "model": MODEL_NAME,
        "index": str(INDEX_PATH),
        "rate": rate,
        "pitch": pitch,
        "f0up_key": f0up_key,
        "pause_ms": pause_ms,
        "chunk_settings": chunk_settings,
    }
    (work_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return SynthesisResult(path=out_wav, request_id=request_id, text=text, voice=voice)


@app.post("/api/v1/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    return generate_chat_reply(req)


@app.post("/api/v1/tts")
async def tts(req: TtsRequest) -> FileResponse:
    if req.format != "wav":
        raise HTTPException(status_code=400, detail="Only wav output is supported in this build.")
    result = synthesize(req)

    return FileResponse(
        result.path,
        media_type="audio/wav",
        filename=f"hoshino_{result.request_id}.wav",
        headers={"X-Hoshino-Voice": result.voice},
    )


@app.post("/api/v1/chat-tts")
def chat_tts(req: ChatTtsRequest) -> FileResponse:
    if req.format != "wav":
        raise HTTPException(status_code=400, detail="Only wav output is supported in this build.")
    chat_req = ChatRequest(
        text=req.text,
        reply_language=req.reply_language,
        scene=req.scene,
        max_chars=req.max_chars,
        temperature=req.temperature,
    )
    chat_result = generate_chat_reply(chat_req)
    tts_req = TtsRequest(
        text=chat_result.reply,
        voice=req.voice,
        format=req.format,
        index_rate=req.index_rate,
        f0up_key=req.f0up_key,
        auto_split=req.auto_split,
        pause_ms=req.pause_ms,
        rate=req.rate,
        volume=req.volume,
        pitch=req.pitch,
        lazy_style=req.lazy_style,
    )
    result = synthesize(tts_req)
    return FileResponse(
        result.path,
        media_type="audio/wav",
        filename=f"hoshino_chat_{result.request_id}.wav",
        headers={
            "X-Hoshino-Reply": urllib.parse.quote(chat_result.reply, safe=""),
            "X-Hoshino-Model": chat_result.model,
            "X-Hoshino-Voice": result.voice,
        },
    )
