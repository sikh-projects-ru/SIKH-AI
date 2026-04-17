"""
lookup.py — утилиты поиска по локальной sggs.db

Использование:
    from banidb.lookup import SggsDB

    db = SggsDB()
    verses = db.get_ang(1136)
    for v in verses:
        print(v["gurmukhi"], "|", v["transliteration"])
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterator

DB_PATH = Path(__file__).parent / "sggs.db"


class SggsDB:
    def __init__(self, db_path: Path = DB_PATH) -> None:
        if not db_path.exists():
            raise FileNotFoundError(
                f"sggs.db не найдена: {db_path}\n"
                "Запусти: python banidb/fetch_sggs.py"
            )
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row

    def close(self) -> None:
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def get_ang(self, ang: int) -> list[dict]:
        """Все строки указанного ang'а, отсортированные по line_no."""
        rows = self._conn.execute(
            "SELECT * FROM verses WHERE ang=? ORDER BY line_no", (ang,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_shabad(self, shabad_id: int) -> list[dict]:
        """Все строки шабада по shabad_id."""
        rows = self._conn.execute(
            "SELECT * FROM verses WHERE shabad_id=? ORDER BY ang, line_no",
            (shabad_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def search_en(self, keyword: str, limit: int = 20) -> list[dict]:
        """Поиск по английскому переводу (LIKE)."""
        rows = self._conn.execute(
            "SELECT * FROM verses WHERE translation_en LIKE ? LIMIT ?",
            (f"%{keyword}%", limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def find_best_match(self, ang: int, keywords: list[str]) -> list[dict]:
        """
        Из ang'а выбирает строки, в английском переводе которых
        встречается больше всего ключевых слов.
        Возвращает топ-3 совпадения.
        """
        verses = self.get_ang(ang)
        scored = []
        kw_lower = [k.lower() for k in keywords]
        for v in verses:
            text = (v["translation_en"] or "").lower()
            score = sum(1 for k in kw_lower if k in text)
            if score > 0:
                scored.append((score, v))
        scored.sort(key=lambda x: -x[0])
        return [v for _, v in scored[:3]]

    def is_available(self, ang: int) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM verses WHERE ang=? LIMIT 1", (ang,)
        ).fetchone()
        return row is not None
