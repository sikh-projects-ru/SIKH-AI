#!/usr/bin/env python3
"""
annotate_quotes.py — добавляет Гурмукхи + транслитерацию к цитатам СГГС
в page_json/*.json, используя локальную sggs.db.

Алгоритм:
  1. Для каждой страницы ищем ссылки вида (Raag M.X, p.YYY)
  2. Находим ближайшую «цитату» перед ссылкой
  3. Из raw_text (английский оригинал) или из русской цитаты извлекаем ключевые слова
  4. По ang Y ищем строку с наибольшим пересечением слов с английским переводом
  5. Добавляем в JSON поле `gurbani_annotations`

Использование:
    python annotate_quotes.py           # обработать все страницы
    python annotate_quotes.py --dry-run # показать матчи без записи
    python annotate_quotes.py --page 35 # одна страница
    python annotate_quotes.py --min-score 2  # минимальный порог совпадений
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from banidb.lookup import SggsDB

HERE     = Path(__file__).parent
JSON_DIR = HERE / "page_json"

# ── Patterns ──────────────────────────────────────────────────────────────────

# Ссылка на СГГС: (Sorath M. 5, p. 611) / (Bhairo M. 5. p. 1136) / (p. 144)
SGGS_REF_RE = re.compile(
    r'\(([^)]*?[Pp][\.\s]*(\d{1,4})[^)]*)\)',
)

# Гурбани цитата в «кавычках»
QUOTE_RU_RE = re.compile(r'«([^»]+)»')

# Гурбани цитата в "кавычках" (английский raw_text)
QUOTE_EN_RE = re.compile(r'"([^"]{10,200})"')

# Стоп-слова для фильтрации при матчинге
STOPWORDS_EN = {
    "the","a","an","of","in","is","are","and","or","not","no","to","be",
    "it","this","that","with","for","from","by","as","at","on","he","she",
    "we","they","i","my","his","her","our","their","its","all","one","two",
    "said","says","lord","god","guru","who","what","which","when","where",
    "do","does","did","has","have","had","will","would","shall","may",
    "but","so","then","there","here","if","than","more","also","only",
}

STOPWORDS_RU = {
    "и","в","на","с","к","а","но","или","не","он","она","они","мы","я",
    "это","что","как","так","его","её","их","по","из","за","от","до",
    "при","для","же","бы","ли","уже","ещё","тот","тем","такой","такого",
    "который","которая","которые","был","была","было","были","есть","нет",
}

# Русские транслитерации → английские эквиваленты для матчинга
RU_TO_EN: dict[str, str] = {
    "хинду":    "hindu",
    "хиндус":   "hindu",
    "мусульман":"muslim",
    "мусульмане":"muslim",
    "сикх":     "sikh",
    "нанак":    "nanak",
    "кабир":    "kabir",
    "пандит":   "pandit",
    "брахмин":  "brahmin",
    "брахман":  "brahman",
    "вахегуру": "vaheguru",
    "вахигуру": "waheguru",
    "гуру":     "guru",
    "рама":     "rama",
    "рахим":    "rahim",
    "аллах":    "allah",
    "мулла":    "mullah",
    "мекка":    "mecca",
    "ганг":     "ganga",
    "ганга":    "ganga",
    "веды":     "vedas",
    "веда":     "veda",
    "мандир":   "mandir",
    "мечеть":   "mosque",
    "молитва":  "prayer",
    "сewa":     "seva",
    "сева":     "seva",
    "нирвана":  "nirvana",
    "шабад":    "shabad",
    "гурбани":  "gurbani",
    "хальса":   "khalsa",
    "кхальса":  "khalsa",
    "пантх":    "panth",
    "харинам":  "naam",
    "вода":     "water",
    "воды":     "water",
    "кумбх":    "kumbh",
    "насекомых":"worm",
    "насекомые":"worm",
    "насекомо": "worm",
    "червь":    "worm",
    "армии":    "army",
    "армия":    "army",
    "отец":     "father",
    "дети":     "children",
    "сыновья":  "sons",
    "истина":   "truth",
    "ложь":     "false",
    "ложный":   "false",
    "смерть":   "death",
    "рождение": "birth",
    "пандита":  "pandit",
    "пандиту":  "pandit",
    "пандиты":  "pandit",
    "муллу":    "mullah",
    "муллы":    "mullah",
    "мечети":   "mosque",
    "мечеть":   "mosque",
    "мечетях":  "mosque",
    "распрю":   "dispute",
    "распря":   "dispute",
    "слеп":     "blind",
    "слепой":   "blind",
    "одноглаз": "one-eyed",
}


# ── Keyword extraction ─────────────────────────────────────────────────────────

def keywords_en(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Z']+", text.lower())
    return [w for w in words if len(w) > 3 and w not in STOPWORDS_EN]


def keywords_ru(text: str) -> list[str]:
    words = re.findall(r"[а-яёА-ЯЁ]+", text.lower())
    return [w for w in words if len(w) > 3 and w not in STOPWORDS_RU]


def ru_keywords_as_en(kw_ru: list[str]) -> list[str]:
    """Конвертирует русские ключевые слова в английские через словарь."""
    result = []
    for k in kw_ru:
        en = RU_TO_EN.get(k)
        if en:
            result.append(en)
    return result


def score_verse(verse: dict, kw_en: list[str], kw_ru: list[str]) -> int:
    """Сколько ключевых слов попало в английский перевод строки."""
    en = (verse.get("translation_en") or "").lower()
    score = sum(1 for k in kw_en if k in en)
    # Перевод русских транслитераций через словарь
    for k in ru_keywords_as_en(kw_ru):
        if k in en:
            score += 2  # двойной вес: прямое совпадение через словарь
    return score


# ── Source-text helpers ────────────────────────────────────────────────────────

def extract_context_around(text: str, ref_start: int, window: int = 400) -> str:
    """Текст до и после ссылки — для поиска цитаты."""
    return text[max(0, ref_start - window): ref_start + 50]


def find_quote_before(text: str, ref_start: int) -> str:
    """Ближайшая «цитата» перед позицией ref_start."""
    snippet = text[max(0, ref_start - 500): ref_start]
    matches = list(QUOTE_RU_RE.finditer(snippet))
    if matches:
        return matches[-1].group(1)
    return ""


def find_en_quote_before(raw: str, ref_start: int) -> str:
    """Ближайшая "en quote" перед позицией в raw_text."""
    snippet = raw[max(0, ref_start - 500): ref_start]
    matches = list(QUOTE_EN_RE.finditer(snippet))
    if matches:
        return matches[-1].group(1)
    return ""


# ── Per-page annotation ───────────────────────────────────────────────────────

def annotate_page(data: dict, db: SggsDB, min_score: int, dry_run: bool) -> bool:
    """
    Сканирует страницу, находит СГГС-ссылки, матчит строки.
    Возвращает True если файл был изменён.
    """
    pnum       = data["page"]
    ru_text    = data.get("translation_ru") or ""
    raw_text   = data.get("raw_text") or ""

    # Уже аннотированные — не трогаем повторно (если есть хоть одна запись)
    existing = {a["ref"] for a in data.get("gurbani_annotations", [])}

    annotations = list(data.get("gurbani_annotations", []))
    changed = False

    # Ищем ссылки в русском тексте
    for m in SGGS_REF_RE.finditer(ru_text):
        ref_str = m.group(1).strip()
        ang     = int(m.group(2))

        # Фильтр: ang от 1 до 1430
        if ang < 1 or ang > 1430:
            continue

        ref_key = f"p{ang}"
        if ref_key in existing:
            continue  # уже обработано

        if not db.is_available(ang):
            print(f"  [!] ang {ang} не в sggs.db (стр. {pnum})")
            continue

        # Русская цитата перед ссылкой
        ru_quote = find_quote_before(ru_text, m.start())

        # Английская цитата из raw_text (если есть)
        en_quote = ""
        if raw_text:
            # Найти ту же ссылку в raw_text
            for rm in SGGS_REF_RE.finditer(raw_text):
                if rm.group(2) == m.group(2):
                    en_quote = find_en_quote_before(raw_text, rm.start())
                    break

        # Ключевые слова
        kw_en = keywords_en(en_quote) if en_quote else []
        kw_ru = keywords_ru(ru_quote) if ru_quote else []

        # Если совсем нет ключевых слов — берём контекст из russian текста
        if not kw_en and not kw_ru:
            ctx = extract_context_around(ru_text, m.start())
            kw_ru = keywords_ru(ctx)

        # Матчинг
        verses = db.get_ang(ang)
        scored = [(score_verse(v, kw_en, kw_ru), v) for v in verses]
        scored.sort(key=lambda x: -x[0])

        best_score, best_verse = scored[0] if scored else (0, None)
        auto = best_score >= min_score

        annotation: dict = {
            "ref":       ref_str,
            "ang":       ang,
            "auto":      auto,
            "score":     best_score,
        }

        if best_verse:
            annotation["verse_id"]       = best_verse["verse_id"]
            annotation["shabad_id"]      = best_verse["shabad_id"]
            annotation["gurmukhi"]       = best_verse["gurmukhi"]
            annotation["transliteration"]= best_verse["transliteration"]
            annotation["translation_en"] = best_verse["translation_en"]
        else:
            annotation["gurmukhi"]       = ""
            annotation["transliteration"]= ""
            annotation["translation_en"] = ""

        if ru_quote:
            annotation["quote_ru"] = ru_quote[:120]
        if en_quote:
            annotation["quote_en"] = en_quote[:120]

        annotations.append(annotation)
        existing.add(ref_key)
        changed = True

        status = "✓" if auto else "?"
        print(f"  [{status}] стр.{pnum} ang {ang:4d}  score={best_score}"
              f"  {best_verse['gurmukhi'][:50] if best_verse else '—'}")
        if dry_run:
            print(f"       ru: «{ru_quote[:60]}»" if ru_quote else "       (нет цитаты)")
            print(f"       en: «{en_quote[:60]}»" if en_quote else "")

    if changed and not dry_run:
        data["gurbani_annotations"] = annotations

    return changed


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Annotate SGGS quotes in page_json")
    parser.add_argument("--dry-run",   action="store_true", help="Показать матчи, не писать файлы")
    parser.add_argument("--page",      type=int,            help="Обработать только одну страницу")
    parser.add_argument("--min-score", type=int, default=1, help="Минимальный порог совпадений (default: 1)")
    parser.add_argument("--force",     action="store_true", help="Перезаписать существующие аннотации")
    args = parser.parse_args()

    db = SggsDB()

    pages = sorted(JSON_DIR.glob("page_*.json"),
                   key=lambda p: int(p.stem.split("_")[1]))

    if args.page:
        pages = [JSON_DIR / f"page_{args.page:04d}.json"]

    total_changed = 0
    total_annotations = 0

    for json_path in pages:
        data = json.loads(json_path.read_text())

        if args.force:
            data.pop("gurbani_annotations", None)

        changed = annotate_page(data, db, args.min_score, args.dry_run)

        if changed:
            total_changed += 1
            n = len(data.get("gurbani_annotations", []))
            total_annotations += n
            if not args.dry_run:
                json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    db.close()
    verb = "найдено" if args.dry_run else "обновлено"
    print(f"\n{verb} {total_annotations} аннотаций на {total_changed} страницах")


if __name__ == "__main__":
    main()
