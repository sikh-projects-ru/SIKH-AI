#!/usr/bin/env python3
"""Create ksd_ang_json files for new angs using custom_khoj_sahib_singh as the structural base.

Reads custom_khoj_sahib_singh/ang_json/ang_XXXX.json (flat, read-only),
writes ksd_ang_json/ksd_ang_XXXX.json with multi-translator slots.

If ksd_ang_XXXX.json already exists, skips it (preserves existing ksd_ru translations).
Use --force to overwrite (CAUTION: will erase existing ksd_ru content).

TODO: shabad_id enrichment per line from sggs_meta/shabad_index.json

Usage:
  python3 expand_ksd_angs.py --ang 14
  python3 expand_ksd_angs.py --ang 14-100
  python3 expand_ksd_angs.py --ang 14,50,100
  python3 expand_ksd_angs.py --all          # all angs present in source but missing in ksd_ang_json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT       = Path(__file__).parent
KSD_DIR    = ROOT / "ksd_ang_json"
SOURCE_DIR = ROOT.parent / "custom_khoj_sahib_singh" / "ang_json"

EMPTY_KSD  = {"main": "", "artistic": "", "context_note": ""}
EMPTY_SLOT = {"main": ""}


def build_line(src: dict) -> dict:
    return {
        "verse_id": src["verse_id"],
        "gurmukhi": src.get("gurmukhi", ""),
        "roman":    src.get("roman", ""),
        "translations": {
            "ksd_ru":         dict(EMPTY_KSD),
            "sahib_singh_pa": {"main": src.get("sahib_singh_pa", "")},
            "sahib_singh_ru": {"main": src.get("translation_ru", "")},
            "ipotseluev_ru":  dict(EMPTY_SLOT),
        },
    }


def expand_ang(ang: int, force: bool) -> str:
    src_path = SOURCE_DIR / f"ang_{ang:04d}.json"
    dst_path = KSD_DIR    / f"ksd_ang_{ang:04d}.json"

    if not src_path.exists():
        return "no source"
    if dst_path.exists() and not force:
        return "exists (skipped)"

    src = json.loads(src_path.read_text(encoding="utf-8"))
    lines = [build_line(ln) for ln in src.get("lines", [])]
    out = {"ang": ang, "lines": lines}
    dst_path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return f"created ({len(lines)} lines)"


def parse_ang_range(s: str) -> list[int]:
    result = []
    for part in s.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            result.extend(range(int(a), int(b) + 1))
        else:
            result.append(int(part))
    return result


def all_missing_angs() -> list[int]:
    existing = {
        int(p.stem.replace("ksd_ang_", ""))
        for p in KSD_DIR.glob("ksd_ang_*.json")
    }
    available = {
        int(p.stem.replace("ang_", ""))
        for p in SOURCE_DIR.glob("ang_*.json")
    }
    return sorted(available - existing)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--ang",  help="Ang range: '14' or '14-100' or '14,50,100'")
    group.add_argument("--all",  action="store_true", help="All angs missing from ksd_ang_json")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    angs = parse_ang_range(args.ang) if args.ang else all_missing_angs()

    for ang in angs:
        result = expand_ang(ang, args.force)
        print(f"  ang {ang:4d}: {result}")

    print(f"\nDone. Processed {len(angs)} angs.")


if __name__ == "__main__":
    main()
