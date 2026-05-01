#!/usr/bin/env python3
"""Build SGGS metadata JSON from banidb/sggs.db.

Generates sggs_meta/authors.json, sggs_meta/raags.json, sggs_meta/shabad_index.json.
"""
from __future__ import annotations
import json
import re
import sqlite3
from pathlib import Path

BANIDB = Path(__file__).parent.parent / "banidb" / "sggs.db"
OUT = Path(__file__).parent / "sggs_meta"

# ── Author mapping ────────────────────────────────────────────────────────────

AUTHOR_META = {
    "Guru Nanak Dev Ji":        {"id": "m1",              "type": "mahalla", "mahalla": 1, "name_ru": "Гуру Нанак",        "name_gu": "ਮਹਲਾ ੧"},
    "Guru Angad Dev Ji":        {"id": "m2",              "type": "mahalla", "mahalla": 2, "name_ru": "Гуру Ангад",         "name_gu": "ਮਹਲਾ ੨"},
    "Guru Amar Daas Ji":        {"id": "m3",              "type": "mahalla", "mahalla": 3, "name_ru": "Гуру Амардас",       "name_gu": "ਮਹਲਾ ੩"},
    "Guru Raam Daas Ji":        {"id": "m4",              "type": "mahalla", "mahalla": 4, "name_ru": "Гуру Рам Дас",       "name_gu": "ਮਹਲਾ ੪"},
    "Guru Arjan Dev Ji":        {"id": "m5",              "type": "mahalla", "mahalla": 5, "name_ru": "Гуру Арджан",        "name_gu": "ਮਹਲਾ ੫"},
    "Guru Tegh Bahaadur Ji":    {"id": "m9",              "type": "mahalla", "mahalla": 9, "name_ru": "Гуру Тег Бахадур",   "name_gu": "ਮਹਲਾ ੯"},
    "Bhagat Kabeer Ji":         {"id": "kabir",           "type": "bhagat",  "mahalla": None, "name_ru": "Кабир",           "name_gu": "ਕਬੀਰ"},
    "Bhagat Ravi Daas Ji":      {"id": "ravidas",         "type": "bhagat",  "mahalla": None, "name_ru": "Равидас",         "name_gu": "ਰਵਿਦਾਸ"},
    "Bhagat Naam Dev Ji":       {"id": "namdev",          "type": "bhagat",  "mahalla": None, "name_ru": "Намдев",          "name_gu": "ਨਾਮਦੇਉ"},
    "Bhagat Trilochan Ji":      {"id": "trilochan",       "type": "bhagat",  "mahalla": None, "name_ru": "Трилочан",        "name_gu": "ਤ੍ਰਿਲੋਚਨ"},
    "Bhagat Sheikh Fareed Ji":  {"id": "farid",           "type": "bhagat",  "mahalla": None, "name_ru": "Фарид",           "name_gu": "ਫਰੀਦ"},
    "Bhagat Beni Ji":           {"id": "beni",            "type": "bhagat",  "mahalla": None, "name_ru": "Бени",            "name_gu": "ਬੇਣੀ"},
    "Bhagat Jaidev Ji":         {"id": "jaidev",          "type": "bhagat",  "mahalla": None, "name_ru": "Джайдев",         "name_gu": "ਜੈਦੇਉ"},
    "Bhagat Raamaanand Ji":     {"id": "ramanand",        "type": "bhagat",  "mahalla": None, "name_ru": "Раманандан",      "name_gu": "ਰਾਮਾਨੰਦ"},
    "Bhagat Dhannaa Ji":        {"id": "dhanna",          "type": "bhagat",  "mahalla": None, "name_ru": "Дханна",          "name_gu": "ਧੰਨਾ"},
    "Bhagat Peepaa Ji":         {"id": "pipa",            "type": "bhagat",  "mahalla": None, "name_ru": "Пипа",            "name_gu": "ਪੀਪਾ"},
    "Bhagat Sain Ji":           {"id": "sain",            "type": "bhagat",  "mahalla": None, "name_ru": "Саин",            "name_gu": "ਸੈਣੁ"},
    "Bhagat Bheekhan Ji":       {"id": "bhikhan",         "type": "bhagat",  "mahalla": None, "name_ru": "Бхикхан",         "name_gu": "ਭੀਖਨ"},
    "Bhagat Parmaanand Ji":     {"id": "parmanand",       "type": "bhagat",  "mahalla": None, "name_ru": "Парманандан",     "name_gu": "ਪਰਮਾਨੰਦ"},
    "Bhagat Saadhnaa Ji":       {"id": "sadhna",          "type": "bhagat",  "mahalla": None, "name_ru": "Садхна",          "name_gu": "ਸਧਨਾ"},
    "Bhagat Surdaas Ji":        {"id": "surdas",          "type": "bhagat",  "mahalla": None, "name_ru": "Сурдас",          "name_gu": "ਸੂਰਦਾਸ"},
    "Bhai Mardana":             {"id": "mardana",         "type": "other",   "mahalla": None, "name_ru": "Бхаи Марданa",    "name_gu": "ਮਰਦਾਨਾ"},
    "Bhatt (Baba) Sundar":      {"id": "sundar",          "type": "bhatt",   "mahalla": None, "name_ru": "Сундар",          "name_gu": "ਸੁੰਦਰ"},
    "Bhatt Bal":                {"id": "bhatt_bal",       "type": "bhatt",   "mahalla": None, "name_ru": "Бхатт Бал",       "name_gu": "ਬਲ੍ਹ"},
    "Bhatt Bhikhaa":            {"id": "bhatt_bhikha",    "type": "bhatt",   "mahalla": None, "name_ru": "Бхатт Бхикха",    "name_gu": "ਭਿੱਖਾ"},
    "Bhatt Gayandh":            {"id": "bhatt_gyand",     "type": "bhatt",   "mahalla": None, "name_ru": "Бхатт Гьянд",     "name_gu": "ਗਯੰਦ"},
    "Bhatt Harbans":            {"id": "bhatt_harbans",   "type": "bhatt",   "mahalla": None, "name_ru": "Бхатт Харбанс",   "name_gu": "ਹਰਬੰਸ"},
    "Bhatt Jal Jaalap":         {"id": "bhatt_jal",       "type": "bhatt",   "mahalla": None, "name_ru": "Бхатт Джал",      "name_gu": "ਜਲਾਪ"},
    "Bhatt Kal":                {"id": "bhatt_kal",       "type": "bhatt",   "mahalla": None, "name_ru": "Бхатт Кал",       "name_gu": "ਕਲ੍ਹ"},
    "Bhatt Kall Sahaar":        {"id": "bhatt_kalsahar",  "type": "bhatt",   "mahalla": None, "name_ru": "Бхатт Калсахар",  "name_gu": "ਕਲਸਹਾਰ"},
    "Bhatt Keerath ":           {"id": "bhatt_kirat",     "type": "bhatt",   "mahalla": None, "name_ru": "Бхатт Кират",     "name_gu": "ਕੀਰਤ"},
    "Bhatt Mathuraa":           {"id": "bhatt_mathura",   "type": "bhatt",   "mahalla": None, "name_ru": "Бхатт Матхура",   "name_gu": "ਮਥੁਰਾ"},
    "Bhatt Nal":                {"id": "bhatt_nal",       "type": "bhatt",   "mahalla": None, "name_ru": "Бхатт Нал",       "name_gu": "ਨਲ੍ਹ"},
    "Bhatt Sal":                {"id": "bhatt_sal",       "type": "bhatt",   "mahalla": None, "name_ru": "Бхатт Сал",       "name_gu": "ਸਲ੍ਹ"},
    "Bhatt Sathaa & Balvand":   {"id": "satta_balvand",   "type": "bhatt",   "mahalla": None, "name_ru": "Сатта и Балванд", "name_gu": "ਸੱਤਾ ਬਲਵੰਡ"},
    "Bhatt Tal":                {"id": "bhatt_tal",       "type": "bhatt",   "mahalla": None, "name_ru": "Бхатт Тал",       "name_gu": "ਤਲ੍ਹ"},
}

