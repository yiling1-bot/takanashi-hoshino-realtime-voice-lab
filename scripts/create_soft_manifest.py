from __future__ import annotations

import argparse
import csv
from pathlib import Path


TARGET_FILES = {
    "hoshino_memoriallobby_0_new.ogg",
    "hoshino_memoriallobby_1_new.ogg",
    "hoshino_memoriallobby_2_new.ogg",
    "hoshino_memoriallobby_3_1_new.ogg",
    "hoshino_memoriallobby_3_2_new.ogg",
    "hoshino_memoriallobby_3_3_new.ogg",
}

SOFT_TAGS = [
    "memoriallobby",
    "lobby",
    "cafe",
    "relationship",
    "season_birthday",
    "season_newyear",
    "season_xmas",
    "season_halloween",
    "season_midautumn",
    "season_chinesenewyear",
]

HARD_TAGS = [
    "battle",
    "exskill",
    "commonskill",
    "tactic",
    "formation",
    "growup",
    "gachaget",
    "exweapon",
]


def row_weight(file_name: str, suggested_use: str, notes: str) -> int:
    name = file_name.lower()
    if any(tag in name for tag in HARD_TAGS):
        return 0
    if not any(tag in name for tag in SOFT_TAGS):
        return 0
    if suggested_use == "exclude":
        return 0
    if "older_variant_has_new_pair" in notes and "_new" not in name:
        return 0
    if file_name in TARGET_FILES:
        return 5
    if "memoriallobby" in name:
        return 4
    if "lobby" in name or "cafe" in name:
        return 3
    if "relationship" in name:
        return 2
    return 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    weighted_rows: list[dict[str, str]] = []
    with args.manifest.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        weight = row_weight(row["file_name"], row["suggested_use"], row["notes"])
        for copy_index in range(weight):
            duplicated = dict(row)
            duplicated["index"] = f'{row["index"]}_{copy_index + 1}'
            duplicated["suggested_use"] = "train"
            duplicated["soft_weight"] = str(weight)
            duplicated["file_name"] = f'{Path(row["file_name"]).stem}__soft{copy_index + 1}{Path(row["file_name"]).suffix}'
            weighted_rows.append(duplicated)

    if not weighted_rows:
        raise RuntimeError("No soft rows selected.")

    fieldnames = list(rows[0].keys())
    if "soft_weight" not in fieldnames:
        fieldnames.append("soft_weight")

    with args.output.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(weighted_rows)

    total = sum(float(row["duration_sec"]) for row in weighted_rows)
    print(f"soft_rows={len(weighted_rows)}")
    print(f"weighted_duration_sec={total:.3f}")
    print(f"output={args.output}")


if __name__ == "__main__":
    main()
