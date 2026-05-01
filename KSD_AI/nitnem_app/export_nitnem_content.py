#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transliteration import roman_display_from_gurmukhi


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
    "guru_amar_das": {
        "id": "guru_amar_das",
        "name_ru": "Гуру Амардас",
        "mahalla": 3,
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
    {
        "id": "anand_bani",
        "order": 101,
        "title_ru": "Ананд Бани",
        "title_gurmukhi": "ਅਨੰਦੁ",
        "shabad_start": 2481,
        "shabad_end": 2481,
        "description_ru": "Ананд Бани: Рамкали Махла 3, анг 917-922.",
    },
]

AUTHOR_BY_SHABAD = {
    2481: "guru_amar_das",
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


GURMUKHI_DIGITS = str.maketrans("੦੧੨੩੪੫੬੭੮੯", "0123456789")


def anand_bani_unit(number: int) -> dict[str, Any]:
    return {
        "id": f"anand_bani_pauri_{number:02d}",
        "order": number,
        "kind": "pauri",
        "number": number,
        "title_ru": f"Паури {number}",
        "title_gurmukhi": f"ਪਉੜੀ {number}",
    }


def anand_bani_opening_unit() -> dict[str, Any]:
    return {
        "id": "anand_bani_opening",
        "order": 0,
        "kind": "opening",
        "title_ru": "Вступление",
        "title_gurmukhi": "ਰਾਮਕਲੀ / ੴ",
    }


def anand_pauri_marker(gurmukhi: str) -> int | None:
    matches = re.findall(r"॥([੦-੯]+)॥", gurmukhi)
    if not matches:
        return None
    return int(matches[-1].translate(GURMUKHI_DIGITS))


def units_for_lines(shabad_id: int, lines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if shabad_id != 2481:
        return [unit_for_shabad(shabad_id) for _ in lines]

    units = []
    current_pauri = next(
        (
            marker
            for marker in (anand_pauri_marker(line.get("gurmukhi", "")) for line in lines)
            if marker is not None
        ),
        1,
    )
    for line in lines:
        gurmukhi = line.get("gurmukhi", "")
        marker = anand_pauri_marker(gurmukhi)
        is_opening = gurmukhi.startswith("ਰਾਮਕਲੀ ਮਹਲਾ ੩") or gurmukhi.startswith("ੴ")
        if current_pauri <= 40:
            unit = anand_bani_unit(current_pauri)
        else:
            unit = anand_bani_opening_unit()

        if marker is None and is_opening:
            unit = anand_bani_opening_unit()

        units.append(unit)

        if marker is not None:
            current_pauri = marker + 1

    return units


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
        "roman_display": roman_display_from_gurmukhi(
            line.get("gurmukhi", ""),
            line.get("roman", ""),
        ),
        "translations": line.get("translations", {}),
    }


def export_shabad(ang: int, shabad: dict[str, Any]) -> dict[str, Any]:
    shabad_id = shabad.get("shabad_id")
    work = work_for_shabad(shabad_id)
    author = author_for_shabad(shabad_id)
    lines = shabad.get("lines", [])
    line_units = units_for_lines(shabad_id, lines)
    shabad_unit = line_units[0] if line_units else unit_for_shabad(shabad_id)
    return {
        "id": f"{ang}:{shabad_id}",
        "ang": ang,
        "shabad_id": shabad_id,
        "work_id": work["id"],
        "work_title_ru": work["title_ru"],
        "work_order": work["order"],
        "work_unit": shabad_unit,
        "author_id": author["id"],
        "author_name_ru": author["name_ru"],
        "mahalla": author["mahalla"],
        "rahao_verse_id": shabad.get("rahao_verse_id"),
        "rahao_theme": shabad.get("rahao_theme", ""),
        "summary": shabad.get("shabad_summary", ""),
        "lines": [
            export_line(ang, shabad_id, line, work, unit, author)
            for line, unit in zip(lines, line_units)
        ],
    }


def build_pack() -> dict[str, Any]:
    angs = []
    export_angs = list(range(1, 14)) + list(range(917, 923))
    for ang in export_angs:
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
            "ang_end": 922,
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
                "title": "Nitnem Authentic",
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
                        "body": (
                            "Nitnem Authentic представлен как ежедневное чтение "
                            "первых 13 ангов СГГС с русским смысловым переводом. "
                            "Здесь Нитнем включает Джап Бани, Со Дар, Со Пуркх "
                            "и Сохила. Эти разделы читаются друг за другом в том "
                            "порядке, в котором они идут в СГГС."
                        ),
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
                            "Читайте каждый шабд по слоям и по цветам. "
                            "Тёмно-красный — Гурмукхи, исходная строка "
                            "Гуру-Шабда; к ней всегда нужно возвращаться как "
                            "к главному источнику. Серый — транслитерация: "
                            "она помогает держать звучание и узнавать "
                            "повторяющиеся слова. Тёмно-зелёный — основной "
                            "русский смысловой перевод. Тёмно-синий — "
                            "художественный слой: он передаёт тот же смысл "
                            "более живым языком и дополняет основной "
                            "перевод. Синий — контекстные вставки и "
                            "пояснения: это мостик, который показывает, что "
                            "добавлено для русского понимания, что взято из "
                            "соседних строк, Рахао или общей темы шабда. "
                            "Серый мелкий комментарий — рабочая заметка о "
                            "переводческом решении, уверенности или грамматике. "
                            "Малиновый — Рахао, ключевая мысль шабда. Если "
                            "в шабде есть Рахао, начинайте понимание с него: "
                            "он задаёт центральный смысл, а остальные строки "
                            "раскрывают, уточняют и разворачивают эту тему. "
                            "Поэтому сначала прочитайте малиновый Рахао, затем "
                            "вернитесь к началу шабда и смотрите, как каждая "
                            "строка связана с этой ключевой мыслью. Разбор "
                            "слов открывайте медленно: он показывает, какие "
                            "термины держат смысл строки и как они связаны с "
                            "Наамом, Хукамом, Шабдом, Сатгуру, майей, разумом "
                            "и совестью. Читайте это как пространство вичара."
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
        ],
        "angs": angs,
    }


def main() -> None:
    import shutil
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pack = build_pack()
    with OUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(pack, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Wrote {OUT_FILE}")

    angs = pack["angs"]
    total_shabads = sum(len(a["shabads"]) for a in angs)
    total_lines = sum(len(s["lines"]) for a in angs for s in a["shabads"])
    print(f"  {len(angs)} angs / {total_shabads} shabads / {total_lines} lines")

    assets = ROOT / "nitnem_mobile" / "app" / "src" / "main" / "assets" / OUT_FILE.name
    if assets.parent.exists():
        shutil.copy2(OUT_FILE, assets)
        print(f"  Copied → {assets.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