RAAG_RU = {
    "Jap":                    "Джап",
    "So Dar":                 "Со Дар",
    "So Purakh":              "Со Пуркх",
    "Sohila":                 "Сохила",
    "Siree Raag":             "Сири Раг",
    "Raag Maajh":             "Раг Маджх",
    "Raag Gauree":            "Раг Гауре",
    "Raag Aasaa":             "Раг Аса",
    "Raag Gujri":             "Раг Гуджри",
    "Raag Dayv Gandhaaree":   "Раг Дев Гандхари",
    "Raag Bihaagraa":         "Раг Бихагра",
    "Raag Vadhans":           "Раг Вадханс",
    "Raag Sorath":            "Раг Сорат",
    "Raag Dhanaasree":        "Раг Дханасри",
    "Raag Jaithsree":         "Раг Джайтсри",
    "Raag Todee":             "Раг Тоди",
    "Raag Baihaaree":         "Раг Байхари",
    "Raag Tilang":            "Раг Тиланг",
    "Raag Soohee":            "Раг Сухи",
    "Raag Bilaaval":          "Раг Билавал",
    "Raag Gond":              "Раг Гонд",
    "Raag Raamkalee":         "Раг Рамкали",
    "Raag Nat Naaraayan":     "Раг Нат Нараян",
    "Raag Maalee Gauraa":     "Раг Мали Гаура",
    "Raag Maaroo":            "Раг Мару",
    "Raag Tukhaari":          "Раг Тукхари",
    "Raag Kaydaaraa":         "Раг Кедара",
    "Raag Bhairao":           "Раг Бхайро",
    "Raag Basant":            "Раг Басант",
    "Raag Saarang":           "Раг Саранг",
    "Raag Malaar":            "Раг Малар",
    "Raag Kaanraa":           "Раг Канра",
    "Raag Kalyaan":           "Раг Калян",
    "Raag Prabhaatee":        "Раг Прабхати",
    "Raag Jaijaavantee":      "Раг Джайджавантэ",
    "Salok Sehskritee":       "Шлок Санскрит",
    "Fifth Mehl, Gaathaa":    "Гатха, Махла 5",
    "Phunhay Fifth Mehl":     "Пхунхэ, Махла 5",
    "Chaubolas Fifth Mehl":   "Чаубола, Махла 5",
    "Salok Kabeer Jee":       "Шлок Кабира",
    "Salok Fareed Jee":       "Шлок Фарида",
    "Svaiyay Mehl 5":         "Свайе, Махла 5",
    "Salok Vaaraan Thay Vadheek": "Шлок, Вааран тхэ вадхик",
    "Salok Mehl 9":           "Шлок, Махла 9",
    "Mundhaavanee Fifth Mehl":"Мундхавани, Махла 5",
    "Raag Maalaa":            "Раг Мала",
}

