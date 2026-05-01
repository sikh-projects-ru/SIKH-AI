#!/usr/bin/env python3
"""Create ksd_ang_json files for new angs using custom_khoj_sahib_singh as the structural base.

Reads custom_khoj_sahib_singh/ang_json/ang_XXXX.json (flat, read-only),
writes ksd_ang_json/ksd_ang_XXXX.json in the unified shabads[] format with
multi-translator slots.

If ksd_ang_XXXX.json already exists, skips it (preserves existing ksd_ru translations).
Use --force to overwrite (CAUTION: will erase existing ksd_ru content).

Usage:
  python3 expand_ksd_angs.py --ang 14
  python3 expand_ksd_angs.py --ang 14-100
  python3 expand_ksd_angs.py --ang 14,50,100
  python3 expand_ksd_angs.py --all          # all angs present in source but missing in ksd_ang_json
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT       = Path(__file__).parent
KSD_DIR    = ROOT / "ksd_ang_json"
SOURCE_DIR = ROOT.parent / "custom_khoj_sahib_singh" / "ang_json"
BANIDB     = ROOT.parent / "banidb" / "sggs.db"
FIX_SCRIPT = ROOT.parent / "custom_khoj_sahib_singh" / "fix_romanization_rules.py"

sys.path.insert(0, str(FIX_SCRIPT.parent))
from fix_romanization_rules import fix_roman_line  # noqa: E402

EMPTY_KSD  = {"main": "", "artistic": "", "context_note": ""}
EMPTY_SLOT = {"main": ""}

# Matches lines that close a numbered stanza: ends with ॥੧॥, ॥੨॥, etc.
_STANZA_END_RE = re.compile(r"[੦-੯]॥\s*$")


def normalize_source_value(value: object) -> str:
    if value is None or value == "None":
        return ""
    return str(value)


def build_line(src: dict) -> dict:
    gurmukhi = normalize_source_value(src.get("gurmukhi", ""))
    roman, _ = fix_roman_line(gurmukhi, normalize_source_value(src.get("roman", "")))

    return {
        "verse_id": src["verse_id"],
        "is_rahao": "ਰਹਾਉ" in gurmukhi,
        "gurmukhi": gurmukhi,
        "roman":    roman,
        "translations": {
            "ksd_ru":         dict(EMPTY_KSD),
            "sahib_singh_pa": {"main": normalize_source_value(src.get("sahib_singh_pa", ""))},
            "sahib_singh_ru": {"main": normalize_source_value(src.get("translation_ru", ""))},
            "ipotseluev_ru":  dict(EMPTY_SLOT),
        },
    }


def load_shabad_map(ang: int) -> dict[int, int]:
    if not BANIDB.exists():
        raise FileNotFoundError(f"BaniDB not found: {BANIDB}")

    conn = sqlite3.connect(BANIDB)
    try:
        rows = conn.execute(
            "SELECT verse_id, shabad_id FROM verses WHERE ang=? ORDER BY verse_id",
            (ang,),
        ).fetchall()
    finally:
        conn.close()

    return {verse_id: shabad_id for verse_id, shabad_id in rows}


def expand_rahao_blocks(lines: list[dict]) -> None:
    """Extend is_rahao backwards to cover the full rahao block (in-place).

    A rahao block = every line from just after the previous stanza-end marker
    (a line whose gurmukhi ends with ॥N॥) up to and including the line that
    contains ਰਹਾਉ. There can be multiple rahao blocks in one shabad.
    """
    for i, line in enumerate(lines):
        if not line.get("is_rahao"):
            continue
        j = i - 1
        while j >= 0:
            if _STANZA_END_RE.search(lines[j]["gurmukhi"]):
                j += 1
                break
            j -= 1
        else:
            j = 0
        for k in range(j, i):
            lines[k]["is_rahao"] = True


def group_lines(ang: int, lines: list[dict]) -> list[dict]:
    shabad_by_verse = load_shabad_map(ang)
    grouped: dict[int, dict] = {}

    for line in lines:
        verse_id = line["verse_id"]
        shabad_id = shabad_by_verse.get(verse_id)
        if shabad_id is None:
            raise KeyError(f"Missing shabad_id for ang {ang}, verse_id {verse_id}")

        shabad = grouped.setdefault(
            shabad_id,
            {
                "shabad_id": shabad_id,
                "rahao_verse_id": None,
                "rahao_theme": "",
                "shabad_summary": "",
                "lines": [],
            },
        )
        shabad["lines"].append(line)

    for shabad in grouped.values():
        expand_rahao_blocks(shabad["lines"])
        for line in shabad["lines"]:
            if line.get("is_rahao") and shabad["rahao_verse_id"] is None:
                shabad["rahao_verse_id"] = line["verse_id"]

    return list(grouped.values())


def expand_ang(ang: int, force: bool) -> str:
    src_path = SOURCE_DIR / f"ang_{ang:04d}.json"
    dst_path = KSD_DIR    / f"ksd_ang_{ang:04d}.json"

    if not src_path.exists():
        return "no source"
    if dst_path.exists() and not force:
        return "exists (skipped)"

    src = json.loads(src_path.read_text(encoding="utf-8"))
    lines = [build_line(ln) for ln in src.get("lines", [])]
    shabads = group_lines(ang, lines)
    out = {"ang": ang, "shabads": shabads}
    dst_path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return f"created ({len(shabads)} shabads, {len(lines)} lines)"


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
