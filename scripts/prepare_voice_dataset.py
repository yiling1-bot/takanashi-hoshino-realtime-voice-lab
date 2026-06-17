from __future__ import annotations

import argparse
import csv
import math
import shutil
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly


def read_manifest(path: Path, include_review: bool) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            use = row["suggested_use"]
            if use == "train" or (include_review and use == "review"):
                rows.append(row)
    return rows


def to_mono(audio: np.ndarray) -> np.ndarray:
    if audio.ndim == 1:
        return audio.astype(np.float32)
    return np.mean(audio, axis=1).astype(np.float32)


def trim_silence(audio: np.ndarray, sample_rate: int, threshold_db: float, pad_ms: int) -> np.ndarray:
    if len(audio) == 0:
        return audio

    threshold = 10 ** (threshold_db / 20)
    abs_audio = np.abs(audio)
    active = np.flatnonzero(abs_audio >= threshold)
    if len(active) == 0:
        return audio

    pad = int(sample_rate * pad_ms / 1000)
    start = max(0, int(active[0]) - pad)
    end = min(len(audio), int(active[-1]) + pad)
    return audio[start:end]


def resample(audio: np.ndarray, old_sr: int, new_sr: int) -> np.ndarray:
    if old_sr == new_sr:
        return audio.astype(np.float32)
    gcd = math.gcd(old_sr, new_sr)
    up = new_sr // gcd
    down = old_sr // gcd
    return resample_poly(audio, up, down).astype(np.float32)


def normalize_peak(audio: np.ndarray, peak: float) -> np.ndarray:
    if len(audio) == 0:
        return audio
    current = float(np.max(np.abs(audio)))
    if current <= 0:
        return audio
    return np.clip(audio * (peak / current), -1.0, 1.0).astype(np.float32)


def safe_name(index: int, subset: str, file_name: str) -> str:
    stem = Path(file_name).stem
    subset_ascii = "swimsuit" if "swimsuit" in stem.lower() else "default"
    return f"{index:05d}_{subset_ascii}_{stem}.wav"


def prepare(args: argparse.Namespace) -> None:
    rows = read_manifest(args.manifest, args.include_review)
    wav_dir = args.output / "wavs"
    wav_dir.mkdir(parents=True, exist_ok=True)
    filelist_path = args.output / "rvc_filelist.txt"
    summary_path = args.output / "prepare_summary.csv"

    prepared: list[dict[str, str]] = []
    for idx, row in enumerate(rows, 1):
        source = Path(row["source_path"])
        audio, sr = sf.read(str(source), always_2d=False)
        mono = to_mono(audio)
        mono = trim_silence(mono, sr, args.trim_db, args.pad_ms)
        mono = resample(mono, sr, args.sample_rate)
        mono = normalize_peak(mono, args.peak)

        if len(mono) < int(args.min_sec * args.sample_rate):
            continue

        out_name = safe_name(idx, row["subset"], row["file_name"])
        out_path = wav_dir / out_name
        sf.write(str(out_path), mono, args.sample_rate, subtype="PCM_16")
        prepared.append(
            {
                "source_path": str(source),
                "wav_path": str(out_path),
                "duration_sec": f"{len(mono) / args.sample_rate:.3f}",
                "sample_rate": str(args.sample_rate),
                "original_duration_sec": row["duration_sec"],
                "suggested_use": row["suggested_use"],
                "notes": row["notes"],
            }
        )

    with filelist_path.open("w", encoding="utf-8", newline="\n") as f:
        for item in prepared:
            f.write(item["wav_path"] + "\n")

    with summary_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "source_path",
                "wav_path",
                "duration_sec",
                "sample_rate",
                "original_duration_sec",
                "suggested_use",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(prepared)

    total_sec = sum(float(item["duration_sec"]) for item in prepared)
    print(f"prepared_files={len(prepared)}")
    print(f"prepared_duration_sec={total_sec:.3f}")
    print(f"wav_dir={wav_dir}")
    print(f"filelist={filelist_path}")
    print(f"summary={summary_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--sample-rate", type=int, default=40000)
    parser.add_argument("--trim-db", type=float, default=-45.0)
    parser.add_argument("--pad-ms", type=int, default=80)
    parser.add_argument("--peak", type=float, default=0.95)
    parser.add_argument("--min-sec", type=float, default=1.0)
    parser.add_argument("--include-review", action="store_true")
    parser.set_defaults(func=prepare)
    args = parser.parse_args()

    if args.output.exists():
        shutil.rmtree(args.output)
    args.func(args)


if __name__ == "__main__":
    main()