RAAG_GU = {
    "Jap": "ਜਪੁ", "So Dar": "ਸੋ ਦਰੁ", "So Purakh": "ਸੋ ਪੁਰਖੁ", "Sohila": "ਸੋਹਿਲਾ",
    "Siree Raag": "ਸਿਰੀ ਰਾਗੁ", "Raag Maajh": "ਰਾਗੁ ਮਾਝ", "Raag Gauree": "ਰਾਗੁ ਗਉੜੀ",
    "Raag Aasaa": "ਰਾਗੁ ਆਸਾ", "Raag Gujri": "ਰਾਗੁ ਗੂਜਰੀ", "Raag Dayv Gandhaaree": "ਰਾਗੁ ਦੇਵਗੰਧਾਰੀ",
    "Raag Bihaagraa": "ਰਾਗੁ ਬਿਹਾਗੜਾ", "Raag Vadhans": "ਰਾਗੁ ਵਡਹੰਸੁ", "Raag Sorath": "ਰਾਗੁ ਸੋਰਠਿ",
    "Raag Dhanaasree": "ਰਾਗੁ ਧਨਾਸਰੀ", "Raag Jaithsree": "ਰਾਗੁ ਜੈਤਸਰੀ", "Raag Todee": "ਰਾਗੁ ਟੋਡੀ",
    "Raag Baihaaree": "ਰਾਗੁ ਬੈਹਾਗੜਾ", "Raag Tilang": "ਰਾਗੁ ਤਿਲੰਗ", "Raag Soohee": "ਰਾਗੁ ਸੂਹੀ",
    "Raag Bilaaval": "ਰਾਗੁ ਬਿਲਾਵਲੁ", "Raag Gond": "ਰਾਗੁ ਗੋਂਡ", "Raag Raamkalee": "ਰਾਗੁ ਰਾਮਕਲੀ",
    "Raag Nat Naaraayan": "ਰਾਗੁ ਨਟ ਨਾਰਾਇਨ", "Raag Maalee Gauraa": "ਰਾਗੁ ਮਾਲੀ ਗਉੜਾ",
    "Raag Maaroo": "ਰਾਗੁ ਮਾਰੂ", "Raag Tukhaari": "ਰਾਗੁ ਤੁਖਾਰੀ", "Raag Kaydaaraa": "ਰਾਗੁ ਕੇਦਾਰਾ",
    "Raag Bhairao": "ਰਾਗੁ ਭੈਰਉ", "Raag Basant": "ਰਾਗੁ ਬਸੰਤੁ", "Raag Saarang": "ਰਾਗੁ ਸਾਰੰਗ",
    "Raag Malaar": "ਰਾਗੁ ਮਲਾਰ", "Raag Kaanraa": "ਰਾਗੁ ਕਾਨੜਾ", "Raag Kalyaan": "ਰਾਗੁ ਕਲਿਆਨ",
    "Raag Prabhaatee": "ਰਾਗੁ ਪ੍ਰਭਾਤੀ", "Raag Jaijaavantee": "ਰਾਗੁ ਜੈਜਾਵੰਤੀ",
    "Salok Sehskritee": "ਸਲੋਕ ਸਹਸਕ੍ਰਿਤੀ", "Fifth Mehl, Gaathaa": "ਗਾਥਾ ਮਹਲਾ ੫",
    "Phunhay Fifth Mehl": "ਫੁਨਹੇ ਮਹਲਾ ੫", "Chaubolas Fifth Mehl": "ਚਉਬੋਲੇ ਮਹਲਾ ੫",
    "Salok Kabeer Jee": "ਸਲੋਕ ਕਬੀਰ ਜੀਉ", "Salok Fareed Jee": "ਸਲੋਕ ਫਰੀਦ ਜੀਉ",
    "Svaiyay Mehl 5": "ਸਵਈਏ ਮਹਲੇ ਪੰਜਵੇ ਕੇ", "Salok Vaaraan Thay Vadheek": "ਸਲੋਕ ਵਾਰਾਂ ਤੇ ਵਧੀਕ",
    "Salok Mehl 9": "ਸਲੋਕੁ ਮਹਲਾ ੯", "Mundhaavanee Fifth Mehl": "ਮੁੰਦਾਵਣੀ ਮਹਲਾ ੫",
    "Raag Maalaa": "ਰਾਗਮਾਲਾ",
}

