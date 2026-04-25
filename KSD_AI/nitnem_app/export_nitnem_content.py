#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
KSD_DIR = ROOT / "ksd_ang_json"
OUT_DIR = ROOT / "nitnem_app" / "content"
OUT_FILE = OUT_DIR / "nitnem_ru_ksd_v1.json"

AUTHORS = {
    "guru_nanak": {
        "id": "guru_nanak",
        "name_ru": "Гуру Нанак",
        "mahalla": 1,
    },
    "guru_ram_das": {
        "id": "guru_ram_das",
        "name_ru": "Гуру Рам Дас",
        "mahalla": 4,
    },
    "guru_arjan": {
        "id": "guru_arjan",
        "name_ru": "Гуру Арджан",
        "mahalla": 5,
    },
}

WORKS = [
    {
        "id": "jap",
        "order": 1,
        "title_ru": "Джап",
        "title_gurmukhi": "ਜਪੁ",
        "shabad_start": 1,
        "shabad_end": 40,
        "description_ru": "Джап: вступительная формула, 38 паури и заключительный шлок.",
    },
    {
        "id": "so_dar",
        "order": 2,
        "title_ru": "Со Дар",
        "title_gurmukhi": "ਸੋ ਦਰੁ",
        "shabad_start": 41,
        "shabad_end": 45,
        "description_ru": "Со Дар: раздел, раскрывающий внутренний дар/дом осознания.",
    },
    {
        "id": "so_purakh",
        "order": 3,
        "title_ru": "Со Пуркх",
        "title_gurmukhi": "ਸੋ ਪੁਰਖੁ",
        "shabad_start": 46,
        "shabad_end": 49,
        "description_ru": "Со Пуркх: раздел о всепронизывающем Творце и внутреннем дхьяне.",
    },
    {
        "id": "sohila",
        "order": 4,
        "title_ru": "Сохила",
        "title_gurmukhi": "ਸੋਹਿਲਾ",
        "shabad_start": 50,
        "shabad_end": 54,
        "description_ru": "Сохила: песнь Мира и внутреннего согласия с Хукамом.",
    },
]

AUTHOR_BY_SHABAD = {
    41: "guru_nanak",
    42: "guru_nanak",
    43: "guru_nanak",
    44: "guru_ram_das",
    45: "guru_arjan",
    46: "guru_ram_das",
    47: "guru_ram_das",
    48: "guru_nanak",
    49: "guru_arjan",
    50: "guru_nanak",
    51: "guru_nanak",
    52: "guru_nanak",
    53: "guru_ram_das",
    54: "guru_arjan",
}


def work_for_shabad(shabad_id: int) -> dict[str, Any]:
    for work in WORKS:
        if work["shabad_start"] <= shabad_id <= work["shabad_end"]:
            return work
    raise ValueError(f"Shabad {shabad_id} does not belong to a known Nitnem work")


def unit_for_shabad(shabad_id: int) -> dict[str, Any]:
    if shabad_id == 1:
        return {
            "id": "jap_opening",
            "order": 0,
            "kind": "opening",
            "title_ru": "Вступление",
            "title_gurmukhi": "ਮੂਲ ਮੰਤ੍ਰ / ਜਪੁ",
        }
    if 2 <= shabad_id <= 39:
        number = shabad_id - 1
        return {
            "id": f"jap_pauri_{number:02d}",
            "order": number,
            "kind": "pauri",
            "number": number,
            "title_ru": f"Паури {number}",
            "title_gurmukhi": f"ਪਉੜੀ {number}",
        }
    if shabad_id == 40:
        return {
            "id": "jap_final_salok",
            "order": 39,
            "kind": "salok",
            "title_ru": "Заключительный шлок",
            "title_gurmukhi": "ਸਲੋਕੁ",
        }

    work = work_for_shabad(shabad_id)
    number = shabad_id - work["shabad_start"] + 1
    return {
        "id": f"{work['id']}_shabad_{number:02d}",
        "order": number,
        "kind": "shabad",
        "number": number,
        "title_ru": f"Шабд {number}",
        "title_gurmukhi": "",
    }


def author_for_shabad(shabad_id: int) -> dict[str, Any]:
    author_id = AUTHOR_BY_SHABAD.get(shabad_id, "guru_nanak")
    return AUTHORS[author_id]


