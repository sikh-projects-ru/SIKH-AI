#!/usr/bin/env python3
"""KSD translation coverage report.

Shows which angs/lines have KSD translations, which are empty,
and outputs a flagged-for-review list after knowledge base changes.

Usage:
  python3 ksd_coverage.py              # full coverage report
  python3 ksd_coverage.py --ang 1-13   # specific ang range
  python3 ksd_coverage.py --empty      # show only angs with gaps
  python3 ksd_coverage.py --review     # flag lines for re-translation
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

ROOT    = Path(__file__).parent
ANG_DIR = ROOT / "ksd_ang_json"
BANIDB  = ROOT.parent / "banidb" / "sggs.db"


def load_ang(ang: int) -> dict | None:
    path = ANG_DIR / f"ksd_ang_{ang:04d}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def ksd_main(line: dict) -> str:
    return line.get("translations", {}).get("ksd_ru", {}).get("main", "")


def coverage_for_ang(ang: int) -> dict:
    data = load_ang(ang)
    if data is None:
        return {"ang": ang, "status": "missing", "total": 0, "done": 0, "empty": 0}

    lines = [ln for sh in data.get("shabads", []) for ln in sh.get("lines", [])]
    done  = sum(1 for ln in lines if ksd_main(ln))
    empty = len(lines) - done
    if done == 0:
        status = "empty"
    elif empty == 0:
        status = "full"
    else:
        status = "partial"
    return {"ang": ang, "status": status, "total": len(lines), "done": done, "empty": empty}


def all_ksd_angs() -> list[int]:
    return sorted(
        int(p.stem.replace("ksd_ang_", ""))
        for p in ANG_DIR.glob("ksd_ang_*.json")
    )


def print_report(angs: list[int], show_empty_only: bool) -> None:
    total_lines = done_lines = 0
    rows = []
    for ang in angs:
        cov = coverage_for_ang(ang)
        total_lines += cov["total"]
        done_lines  += cov["done"]
        if show_empty_only and cov["status"] == "full":
            continue
        rows.append(cov)

    # Header
    print(f"\n{'Ang':>4}  {'Status':<8}  {'Done':>5}  {'Empty':>5}  {'Total':>5}")
    print("─" * 38)
    for r in rows:
        flag = "  ← нужен перевод" if r["status"] in ("empty", "partial") else ""
        print(f"{r['ang']:>4}  {r['status']:<8}  {r['done']:>5}  {r['empty']:>5}  {r['total']:>5}{flag}")

    pct = done_lines / total_lines * 100 if total_lines else 0
    print("─" * 38)
    print(f"Итого: {done_lines}/{total_lines} строк ({pct:.1f}%)")
    print(f"Файлов: {len(angs)} ангов в ksd_ang_json/\n")


def flag_for_review(angs: list[int]) -> None:
    """Print lines where ksd_ru.main is empty — candidates for (re-)translation."""
    if not BANIDB.exists():
        print("banidb/sggs.db not found — cannot look up gurmukhi for missing lines.")
        return

    conn  = sqlite3.connect(BANIDB)
    c     = conn.cursor()
    found = 0

    print("\n── Строки без KSD-перевода (кандидаты для перевода) ──\n")
    for ang in angs:
        data = load_ang(ang)
        if not data:
            continue
        for sh in data.get("shabads", []):
            for ln in sh.get("lines", []):
                if not ksd_main(ln):
                    vid = ln.get("verse_id")
                    c.execute("SELECT gurmukhi FROM verses WHERE verse_id=?", (vid,))
                    row = c.fetchone()
                    gurmukhi = row[0] if row else ln.get("gurmukhi", "")
                    print(f"  ang={ang} shabad={sh.get('shabad_id')} verse={vid}")
                    print(f"    {gurmukhi}")
                    found += 1
    conn.close()
    print(f"\nИтого без перевода: {found} строк")


def parse_ang_range(s: str) -> list[int]:
    """Parse '1-13' or '1,5,13' or '1' into list of ints."""
    result = []
    for part in s.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            result.extend(range(int(a), int(b) + 1))
        else:
            result.append(int(part))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ang",    help="Ang range: '1-13' or '1,5,13'")
    parser.add_argument("--empty",  action="store_true", help="Show only partial/empty angs")
    parser.add_argument("--review", action="store_true", help="List lines needing translation")
    args = parser.parse_args()

    if args.ang:
        angs = [a for a in parse_ang_range(args.ang) if (ANG_DIR / f"ksd_ang_{a:04d}.json").exists()]
    else:
        angs = all_ksd_angs()

    print_report(angs, show_empty_only=args.empty)

    if args.review:
        flag_for_review(angs)


if __name__ == "__main__":
    main()
