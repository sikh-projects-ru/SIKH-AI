#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KSD_DIR = ROOT / "ksd_ang_json"
META_DIR = ROOT / "sggs_meta"
OUT_DIR = ROOT / "sggs_app" / "content" / "sggs_ru"
MOBILE_ASSETS_DIR = ROOT / "sggs_mobile" / "app" / "src" / "main" / "assets" / "sggs_ru"

SCHEMA_VERSION = 1
CONTENT_VERSION = 1
PACKAGE_ID = "sri_guru_granth_sahib_ru_ksd_v1"


ABOUT_SAHIB_SINGH = """# О переводе

Этот русский корпус подготовлен по мотивам линии толкования Prof. Sahib Singh.
Панджабский слой `sahib_singh_pa` сохраняет исходное объяснение, а русский слой
`sahib_singh_ru` передаёт его смысл на русском языке.

Это не официальный русский перевод Prof. Sahib Singh и не буквальная замена
панджабского оригинала. Приложение показывает Gurmukhi, roman, панджабское
объяснение и русский смысловой слой рядом, чтобы читатель мог сверять уровни
текста.

Автор приложения и русского проекта: Ilia Potseluev.
"""


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_works(raags: list[dict]) -> list[dict]:
    known = {
        "jap": "Джап",
        "so_dar": "Со Дар",
        "so_purakh": "Со Пуркх",
        "sohila": "Сохила",
        "salok_kabeer_jee": "Шлок Кабира",
        "salok_fareed_jee": "Шлок Фарида",
        "svaiyay_mehl_5": "Свайе Махла 5",
        "mundhaavanee_fifth_mehl": "Мундхавани",
        "raag_maalaa": "Раг Мала",
    }
    works = []
    for raag in raags:
        if raag["id"] in known or raag.get("type") in {"preamble", "appendix"}:
            works.append(
                {
                    "id": raag["id"],
                    "title_ru": known.get(raag["id"], raag.get("name_ru", raag["id"])),
                    "title_gurmukhi": raag.get("name_gu", ""),
                    "source": "raags",
                    "raag_id": raag["id"],
                    "ang_start": raag.get("ang_start"),
                    "ang_end": raag.get("ang_end"),
                    "shabad_count": raag.get("shabad_count"),
                }
            )

    works.extend(
        [
            {
                "id": "anand",
                "title_ru": "Ананд",
                "title_gurmukhi": "ਅਨੰਦੁ",
                "source": "manual_todo",
                "ang_start": 917,
                "ang_end": 922,
                "note": "Черновая граница для будущей точной индексации по shabad_id/verse_id.",
            },
            {
                "id": "sukhmani",
                "title_ru": "Сукхмани",
                "title_gurmukhi": "ਸੁਖਮਨੀ",
                "source": "manual_todo",
                "ang_start": 262,
                "ang_end": 296,
                "note": "Черновая граница для будущей точной индексации по ashtpadi.",
            },
            {
                "id": "barah_maha_majh_m5",
                "title_ru": "Барах Маха (Маджх, М5)",
                "title_gurmukhi": "ਬਾਰਹ ਮਾਹਾ ਮਾਂਝ ਮਹਲਾ ੫",
                "source": "manual",
                "ang_start": 133,
                "ang_end": 136,
                "start_shabad_id": 358,
                "shabad_id_end": 358,
                "start_verse_id": 5422,
            },
            {
                "id": "dakhni_gauri_m1",
                "title_ru": "Дакхни (Гаури, М1)",
                "title_gurmukhi": "ਗਉੜੀ ਮਹਲਾ ੧ ਦਖਣੀ",
                "source": "manual",
                "ang_start": 152,
                "ang_end": 152,
                "start_shabad_id": 454,
                "shabad_id_end": 454,
                "start_verse_id": 6295,
            },
            {
                "id": "bavan_akhari_gauri_m5",
                "title_ru": "Баван Акхари (Гаури, М5)",
                "title_gurmukhi": "ਗਉੜੀ ਬਾਵਨ ਅਖਰੀ ਮਹਲਾ ੫",
                "source": "manual",
                "ang_start": 250,
                "ang_end": 250,
                "start_shabad_id": 759,
                "shabad_id_end": 759,
                "start_verse_id": 10820,
            },
            {
                "id": "thhiti_gauri_m5",
                "title_ru": "Тхити (Гаури, М5)",
                "title_gurmukhi": "ਥਿਤੀ ਗਉੜੀ ਮਹਲਾ ੫",
                "source": "manual",
                "ang_start": 296,
                "ang_end": 296,
                "start_shabad_id": 1087,
                "shabad_id_end": 1087,
                "start_verse_id": 13512,
            },
            {
                "id": "bavan_akhari_kabir",
                "title_ru": "Баван Акхари (Гаури Пурби, Кабир)",
                "title_gurmukhi": "ਗਉੜੀ ਪੂਰਬੀ ਬਾਵਨ ਅਖਰੀ ਕਬੀਰ ਜੀਉ",
                "source": "manual",
                "ang_start": 340,
                "ang_end": 343,
                "start_shabad_id": 1359,
                "shabad_id_end": 1359,
                "start_verse_id": 15434,
            },
            {
                "id": "patti_likhi_m1",
                "title_ru": "Патти Ликхи (Аса, М1)",
                "title_gurmukhi": "ਆਸਾ ਮਹਲਾ ੧ ਪਟੀ ਲਿਖੀ",
                "source": "manual",
                "ang_start": 432,
                "ang_end": 434,
                "start_shabad_id": 1639,
                "shabad_id_end": 1639,
                "start_verse_id": 19723,
            },
            {
                "id": "patti_asa_m3",
                "title_ru": "Патти (Аса, М3)",
                "title_gurmukhi": "ਆਸਾ ਮਹਲਾ ੩ ਪਟੀ",
                "source": "manual",
                "ang_start": 434,
                "ang_end": 435,
                "start_shabad_id": 1641,
                "shabad_id_end": 1641,
                "start_verse_id": 19796,
            },
            {
                "id": "alahnia_vadhans_m1",
                "title_ru": "Алахниа (Вадханс, М1)",
                "title_gurmukhi": "ਵਡਹੰਸੁ ਮਹਲਾ ੧ ਅਲਾਹਣੀਆ",
                "source": "manual",
                "ang_start": 578,
                "ang_end": 579,
                "start_shabad_id": 2194,
                "shabad_id_end": 2194,
                "start_verse_id": 25305,
            },
            {
                "id": "kuchhaji_suhi_m1",
                "title_ru": "Кучхаджи (Сухи, М1)",
                "title_gurmukhi": "ਸੂਹੀ ਮਹਲਾ ੧ ਕੁਚਜੀ",
                "source": "manual",
                "ang_start": 762,
                "ang_end": 762,
                "start_shabad_id": 2881,
                "shabad_id_end": 2881,
                "start_verse_id": 32533,
            },
            {
                "id": "suchaji_suhi_m1",
                "title_ru": "Сучхаджи (Сухи, М1)",
                "title_gurmukhi": "ਸੂਹੀ ਮਹਲਾ ੧ ਸੁਚਜੀ",
                "source": "manual",
                "ang_start": 762,
                "ang_end": 762,
                "start_shabad_id": 2882,
                "shabad_id_end": 2882,
                "start_verse_id": 32551,
            },
            {
                "id": "thhiti_bilaval_m1",
                "title_ru": "Тхити (Билавал, М1)",
                "title_gurmukhi": "ਬਿਲਾਵਲੁ ਮਹਲਾ ੧ ਥਿਤੀ",
                "source": "manual",
                "ang_start": 838,
                "ang_end": 840,
                "start_shabad_id": 3150,
                "shabad_id_end": 3150,
                "start_verse_id": 35546,
            },
            {
                "id": "dakhni_onkar_ramkali_m1",
                "title_ru": "Онкар / Дакхни Онкар (Рамкали, М1)",
                "title_gurmukhi": "ਰਾਮਕਲੀ ਮਹਲਾ ੧ ਦਖਣੀ ਓਅੰਕਾਰੁ",
                "source": "manual",
                "ang_start": 929,
                "ang_end": 938,
                "start_shabad_id": 3406,
                "shabad_id_end": 3406,
                "start_verse_id": 39593,
            },
            {
                "id": "sidh_gosht_ramkali_m1",
                "title_ru": "Сидх Гости (Рамкали, М1)",
                "title_gurmukhi": "ਰਾਮਕਲੀ ਮਹਲਾ ੧ ਸਿਧ ਗੋਸਟਿ",
                "source": "manual",
                "ang_start": 938,
                "ang_end": 938,
                "start_shabad_id": 3407,
                "shabad_id_end": 3407,
                "start_verse_id": 39992,
            },
            {
                "id": "barah_maha_tukhari_m1",
                "title_ru": "Барах Маха (Тукхари, М1)",
                "title_gurmukhi": "ਤੁਖਾਰੀ ਛੰਤ ਮਹਲਾ ੧ ਬਾਰਹ ਮਾਹਾ",
                "source": "manual",
                "ang_start": 1107,
                "ang_end": 1107,
                "start_shabad_id": 3975,
                "shabad_id_end": 3975,
                "start_verse_id": 47329,
            },
        ]
    )
    return works