RAAG_TYPE = {
    "Jap": "preamble", "So Dar": "preamble", "So Purakh": "preamble", "Sohila": "preamble",
    "Raag Maalaa": "appendix", "Mundhaavanee Fifth Mehl": "appendix",
    "Salok Kabeer Jee": "appendix", "Salok Fareed Jee": "appendix",
    "Svaiyay Mehl 5": "appendix", "Salok Vaaraan Thay Vadheek": "appendix",
    "Salok Mehl 9": "appendix", "Salok Sehskritee": "appendix",
    "Fifth Mehl, Gaathaa": "appendix", "Phunhay Fifth Mehl": "appendix",
    "Chaubolas Fifth Mehl": "appendix", "Raag Jaijaavantee": "raag",
}

def raag_id(name_en: str) -> str:
    slug = name_en.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", slug).strip("_")
    return slug


def author_id_for(writer_en: str) -> str | None:
    meta = AUTHOR_META.get(writer_en)
    return meta["id"] if meta else None


def build(conn: sqlite3.Connection) -> None:
    c = conn.cursor()

    # ── Authors ──────────────────────────────────────────────────────────────
    c.execute("SELECT DISTINCT writer_en FROM verses ORDER BY writer_en")
    authors = []
    for (writer_en,) in c.fetchall():
        if not writer_en:
            continue
        meta = AUTHOR_META.get(writer_en)
        if not meta:
            print(f"  WARN: unknown writer '{writer_en}'")
            continue
        c.execute("SELECT MIN(ang), MAX(ang), COUNT(*) FROM verses WHERE writer_en=?", (writer_en,))
        ang_min, ang_max, verse_count = c.fetchone()
        authors.append({
            "id": meta["id"],
            "name_en": writer_en.strip(),
            "name_gu": meta["name_gu"],
            "name_ru": meta["name_ru"],
            "type": meta["type"],
            "mahalla": meta["mahalla"],
            "ang_start": ang_min,
            "ang_end": ang_max,
            "verse_count": verse_count,
        })
    authors.sort(key=lambda a: (a["type"] != "mahalla", a["mahalla"] or 99, a["id"]))
    (OUT / "authors.json").write_text(json.dumps(authors, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"authors.json: {len(authors)} authors")

    # ── Raags ────────────────────────────────────────────────────────────────
    c.execute("SELECT raag_en, MIN(ang), MAX(ang), COUNT(*), COUNT(DISTINCT shabad_id) FROM verses GROUP BY raag_en ORDER BY MIN(ang)")
    raags = []
    for order, (raag_en, ang_min, ang_max, verse_count, shabad_count) in enumerate(c.fetchall(), 1):
        # writers in this raag
        c.execute("SELECT DISTINCT writer_en FROM verses WHERE raag_en=? AND writer_en != ''", (raag_en,))
        raag_authors = [author_id_for(w) for (w,) in c.fetchall() if author_id_for(w)]

        t = RAAG_TYPE.get(raag_en)
        if t is None:
            t = "raag" if raag_en.startswith("Raag ") else "section"

        raags.append({
            "id": raag_id(raag_en),
            "order": order,
            "name_en": raag_en,
            "name_gu": RAAG_GU.get(raag_en, ""),
            "name_ru": RAAG_RU.get(raag_en, raag_en),
            "type": t,
            "ang_start": ang_min,
            "ang_end": ang_max,
            "verse_count": verse_count,
            "shabad_count": shabad_count,
            "authors": raag_authors,
        })
    (OUT / "raags.json").write_text(json.dumps(raags, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"raags.json: {len(raags)} raags/sections")

    # ── Shabad index ─────────────────────────────────────────────────────────
    # MAX(CASE...) picks the non-empty writer even when the first verse is a
    # heading line (ਸਲੋਕੁ ॥, ਅਸਟਪਦੀ ॥, etc.) with no writer_en assigned.
    c.execute("""
        SELECT shabad_id,
               MIN(ang) AS ang,
               MIN(line_no) AS first_line,
               MAX(line_no) AS last_line,
               COUNT(*) AS verse_count,
               MAX(CASE WHEN writer_en != '' THEN writer_en ELSE NULL END) AS writer_en,
               MAX(raag_en) AS raag_en
        FROM verses
        GROUP BY shabad_id
        ORDER BY shabad_id
    """)
    shabads = []
    for row in c.fetchall():
        sh_id, ang, first_line, last_line, verse_count, writer_en, raag_en = row
        shabads.append({
            "shabad_id": sh_id,
            "ang": ang,
            "raag_id": raag_id(raag_en) if raag_en else None,
            "author_id": author_id_for(writer_en) if writer_en else None,
            "verse_count": verse_count,
        })

    # Propagate author from the previous shabad for the ~21 pure-header shabads
    # that have no author in any of their lines (structural markers).
    last_author: str | None = None
    for sh in shabads:
        if sh["author_id"] is not None:
            last_author = sh["author_id"]
        elif last_author is not None:
            sh["author_id"] = last_author

    (OUT / "shabad_index.json").write_text(json.dumps(shabads, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"shabad_index.json: {len(shabads)} shabads")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    conn = sqlite3.connect(BANIDB)
    build(conn)
    conn.close()


if __name__ == "__main__":
    main()
