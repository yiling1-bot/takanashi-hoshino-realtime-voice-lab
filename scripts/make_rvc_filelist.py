from __future__ import annotations

import argparse
import json
import random
import shutil
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--exp", required=True)
    parser.add_argument("--sr", default="40k")
    parser.add_argument("--version", default="v2", choices=["v1", "v2"])
    parser.add_argument("--speaker-id", default="0")
    args = parser.parse_args()

    repo = args.repo
    exp_dir = repo / "logs" / args.exp
    gt_wavs_dir = exp_dir / "0_gt_wavs"
    f0_dir = exp_dir / "2a_f0"
    f0nsf_dir = exp_dir / "2b-f0nsf"
    feature_dir = exp_dir / ("3_feature256" if args.version == "v1" else "3_feature768")

    config_src = repo / "configs" / ("v1" if args.version == "v1" or args.sr == "40k" else "v2") / f"{args.sr}.json"
    config_dst = exp_dir / "config.json"
    if not config_src.exists():
        raise FileNotFoundError(config_src)
    shutil.copyfile(config_src, config_dst)

    names = (
        {p.stem for p in gt_wavs_dir.glob("*.wav")}
        & {p.stem for p in feature_dir.glob("*.npy")}
        & {p.name.removesuffix(".wav.npy") for p in f0_dir.glob("*.wav.npy")}
        & {p.name.removesuffix(".wav.npy") for p in f0nsf_dir.glob("*.wav.npy")}
    )
    if not names:
        raise RuntimeError("No matching gt wav / feature / f0 files found.")

    entries: list[str] = []
    for name in sorted(names):
        entries.append(
            "|".join(
                [
                    str(gt_wavs_dir / f"{name}.wav").replace("\\", "\\\\"),
                    str(feature_dir / f"{name}.npy").replace("\\", "\\\\"),
                    str(f0_dir / f"{name}.wav.npy").replace("\\", "\\\\"),
                    str(f0nsf_dir / f"{name}.wav.npy").replace("\\", "\\\\"),
                    args.speaker_id,
                ]
            )
        )

    mute = repo / "logs" / "mute"
    fea_dim = "256" if args.version == "v1" else "768"
    for _ in range(2):
        entries.append(
            "|".join(
                [
                    str(mute / "0_gt_wavs" / f"mute{args.sr}.wav").replace("\\", "\\\\"),
                    str(mute / f"3_feature{fea_dim}" / "mute.npy").replace("\\", "\\\\"),
                    str(mute / "2a_f0" / "mute.wav.npy").replace("\\", "\\\\"),
                    str(mute / "2b-f0nsf" / "mute.wav.npy").replace("\\", "\\\\"),
                    args.speaker_id,
                ]
            )
        )

    random.shuffle(entries)
    filelist = exp_dir / "filelist.txt"
    filelist.write_text("\n".join(entries), encoding="utf-8")

    meta = {
        "experiment": args.exp,
        "sample_rate": args.sr,
        "version": args.version,
        "entries": len(entries),
        "real_entries": len(names),
        "filelist": str(filelist),
        "config": str(config_dst),
    }
    (exp_dir / "filelist_meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(meta, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
