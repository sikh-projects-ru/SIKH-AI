#!/usr/bin/env python3
"""Migrate ksd_ang_*.json to unified multi-translator format.

Line-level changes:
- Moves ksd_translation/artistic_ru/context_note/confidence/confidence_reason
  into translations.ksd_ru
- Moves sahib_singh_pa into translations.sahib_singh_pa.main
- Adds empty slots: translations.sahib_singh_ru, translations.ipotseluev_ru
- Removes: word_analysis, roman_display (dropped)
- Applies romanization rules (dulavan ai→ē, final sihari drop, final onkar drop)
- Field order: verse_id, is_rahao, gurmukhi, roman, translations

Shabad-level: keeps shabad_id, rahao_verse_id, rahao_theme, shabad_summary.
Drops shabad-level 'ang' (redundant with top-level ang).

Default: dry run. Use --apply to write.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
ANG_DIR = ROOT / "ksd_ang_json"
FIX_SCRIPT = ROOT.parent / "custom_khoj_sahib_singh" / "fix_romanization_rules.py"

sys.path.insert(0, str(FIX_SCRIPT.parent))
from fix_romanization_rules import fix_roman_line  # noqa: E402

SHABAD_KEEP = {"shabad_id", "rahao_verse_id", "rahao_theme", "shabad_summary"}

EMPTY_TRANSLATORS = ["sahib_singh_ru", "ipotseluev_ru"]


def migrate_line(line: dict) -> tuple[dict, bool]:
    gurmukhi = str(line.get("gurmukhi", ""))
    roman_orig = str(line.get("roman", ""))
    roman_fixed, _ = fix_roman_line(gurmukhi, roman_orig)

    ksd_ru: dict = {
        "main": line.get("ksd_translation", ""),
        "artistic": line.get("artistic_ru", ""),
        "context_note": line.get("context_note", ""),
    }
    conf = line.get("confidence")
    conf_reason = line.get("confidence_reason", "")
    if conf is not None:
        ksd_ru["confidence"] = conf
    if conf_reason:
        ksd_ru["confidence_reason"] = conf_reason

    translations: dict = {
        "ksd_ru": ksd_ru,
        "sahib_singh_pa": {"main": line.get("sahib_singh_pa", "")},
    }
    for tid in EMPTY_TRANSLATORS:
        translations[tid] = {"main": ""}

    out = {
        "verse_id": line["verse_id"],
        "is_rahao": bool(line.get("is_rahao", False)),
        "gurmukhi": gurmukhi,
        "roman": roman_fixed,
        "translations": translations,
    }

    # Detect if anything actually changed vs current state
    already_migrated = "translations" in line and "ksd_ru" in line.get("translations", {})
    changed = not already_migrated or roman_orig != roman_fixed
    return out, changed


def migrate_shabad(shabad: dict) -> tuple[dict, int]:
    lines_changed = 0
    new_lines = []
    for ln in shabad.get("lines", []):
        new_ln, changed = migrate_line(ln)
        new_lines.append(new_ln)
        if changed:
            lines_changed += 1

    out = {k: shabad[k] for k in SHABAD_KEEP if k in shabad}
    out["lines"] = new_lines
    return out, lines_changed


def migrate_file(path: Path, apply: bool) -> tuple[int, int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    total_changed = 0
    new_shabads = []
    for sh in data.get("shabads", []):
        new_sh, changed = migrate_shabad(sh)
        new_shabads.append(new_sh)
        total_changed += changed

    new_data = {"ang": data["ang"], "shabads": new_shabads}
    total_lines = sum(len(sh.get("lines", [])) for sh in data.get("shabads", []))

    if apply:
        path.write_text(
            json.dumps(new_data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return total_changed, total_lines


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Write changes")
    parser.add_argument("--ang", type=int, help="Migrate single ang only")
    args = parser.parse_args()

    if args.ang:
        paths = [ANG_DIR / f"ksd_ang_{args.ang:04d}.json"]
    else:
        paths = sorted(ANG_DIR.glob("ksd_ang_*.json"))

    total_files = 0
    total_changed = 0
    total_lines = 0
    for path in paths:
        if not path.exists():
            print(f"  MISSING: {path.name}")
            continue
        changed, lines = migrate_file(path, args.apply)
        total_changed += changed
        total_lines += lines
        print(f"  {path.name}: {'CHANGED' if changed else 'ok'} ({changed}/{lines})")
        total_files += 1

    action = "Applied" if args.apply else "Dry run:"
    print(f"\n{action} {total_files} files, {total_changed}/{total_lines} lines.")
    if not args.apply:
        print("Run with --apply to write changes.")


if __name__ == "__main__":
    main()