def main() -> None:
    raags = read_json(META_DIR / "raags.json")
    authors = read_json(META_DIR / "authors.json")
    shabads = read_json(META_DIR / "shabad_index.json")

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    (OUT_DIR / "angs").mkdir(parents=True)
    (OUT_DIR / "indexes").mkdir()
    (OUT_DIR / "articles").mkdir()

    ang_files = sorted(KSD_DIR.glob("ksd_ang_*.json"))
    if len(ang_files) != 1430:
        raise RuntimeError(f"Expected 1430 ang files, got {len(ang_files)}")

    total_shabads = 0
    total_lines = 0
    for src in ang_files:
        data = read_json(src)
        if "shabads" not in data or "lines" in data:
            raise RuntimeError(f"Unexpected ang format: {src.name}")
        total_shabads += len(data["shabads"])
        total_lines += sum(len(shabad.get("lines", [])) for shabad in data["shabads"])
        shutil.copy2(src, OUT_DIR / "angs" / src.name)

    write_json(OUT_DIR / "indexes" / "raags.json", raags)
    write_json(OUT_DIR / "indexes" / "authors.json", authors)
    write_json(OUT_DIR / "indexes" / "shabads.json", shabads)
    write_json(OUT_DIR / "indexes" / "works.json", build_works(raags))
    (OUT_DIR / "articles" / "about_sahib_singh_ru.md").write_text(
        ABOUT_SAHIB_SINGH,
        encoding="utf-8",
    )

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "content_version": CONTENT_VERSION,
        "package_id": PACKAGE_ID,
        "title": "Sri Guru Granth Sahib RU",
        "app_authors": ["Ilia Potseluev"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ang_start": 1,
        "ang_end": 1430,
        "ang_count": len(ang_files),
        "shabad_count": total_shabads,
        "line_count": total_lines,
        "default_layers": ["gurmukhi", "roman", "sahib_singh_pa", "sahib_singh_ru"],
        "indexes": {
            "raags": "indexes/raags.json",
            "authors": "indexes/authors.json",
            "shabads": "indexes/shabads.json",
            "works": "indexes/works.json",
        },
        "ang_path_pattern": "angs/ksd_ang_%04d.json",
        "articles": {
            "about_sahib_singh": "articles/about_sahib_singh_ru.md",
        },
    }
    write_json(OUT_DIR / "sggs_manifest.json", manifest)

    if MOBILE_ASSETS_DIR.parent.exists():
        if MOBILE_ASSETS_DIR.exists():
            shutil.rmtree(MOBILE_ASSETS_DIR)
        shutil.copytree(OUT_DIR, MOBILE_ASSETS_DIR)

    print(f"Wrote {OUT_DIR}")
    print(f"Copied to {MOBILE_ASSETS_DIR}")
    print(f"angs={len(ang_files)} shabads={total_shabads} lines={total_lines}")


if __name__ == "__main__":
    main()
