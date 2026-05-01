#!/usr/bin/env python3
"""Fix is_rahao in existing ksd_ang_json files.

Extends is_rahao backwards from the ਰਹਾਉ line to cover all lines
in the same rahao block (everything after the previous ॥N॥ stanza end).

Usage:
  python3 fix_rahao_blocks.py            # dry run — show counts only
  python3 fix_rahao_blocks.py --write    # apply fixes
  python3 fix_rahao_blocks.py --ang 262  # single ang
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

KSD_DIR = Path(__file__).parent / "ksd_ang_json"

_STANZA_END_RE = re.compile(r"[੦-੯]॥\s*$")


def expand_rahao_blocks(lines: list[dict]) -> int:
    changed = 0
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
            if not lines[k]["is_rahao"]:
                lines[k]["is_rahao"] = True
                changed += 1
    return changed


def fix_ang(path: Path, write: bool) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    total = 0
    for shabad in data.get("shabads", []):
        total += expand_rahao_blocks(shabad.get("lines", []))
    if total and write:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return total


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Apply fixes (default: dry run)")
    parser.add_argument("--ang", type=int, help="Fix a single ang")
    args = parser.parse_args()

    if args.ang:
        files = [KSD_DIR / f"ksd_ang_{args.ang:04d}.json"]
    else:
        files = sorted(KSD_DIR.glob("ksd_ang_*.json"))

    total_lines = 0
    total_angs = 0
    for f in files:
        n = fix_ang(f, args.write)
        if n:
            total_lines += n
            total_angs += 1
            print(f"  {f.name}: +{n} lines marked rahao")

    action = "Fixed" if args.write else "Would fix"
    print(f"{action} {total_lines} lines across {total_angs} angs")
    if not args.write and total_lines:
        print("Re-run with --write to apply.")


if __name__ == "__main__":
    main()
