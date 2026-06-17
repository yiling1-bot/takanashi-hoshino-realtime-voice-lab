from __future__ import annotations

import argparse
import csv
from pathlib import Path


DAILY_TAGS = [
    "cafe",
    "lobby",
    "login",
    "memoriallobby",
    "relationship",
    "season",
]

HARD_TAGS = [
    "alarms",
    "autopilot",
    "battle",
    "capture",
    "catfight",
    "commonskill",
    "consumable",
    "defeat",
    "defective",
    "destroy",
    "detection",
    "domination",
    "exskill",
    "exweapon",
    "fire_",
    "formation",
    "friendly",
    "gachaget",
    "growup",
    "hit_confirmation",
    "last_hope",
    "lets_battle",
    "pilots",
    "quick_commands",
    "ship_destroyed",
    "tactic",
    "torpedo",
    "victory",
]


def row_weight(file_name: str, duration_sec: float, suggested_use: str) -> int:
    name = file_name.lower()
    if suggested_use == "exclude":
        return 0
    if duration_sec < 1.0 or duration_sec > 15.0:
        return 0
    if any(tag in name for tag in HARD_TAGS):
        return 0
    if not any(tag in name for tag in DAILY_TAGS):
        return 0

    if "memoriallobby" in name:
        return 5
    if "cafe" in name:
        return 4
    if "lobby" in name:
        return 4
    if "relationship" in name:
        return 3
    if "season" in name:
        return 2
    if "login" in name:
        return 1
    return 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    with args.manifest.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise RuntimeError("Input manifest is empty.")

    weighted_rows: list[dict[str, str]] = []
    for row in rows:
        duration_sec = float(row["duration_sec"])
        weight = row_weight(row["file_name"], duration_sec, row["suggested_use"])
        for copy_index in range(weight):
            duplicated = dict(row)
            duplicated["index"] = f'{row["index"]}_{copy_index + 1}'
            duplicated["suggested_use"] = "train"
            duplicated["daily_weight"] = str(weight)
            stem = Path(row["file_name"]).stem
            suffix = Path(row["file_name"]).suffix
            duplicated["file_name"] = f"{stem}__daily{copy_index + 1}{suffix}"
            weighted_rows.append(duplicated)

    if not weighted_rows:
        raise RuntimeError("No daily rows selected.")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    if "daily_weight" not in fieldnames:
        fieldnames.append("daily_weight")

    with args.output.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(weighted_rows)

    total = sum(float(row["duration_sec"]) for row in weighted_rows)
    unique = {row["source_path"] for row in weighted_rows}
    print(f"daily_unique_files={len(unique)}")
    print(f"daily_weighted_rows={len(weighted_rows)}")
    print(f"daily_weighted_duration_sec={total:.3f}")
    print(f"output={args.output}")


if __name__ == "__main__":
    main()
