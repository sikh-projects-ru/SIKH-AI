#!/usr/bin/env python3
"""
ksd_backup_db.py

Создаёт SQL-дамп ksd_knowledge.db → ksd_knowledge_dump.sql
Дамп версионируется в git и читаем как текст.
Также экспортирует JSON-снапшоты ключевых таблиц.

Использование:
  python3 ksd_backup_db.py           # сделать дамп
  python3 ksd_backup_db.py --restore # восстановить из дампа
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DB_PATH    = SCRIPT_DIR / "ksd_knowledge.db"
DUMP_SQL   = SCRIPT_DIR / "ksd_knowledge_dump.sql"
DUMP_JSON  = SCRIPT_DIR / "ksd_knowledge_snapshot.json"


def backup():
    if not DB_PATH.exists():
        print(f"ERROR: {DB_PATH} не найдена")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))

    # SQL-дамп
    with open(DUMP_SQL, "w", encoding="utf-8") as f:
        for line in conn.iterdump():
            f.write(line + "\n")

    # JSON-снапшот (ключевые таблицы)
    cur = conn.cursor()
    snapshot = {}

    # Слова — только с ksd_meta_ru непустым
    cur.execute("""
        SELECT roman, literal_ru, ksd_meta_ru, confidence, grammar_note, source
        FROM words WHERE ksd_meta_ru != '' ORDER BY roman
    """)
    snapshot["words"] = [
        {"roman": r[0], "literal_ru": r[1], "ksd_meta_ru": r[2],
         "confidence": r[3], "grammar_note": r[4], "source": r[5]}
        for r in cur.fetchall()
    ]

    # Концепты
    cur.execute("SELECT concept, ksd_meaning, source FROM canvas_concepts ORDER BY concept")
    snapshot["canvas_concepts"] = [
        {"concept": r[0], "ksd_meaning": r[1][:300], "source": r[2]}
        for r in cur.fetchall()
    ]

    # Принципы
    cur.execute("SELECT num, title, description FROM ksd_principles ORDER BY num")
    snapshot["ksd_principles"] = [
        {"num": r[0], "title": r[1], "description": r[2][:400]}
        for r in cur.fetchall()
    ]

    # Грамматика
    cur.execute("SELECT pattern, meaning, source FROM grammar_rules ORDER BY pattern")
    snapshot["grammar_rules"] = [
        {"pattern": r[0], "meaning": r[1], "source": r[2]}
        for r in cur.fetchall()
    ]

    # Статистика
    for tbl in ["words", "canvas_concepts", "ksd_principles", "grammar_rules", "ksd_examples"]:
        cur.execute(f"SELECT COUNT(*) FROM {tbl}")
        snapshot.setdefault("_stats", {})[tbl] = cur.fetchone()[0]

    with open(DUMP_JSON, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    conn.close()

    print(f"SQL дамп: {DUMP_SQL} ({DUMP_SQL.stat().st_size // 1024} KB)")
    print(f"JSON snap: {DUMP_JSON} ({DUMP_JSON.stat().st_size // 1024} KB)")
    print(f"Статистика: {snapshot.get('_stats', {})}")


def restore():
    if not DUMP_SQL.exists():
        print(f"ERROR: {DUMP_SQL} не найден")
        sys.exit(1)

    if DB_PATH.exists():
        backup_path = DB_PATH.with_suffix(".db.bak")
        import shutil
        shutil.copy2(DB_PATH, backup_path)
        print(f"Старая БД скопирована в {backup_path}")
        DB_PATH.unlink()

    conn = sqlite3.connect(str(DB_PATH))
    sql = DUMP_SQL.read_text(encoding="utf-8")
    conn.executescript(sql)
    conn.close()
    print(f"БД восстановлена из {DUMP_SQL}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--restore", action="store_true", help="Восстановить из дампа")
    args = parser.parse_args()
    if args.restore:
        restore()
    else:
        backup()


if __name__ == "__main__":
    main()
