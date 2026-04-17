#!/usr/bin/env python3
"""
fetch_sggs.py — скачивает все 1430 ang'ов СГГС из BaniDB API
и сохраняет в локальную SQLite базу sggs.db

Использование:
    python fetch_sggs.py              # скачать всё (1–1430)
    python fetch_sggs.py --start 500  # продолжить с ang 500
    python fetch_sggs.py --ang 1136   # обновить один ang
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import time
import urllib.request
from pathlib import Path

DB_PATH = Path(__file__).parent / "sggs.db"
API_BASE = "https://api.banidb.com/v2"
TOTAL_ANGS = 1430
DELAY_S = 0.3  # пауза между запросами


# ── Schema ────────────────────────────────────────────────────────────────────

DDL = """
CREATE TABLE IF NOT EXISTS verses (
    verse_id        INTEGER PRIMARY KEY,
    shabad_id       INTEGER NOT NULL,
    ang             INTEGER NOT NULL,
    line_no         INTEGER NOT NULL,
    gurmukhi        TEXT,
    transliteration TEXT,
    translation_en  TEXT,
    translation_pu  TEXT,
    writer_en       TEXT,
    raag_en         TEXT
);
CREATE INDEX IF NOT EXISTS idx_verses_ang ON verses(ang);
CREATE INDEX IF NOT EXISTS idx_verses_shabad ON verses(shabad_id);
"""


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(DDL)
    conn.commit()


# ── API ───────────────────────────────────────────────────────────────────────

def fetch_ang(ang: int) -> list[dict]:
    url = f"{API_BASE}/angs/{ang}"
    req = urllib.request.Request(url, headers={"Accept": "application/json",
                                               "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read())
    return data.get("page", [])


def verse_to_row(v: dict) -> tuple:
    tr = v.get("transliteration") or {}
    en_tr = tr.get("en") or tr.get("english") or ""

    trans = v.get("translation") or {}
    en = trans.get("en") or {}
    en_text = en.get("bdb") or en.get("ms") or en.get("ssk") or ""

    pu = trans.get("pu") or {}
    ss = pu.get("ss") or {}
    pu_text = (ss.get("unicode") or "").strip()

    writer = (v.get("writer") or {}).get("english") or ""
    raag   = (v.get("raag")   or {}).get("english") or ""

    verse = v.get("verse") or {}
    gurmukhi = (verse.get("unicode") or "").strip()

    return (
        v["verseId"],
        v["shabadId"],
        v["pageNo"],
        v["lineNo"],
        gurmukhi,
        en_tr,
        en_text,
        pu_text,
        writer,
        raag,
    )


# ── Download ──────────────────────────────────────────────────────────────────

def already_downloaded(conn: sqlite3.Connection, ang: int) -> bool:
    row = conn.execute("SELECT 1 FROM verses WHERE ang=? LIMIT 1", (ang,)).fetchone()
    return row is not None


def download_ang(conn: sqlite3.Connection, ang: int, force: bool = False) -> int:
    if not force and already_downloaded(conn, ang):
        return 0

    verses = fetch_ang(ang)
    if not verses:
        return 0

    conn.execute("DELETE FROM verses WHERE ang=?", (ang,))
    rows = [verse_to_row(v) for v in verses]
    conn.executemany(
        "INSERT OR REPLACE INTO verses VALUES (?,?,?,?,?,?,?,?,?,?)", rows
    )
    conn.commit()
    return len(rows)


def download_range(start: int, end: int, force: bool = False) -> None:
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    done = conn.execute("SELECT COUNT(DISTINCT ang) FROM verses").fetchone()[0]
    print(f"База: {DB_PATH.name}  |  уже загружено ang'ов: {done}")

    for ang in range(start, end + 1):
        if not force and already_downloaded(conn, ang):
            print(f"  [skip] ang {ang}", end="\r")
            continue

        try:
            n = download_ang(conn, ang, force=force)
            pct = (ang - start + 1) / (end - start + 1) * 100
            print(f"  ang {ang:4d}  {n:3d} строк  [{pct:5.1f}%]")
        except Exception as e:
            print(f"  [err]  ang {ang}: {e}")

        time.sleep(DELAY_S)

    total = conn.execute("SELECT COUNT(DISTINCT ang) FROM verses").fetchone()[0]
    verses = conn.execute("SELECT COUNT(*) FROM verses").fetchone()[0]
    print(f"\nГотово. Ang'ов: {total}, строк: {verses}")
    conn.close()


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end",   type=int, default=TOTAL_ANGS)
    parser.add_argument("--ang",   type=int, help="Загрузить один ang")
    parser.add_argument("--force", action="store_true", help="Перезаписать уже скачанные")
    parser.add_argument("--status", action="store_true", help="Показать статус БД")
    args = parser.parse_args()

    if args.status:
        if not DB_PATH.exists():
            print("sggs.db не найдена. Запусти fetch_sggs.py для загрузки.")
            return
        conn = sqlite3.connect(DB_PATH)
        total_angs = conn.execute("SELECT COUNT(DISTINCT ang) FROM verses").fetchone()[0]
        total_verses = conn.execute("SELECT COUNT(*) FROM verses").fetchone()[0]
        missing = [a for a in range(1, TOTAL_ANGS+1)
                   if not conn.execute("SELECT 1 FROM verses WHERE ang=?", (a,)).fetchone()]
        conn.close()
        print(f"sggs.db: {total_angs}/{TOTAL_ANGS} ang'ов, {total_verses} строк")
        if missing:
            print(f"Пропущено: {missing[:20]}{'...' if len(missing)>20 else ''}")
        return

    if args.ang:
        conn = sqlite3.connect(DB_PATH)
        init_db(conn)
        n = download_ang(conn, args.ang, force=True)
        print(f"ang {args.ang}: {n} строк сохранено")
        conn.close()
        return

    download_range(args.start, min(args.end, TOTAL_ANGS), force=args.force)


if __name__ == "__main__":
    main()
