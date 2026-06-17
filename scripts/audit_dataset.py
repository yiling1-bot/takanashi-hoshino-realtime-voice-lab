from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

import soundfile as sf


AUDIO_EXTS = {".wav", ".flac", ".ogg", ".mp3", ".m4a"}


@dataclass
class AudioRow:
    index: int
    source_path: Path
    subset: str
    file_name: str
    ext: str
    duration_sec: float
    sample_rate: int
    channels: int
    frames: int
    size_bytes: int
    suggested_use: str
    notes: str


def classify(path: Path, duration_sec: float) -> tuple[str, str]:
    name = path.stem.lower()
    short_tags = [
        "battle_damage",
        "battle_shout",
        "battle_move",
        "battle_buff",
        "battle_recovery",
        "battle_defense",
        "commonskill",
    ]
    if duration_sec < 1.0:
        return "exclude", "too_short"
    if any(tag in name for tag in short_tags) and duration_sec < 2.0:
        return "exclude", "short_battle_effort"
    if duration_sec > 15.0:
        return "review", "long_clip"
    if "_new" not in name and (path.with_name(path.stem + "_new" + path.suffix)).exists():
        return "review", "older_variant_has_new_pair"
    return "train", "ok"


def read_audio(path: Path) -> tuple[float, int, int, int]:
    info = sf.info(str(path))
    duration = float(info.frames) / float(info.samplerate) if info.samplerate else 0.0
    return duration, int(info.samplerate), int(info.channels), int(info.frames)


def collect_rows(input_dir: Path) -> list[AudioRow]:
    files = sorted(
        p for p in input_dir.rglob("*") if p.is_file() and p.suffix.lower() in AUDIO_EXTS
    )
    rows: list[AudioRow] = []
    for i, path in enumerate(files, 1):
        try:
            duration, sample_rate, channels, frames = read_audio(path)
            suggested_use, notes = classify(path, duration)
        except Exception as exc:  # noqa: BLE001 - audit should report bad files, not stop.
            duration, sample_rate, channels, frames = 0.0, 0, 0, 0
            suggested_use, notes = "exclude", f"read_error:{exc}"

        try:
            subset = path.relative_to(input_dir).parts[0]
        except Exception:
            subset = ""

        rows.append(
            AudioRow(
                index=i,
                source_path=path,
                subset=subset,
                file_name=path.name,
                ext=path.suffix.lower(),
                duration_sec=duration,
                sample_rate=sample_rate,
                channels=channels,
                frames=frames,
                size_bytes=path.stat().st_size,
                suggested_use=suggested_use,
                notes=notes,
            )
        )
    return rows


def write_manifest(rows: list[AudioRow], output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "index",
                "source_path",
                "subset",
                "file_name",
                "ext",
                "duration_sec",
                "sample_rate",
                "channels",
                "frames",
                "size_bytes",
                "suggested_use",
                "notes",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "index": row.index,
                    "source_path": str(row.source_path),
                    "subset": row.subset,
                    "file_name": row.file_name,
                    "ext": row.ext,
                    "duration_sec": f"{row.duration_sec:.3f}",
                    "sample_rate": row.sample_rate,
                    "channels": row.channels,
                    "frames": row.frames,
                    "size_bytes": row.size_bytes,
                    "suggested_use": row.suggested_use,
                    "notes": row.notes,
                }
            )


def fmt_time(seconds: float) -> str:
    minutes = int(seconds // 60)
    secs = seconds - minutes * 60
    return f"{minutes}m {secs:.1f}s"


def write_report(rows: list[AudioRow], output_md: Path, input_dir: Path) -> None:
    output_md.parent.mkdir(parents=True, exist_ok=True)
    total = sum(r.duration_sec for r in rows)
    train = [r for r in rows if r.suggested_use == "train"]
    review = [r for r in rows if r.suggested_use == "review"]
    exclude = [r for r in rows if r.suggested_use == "exclude"]
    subset_names = sorted({r.subset for r in rows})

    by_subset: list[str] = []
    for subset in subset_names:
        subset_rows = [r for r in rows if r.subset == subset]
        subset_train = [r for r in subset_rows if r.suggested_use == "train"]
        by_subset.append(
            "| "
            + " | ".join(
                [
                    subset,
                    str(len(subset_rows)),
                    fmt_time(sum(r.duration_sec for r in subset_rows)),
                    str(len(subset_train)),
                    fmt_time(sum(r.duration_sec for r in subset_train)),
                ]
            )
            + " |"
        )

    sample_rates = sorted({r.sample_rate for r in rows if r.sample_rate})
    channels = sorted({r.channels for r in rows if r.channels})

    lines = [
        "# Dataset Audit Report",
        "",
        f"- Source: `{input_dir}`",
        f"- Files: {len(rows)}",
        f"- Total duration: {fmt_time(total)}",
        f"- Train-suggested duration: {fmt_time(sum(r.duration_sec for r in train))}",
        f"- Review duration: {fmt_time(sum(r.duration_sec for r in review))}",
        f"- Excluded duration: {fmt_time(sum(r.duration_sec for r in exclude))}",
        f"- Sample rates: {', '.join(str(x) for x in sample_rates) or 'n/a'}",
        f"- Channels: {', '.join(str(x) for x in channels) or 'n/a'}",
        "",
        "## Subsets",
        "",
        "| Subset | Files | Total | Train Files | Train Duration |",
        "| --- | ---: | ---: | ---: | ---: |",
        *by_subset,
        "",
        "## Recommendation",
        "",
    ]

    train_seconds = sum(r.duration_sec for r in train)
    if train_seconds >= 10 * 60:
        lines.extend(
            [
                "- Enough clean-looking audio for direct TTS fine-tuning if transcripts are available.",
                "- Without transcripts, use RVC/SVC-style voice conversion first.",
            ]
        )
    elif train_seconds >= 3 * 60:
        lines.extend(
            [
                "- Enough audio for a first voice-conversion demo.",
                "- Direct TTS fine-tuning is possible only if transcripts are accurate, but quality may be limited.",
            ]
        )
    else:
        lines.extend(
            [
                "- Dataset is small. Prefer zero-shot/few-shot testing or voice conversion.",
                "- Avoid long full training runs until more clean clips or transcripts are available.",
            ]
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- `train` is an automatic suggestion based on file name and duration only.",
            "- Manual listening is still required before final training.",
            "- Files marked `review` may still be useful after deduplication or transcript matching.",
        ]
    )

    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()

    rows = collect_rows(args.input)
    write_manifest(rows, args.manifest)
    write_report(rows, args.report, args.input)
    print(f"files={len(rows)}")
    print(f"duration_sec={sum(r.duration_sec for r in rows):.3f}")
    print(f"train_duration_sec={sum(r.duration_sec for r in rows if r.suggested_use == 'train'):.3f}")
    print(f"manifest={args.manifest}")
    print(f"report={args.report}")


if __name__ == "__main__":
    main()