def load_ang(ang: int) -> dict[str, Any]:
    path = KSD_DIR / f"ksd_ang_{ang:04d}.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def export_line(
    ang: int,
    shabad_id: int,
    line: dict[str, Any],
    work: dict[str, Any],
    unit: dict[str, Any],
    author: dict[str, Any],
) -> dict[str, Any]:
    verse_id = line.get("verse_id")
    return {
        "id": f"{ang}:{shabad_id}:{verse_id}",
        "ang": ang,
        "shabad_id": shabad_id,
        "verse_id": verse_id,
        "work_id": work["id"],
        "work_title_ru": work["title_ru"],
        "work_order": work["order"],
        "work_unit_id": unit["id"],
        "work_unit_order": unit["order"],
        "work_unit_kind": unit["kind"],
        "work_unit_title_ru": unit["title_ru"],
        "author_id": author["id"],
        "author_name_ru": author["name_ru"],
        "mahalla": author["mahalla"],
        "is_rahao": bool(line.get("is_rahao", False)),
        "gurmukhi": line.get("gurmukhi", ""),
        "roman": line.get("roman", ""),
        "roman_display": line.get("roman_display", line.get("roman", "")),
        "translations": {
            "ksd_ru": {
                "main": line.get("ksd_translation", ""),
                "artistic": line.get("artistic_ru", ""),
                "context_note": line.get("context_note", ""),
                "confidence": line.get("confidence", None),
                "confidence_reason": line.get("confidence_reason", ""),
            }
        },
        "word_analysis": line.get("word_analysis", []),
    }


def export_shabad(ang: int, shabad: dict[str, Any]) -> dict[str, Any]:
    shabad_id = shabad.get("shabad_id")
    work = work_for_shabad(shabad_id)
    unit = unit_for_shabad(shabad_id)
    author = author_for_shabad(shabad_id)
    return {
        "id": f"{ang}:{shabad_id}",
        "ang": ang,
        "shabad_id": shabad_id,
        "work_id": work["id"],
        "work_title_ru": work["title_ru"],
        "work_order": work["order"],
        "work_unit": unit,
        "author_id": author["id"],
        "author_name_ru": author["name_ru"],
        "mahalla": author["mahalla"],
        "rahao_verse_id": shabad.get("rahao_verse_id"),
        "rahao_theme": shabad.get("rahao_theme", ""),
        "summary": shabad.get("shabad_summary", ""),
        "lines": [
            export_line(ang, shabad_id, line, work, unit, author)
            for line in shabad.get("lines", [])
        ],
    }


def build_pack() -> dict[str, Any]:
    angs = []
    for ang in range(1, 14):
        data = load_ang(ang)
        angs.append({
            "ang": ang,
            "shabads": [
                export_shabad(ang, shabad)
                for shabad in data.get("shabads", [])
            ],
        })

    return {
        "schema_version": 1,
        "content_version": 1,
        "package_id": "nitnem_ru_ksd_sggs_001_013",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "language": "ru",
        "source": {
            "name": "Sri Guru Granth Sahib",
            "ang_start": 1,
            "ang_end": 13,
        },
        "translators": [
            {
                "id": "ksd_ru",
                "name": "KSD Russian",
                "language": "ru",
                "style": "interpretive",
            }
        ],
        "authors": list(AUTHORS.values()),
        "works": WORKS,
        "banis": [
            {
                "id": "nitnem_sggs_ang_001_013",
                "title": "Нитнем",
                "subtitle": "Первые 13 ангов СГГС",
                "ang_start": 1,
                "ang_end": 13,
                "section_refs": [
                    {"type": "ang", "ang": ang}
                    for ang in range(1, 14)
                ],
                "info_blocks": [
                    {
                        "id": "about_nitnem",
                        "title": "О Нитнеме",
                        "body": "Нитнем в этом приложении представлен как ежедневное чтение первых 13 ангов СГГС с русским смысловым переводом.",
                    },
                    {
                        "id": "translation_note",
                        "title": "О переводе",
                        "body": (
                            "Этот перевод выполнен с учётом школы доктора "
                            "Карминдера Сингха Диллона и по мотивам его "
                            "подходов к переводу и вичару Гурбани. Он не "
                            "является официальным переводом доктора Карминдера "
                            "Сингха Диллона и не отражает полностью его "
                            "переводы. Для серьёзного знакомства с этим "
                            "направлением необходимо самостоятельно изучать "
                            "его лекции, книги, переводы и разборы."
                        ),
                    },
                    {
                        "id": "reader_note",
                        "title": "Как читать",
                        "body": (
                            "Это приложение предлагает перевод как пространство "
                            "вичара, а не как замену оригинала. Гурмукхи, "
                            "транслитерация, перевод и заметки следует читать "
                            "вместе, возвращаясь к Шабду как главному источнику."
                        ),
                    }
                ],
            }
        ],
        "display_layers": [
            "gurmukhi",
            "roman",
            "roman_display",
            "translation_main",
            "translation_artistic",
            "context_note",
            "word_analysis",
        ],
        "angs": angs,
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pack = build_pack()
    with OUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(pack, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Wrote {OUT_FILE}")


if __name__ == "__main__":
    main()
