#!/usr/bin/env python3
"""Merge sahib_singh_ru translations from custom_khoj_sahib_singh into ksd_ang_json.

Reads ang_json/ang_XXXX.json (flat format, field: translation_ru) by verse_id,
fills translations.sahib_singh_ru.main in ksd_ang_json/ksd_ang_XXXX.json.

Default: dry run. Use --apply to write.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

KSD_DIR    = Path(__file__).parent / "ksd_ang_json"
SOURCE_DIR = Path(__file__).parent.parent / "custom_khoj_sahib_singh" / "ang_json"


def load_source_index(ang: int) -> dict[int, str]:
    path = SOURCE_DIR / f"ang_{ang:04d}.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {ln["verse_id"]: ln.get("translation_ru", "") for ln in data.get("lines", [])}


def merge_ang(ang: int, apply: bool) -> tuple[int, int]:
    ksd_path = KSD_DIR / f"ksd_ang_{ang:04d}.json"
    if not ksd_path.exists():
        return 0, 0

    source = load_source_index(ang)
    if not source:
        print(f"  ang {ang}: source not found, skipped")
        return 0, 0

    data = json.loads(ksd_path.read_text(encoding="utf-8"))
    filled = skipped = 0

    for sh in data.get("shabads", []):
        for ln in sh.get("lines", []):
            vid = ln.get("verse_id")
            tr = ln.setdefault("translations", {})
            slot = tr.setdefault("sahib_singh_ru", {"main": ""})
            ru = source.get(vid, "")
            if ru and not slot.get("main"):
                slot["main"] = ru
                filled += 1
            else:
                skipped += 1

    if apply and filled:
        ksd_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    return filled, skipped


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    ksd_angs = sorted(
        int(p.stem.replace("ksd_ang_", ""))
        for p in KSD_DIR.glob("ksd_ang_*.json")
    )

    total_filled = total_skipped = 0
    for ang in ksd_angs:
        filled, skipped = merge_ang(ang, args.apply)
        total_filled += filled
        total_skipped += skipped
        status = f"filled={filled}" if filled else "nothing new"
        print(f"  ang {ang:4d}: {status}")

    action = "Applied" if args.apply else "Dry run:"
    print(f"\n{action} {total_filled} lines merged, {total_skipped} already set or missing.")
    if not args.apply:
        print("Run with --apply to write.")


if __name__ == "__main__":
    main()
