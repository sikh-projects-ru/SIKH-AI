#!/usr/bin/env python3
"""
ksd_ai_translator.py

AI Karminder Singh Dhillon — переводчик СГГС.

Берёт ang_json → обрабатывает каждый шабд через Claude API
с опорой на ksd_knowledge.db → выдаёт docx.

Принципы вывода:
  - Оригинальный порядок строк и шабдов НЕ меняется.
  - На каждую строку: Гурмукхи → романизация → KSD-перевод (смысл выше художественности).
  - Синий блок (контекст/переход) — только там, где это важно.
  - Краткая сноска-комментарий к строке если нужно — отдельная строка, мелко.
  - Художественный вариант — отдельная строка, курсив, необязательно.
  - Confidence: HIGH/MEDIUM/LOW — не показывается читателю, хранится в JSON.

Использование:
  python3 ksd_ai_translator.py --ang 1          # один анг
  python3 ksd_ai_translator.py --ang 1-8        # диапазон
  python3 ksd_ai_translator.py --shabad 23      # один шабд
  python3 ksd_ai_translator.py --all            # всё подряд
  python3 ksd_ai_translator.py --resume         # продолжить с места остановки
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any

import anthropic
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

# ─── пути ────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
BASE_DIR   = SCRIPT_DIR.parent
ANG_JSON   = BASE_DIR / "custom_khoj_sahib_singh" / "ang_json"
DB_PATH    = SCRIPT_DIR / "ksd_knowledge.db"
OUT_DIR    = SCRIPT_DIR / "output"
LOG_DIR    = SCRIPT_DIR / "logs"

OUT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

PROGRESS_FILE = SCRIPT_DIR / "ksd_translator.progress"
OUTPUT_DOCX   = OUT_DIR / "SGGS_KSD_Russian.docx"
OUTPUT_JSON   = OUT_DIR / "ksd_results.jsonl"

# ─── цвета docx ──────────────────────────────────────────────────────────────
COLOR_GURMUKHI    = RGBColor(0x55, 0x00, 0x00)   # тёмно-красный
COLOR_ROMAN       = RGBColor(0x55, 0x55, 0x55)   # серый
COLOR_TRANSLATION = RGBColor(0x00, 0x55, 0x00)   # тёмно-зелёный
COLOR_CONTEXT     = RGBColor(0x00, 0x55, 0xAA)   # синий — "crossing over"
COLOR_COMMENT     = RGBColor(0x77, 0x77, 0x77)   # серый мелкий — комментарий
COLOR_ARTISTIC    = RGBColor(0x33, 0x33, 0x66)   # тёмно-синий — художественный вариант
COLOR_RAHAO       = RGBColor(0x88, 0x00, 0x55)   # пурпурный — строка Рахао

# ─── Claude API ──────────────────────────────────────────────────────────────
MODEL = "claude-sonnet-4-6"

# ─── system prompt ────────────────────────────────────────────────────────────

def build_system_prompt(db_conn: sqlite3.Connection) -> str:
    cur = db_conn.cursor()

    # Принципы KSD
    cur.execute("SELECT num, title, description FROM ksd_principles ORDER BY num")
    principles = cur.fetchall()
    principles_text = "\n".join(
        f"Принцип {p[0]} ({p[1]}): {p[2][:300]}"
        for p in principles
    )

    # Концепты Nanak Canvas (ключевые)
    cur.execute("SELECT concept, ksd_meaning FROM canvas_concepts WHERE source='canvas_ksd' LIMIT 12")
    canvas = cur.fetchall()
    canvas_text = "\n".join(
        f"• {c[0].upper()}: {c[1][:200]}"
        for c in canvas
    )

    # Грамматические правила
    cur.execute("SELECT pattern, meaning FROM grammar_rules LIMIT 20")
    grammar = cur.fetchall()
    grammar_text = "\n".join(f"  {g[0]} → {g[1]}" for g in grammar)

    return f"""Ты — AI-версия Карминдера Сингха Диллона (KSD), лучшего интерпретатора Сири Гуру Грантх Сахиб (СГГС).

ТВОЯ ЗАДАЧА: создавать аутентичный русский перевод шабдов СГГС строго по методологии KSD.

━━━ МЕТОДОЛОГИЯ (8 принципов) ━━━

{principles_text}

━━━ ХОЛСТ НАНАКА (Nanak Canvas) — концептуальный фрейм ━━━

Следующие понятия в Гурбани НЕ имеют буквального смысла. KSD их переопределяет:
{canvas_text}

━━━ ГРАММАТИКА ГУРБАНИ ━━━

Окончания слов критически меняют смысл:
{grammar_text}

━━━ НЕИЗМЕННЫЕ ПРАВИЛА ━━━

1. ПОРЯДОК строк в шабде не меняется никогда.
2. СМЫСЛ важнее художественности. Художественность — вторична.
3. Если слово может означать несколько вещей — давай confidence (0.0–1.0) для каждого варианта.
4. Строка Рахао — это тема/суть всего шабда. Читать шабд начиная с Рахао.
5. Гурбани объясняет Гурбани. Не привносить внешних философий (индуизм, ислам, йога).
6. Гурбани написано ДЛЯ МЕНЯ (читателя) — не о ком-то снаружи.
7. Творец — ВНУТРИ, не снаружи.
8. Гурбани — о СЕЙЧАС, не о загробной жизни.
9. Комментарий к строке — только если это реально открывает смысл. Не быть снисходительным.

━━━ ФОРМАТ ОТВЕТА ━━━

Верни строго JSON между BEGIN_KSD_JSON и END_KSD_JSON.
Никаких markdown-блоков снаружи этих маркеров.

Структура JSON:
{{
  "ang": <int>,
  "shabad_id": <int>,
  "rahao_verse_id": <int | null>,
  "rahao_theme": "<тема шабда одной фразой>",
  "lines": [
    {{
      "verse_id": <int>,
      "is_rahao": <bool>,
      "word_analysis": [
        {{
          "roman": "<romanized word>",
          "literal_ru": "<буквальный смысл>",
          "ksd_meta_ru": "<KSD-метафорический смысл>",
          "confidence": <0.0–1.0>,
          "grammar_note": "<опционально: aunkard=муж.ед., sihari=в пределах и т.д.>"
        }}
      ],
      "ksd_translation": "<KSD-перевод строки — смысловой, без отсебятины>",
      "artistic_ru": "<художественный вариант — опционально, только если добавляет ценность>",
      "context_note": "<синий блок: только если здесь происходит важный 'переход' — иначе пустая строка>",
      "confidence": <0.0–1.0>,
      "confidence_reason": "<почему такой уровень: что неоднозначно или наоборот хорошо обосновано>"
    }}
  ],
  "shabad_summary": "<краткое резюме смысла всего шабда — 1-2 предложения>"
}}

ВАЖНО по confidence:
- HIGH (0.85–1.0): слово/смысл подтверждён грамматически и контекстом
- MEDIUM (0.65–0.84): смысл логичен, но есть альтернативы
- LOW (0.0–0.64): неоднозначно, нужна пометка

ВАЖНО по artistic_ru:
- Оставь пустым "", если буквальный KSD-перевод уже хорош
- Художественный вариант — это не поэзия ради поэзии, а более живой способ выразить тот же смысл
- Никогда не меняй смысл ради красоты звучания

ВАЖНО по context_note (синий блок):
- Только там, где буквальное слово КРИТИЧЕСКИ ведёт в сторону от духовного смысла
- Например: "gavai = петь (букв.) → воспринимать Хукам. Здесь начинается 'переход' по принципу 1."
- Не объяснять очевидное. Не быть снисходительным.
"""


# ─── knowledge DB lookups ─────────────────────────────────────────────────────

def lookup_word(conn: sqlite3.Connection, roman: str) -> list[dict]:
    """Ищет слово в DB по roman. Возвращает список совпадений."""
    cur = conn.cursor()
    roman_clean = roman.strip().lower()
    cur.execute("""
        SELECT roman, literal_ru, ksd_meta_ru, confidence, grammar_note, source
        FROM words
        WHERE roman = ? OR roman LIKE ?
        ORDER BY confidence DESC
        LIMIT 5
    """, (roman_clean, f"%{roman_clean}%"))
    rows = cur.fetchall()
    return [
        {
            "roman": r[0],
            "literal_ru": r[1],
            "ksd_meta_ru": r[2],
            "confidence": r[3],
            "grammar_note": r[4] or "",
            "source": r[5],
        }
        for r in rows
    ]


def get_few_shot_examples(conn: sqlite3.Connection, pauri_nums: list[int] | None = None) -> str:
    """Возвращает few-shot примеры из ksd_examples."""
    cur = conn.cursor()
    if pauri_nums:
        placeholders = ",".join("?" * len(pauri_nums))
        cur.execute(
            f"SELECT pauri_num, word_analysis, ksd_translation FROM ksd_examples "
            f"WHERE pauri_num IN ({placeholders}) AND source='jbani_v2' LIMIT 3",
            pauri_nums
        )
    else:
        cur.execute(
            "SELECT pauri_num, word_analysis, ksd_translation FROM ksd_examples "
            "WHERE source='jbani_v2' LIMIT 3"
        )
    rows = cur.fetchall()
    if not rows:
        return ""

    examples = []
    for row in rows:
        wa = json.loads(row[1])
        wa_text = "\n".join(
            f"  {w['roman']}: [{w['literal']}] → [{w.get('ksd_meta', '')}]"
            for w in wa[:5]
        )
        examples.append(
            f"Паури {row[0]}:\n{wa_text}\nTranslation: {row[2][:200]}"
        )
    return "\n\n".join(examples)


# ─── ang_json loader ─────────────────────────────────────────────────────────

def load_ang(ang_num: int) -> dict | None:
    path = ANG_JSON / f"ang_{ang_num:04d}.json"
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def group_by_shabad(ang_data: dict) -> list[list[dict]]:
    """Группирует строки анга по шабдам (по shabad_id)."""
    from itertools import groupby
    shabads = []
    for _, group in groupby(ang_data["lines"], key=lambda l: l["shabad_id"]):
        shabads.append(list(group))
    return shabads


def find_rahao(lines: list[dict]) -> int | None:
    """Ищет строку Рахао по признакам в гурмукхи."""
    for line in lines:
        gm = line.get("gurmukhi", "")
        if "ਰਹਾਉ" in gm or "ਰਹਾਓ" in gm:
            return line["verse_id"]
    return None


# ─── Claude API call ─────────────────────────────────────────────────────────

def build_user_prompt(
    ang_data: dict,
    shabad_lines: list[dict],
    db_conn: sqlite3.Connection,
    few_shot: str,
) -> str:
    ang = ang_data["ang"]
    shabad_id = shabad_lines[0]["shabad_id"]
    rahao_vid = find_rahao(shabad_lines)

    # DB lookups для каждого слова каждой строки
    word_hints = {}
    for line in shabad_lines:
        roman = line.get("roman", line.get("site_roman", ""))
        for word in roman.split():
            word_clean = re.sub(r"[āīūṭḍṇṛñśṃṅḥ̄]", lambda m: m.group(), word)
            word_clean = re.sub(r"[^a-zA-Z]", "", word_clean).lower()
            if len(word_clean) > 2:
                hits = lookup_word(db_conn, word_clean)
                if hits:
                    word_hints[word_clean] = hits[0]

    hints_text = ""
    if word_hints:
        hints_text = "\n\nПодсказки из базы знаний KSD (roman → literal → KSD-meta):\n"
        for w, h in list(word_hints.items())[:20]:
            hints_text += (
                f"  {w}: [{h['literal_ru']}]"
                + (f" → [{h['ksd_meta_ru'][:60]}]" if h['ksd_meta_ru'] else "")
                + (f" ({h['grammar_note']})" if h['grammar_note'] else "")
                + "\n"
            )

    # Строки шабда
    lines_text = ""
    for line in shabad_lines:
        is_rahao = line["verse_id"] == rahao_vid
        rahao_mark = " ← РАХАО (тема шабда)" if is_rahao else ""
        ss_pa = line.get("sahib_singh_pa", "")
        lines_text += (
            f"  verse_id={line['verse_id']}{rahao_mark}\n"
            f"  gurmukhi:    {line['gurmukhi']}\n"
            f"  roman:       {line.get('roman', line.get('site_roman', ''))}\n"
            f"  sahib_singh: {ss_pa[:200] if ss_pa else '—'}\n\n"
        )

    few_shot_block = ""
    if few_shot:
        few_shot_block = f"\n\nПримеры KSD-разборов из Джап Бани (few-shot):\n{few_shot}\n"

    return f"""Анг: {ang}, Шабд: {shabad_id}
Строк в шабде: {len(shabad_lines)}
Рахао verse_id: {rahao_vid if rahao_vid else 'не найден'}

Строки шабда:
{lines_text}{hints_text}{few_shot_block}

Выполни KSD-анализ и перевод каждой строки строго в указанном выше порядке.
Порядок строк НЕ менять. Все {len(shabad_lines)} строк должны быть в ответе.
"""


def call_claude(
    client: anthropic.Anthropic,
    system_prompt: str,
    user_prompt: str,
    max_retries: int = 3,
) -> dict | None:
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            text = response.content[0].text

            # Извлекаем JSON
            m = re.search(
                r"BEGIN_KSD_JSON\s*(.*?)\s*END_KSD_JSON",
                text, re.DOTALL
            )
            if not m:
                # Попробуем найти JSON напрямую
                m2 = re.search(r"\{.*\}", text, re.DOTALL)
                if m2:
                    raw = m2.group()
                else:
                    print(f"    [WARN] нет JSON в ответе (попытка {attempt+1})")
                    time.sleep(2)
                    continue
            else:
                raw = m.group(1)

            # Чиним кавычки если нужно
            raw = raw.replace('\u201c', '"').replace('\u201d', '"')
            raw = raw.replace('\u00ab', '"').replace('\u00bb', '"')

            return json.loads(raw)

        except json.JSONDecodeError as e:
            print(f"    [WARN] JSON parse error: {e} (попытка {attempt+1})")
            time.sleep(2)
        except anthropic.APIError as e:
            print(f"    [ERROR] API: {e} (попытка {attempt+1})")
            time.sleep(5)

    return None


# ─── DOCX builder ─────────────────────────────────────────────────────────────

def add_shabad_to_doc(doc: Document, result: dict, ang_num: int):
    """Добавляет шабд в docx документ."""
    # Заголовок шабда
    ang_val = result.get("ang", ang_num)
    shabad_id = result.get("shabad_id", "?")
    rahao_theme = result.get("rahao_theme", "")

    p_head = doc.add_paragraph()
    p_head.paragraph_format.space_before = Pt(12)
    run = p_head.add_run(f"Анг {ang_val}")
    run.bold = True
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

    # Тема (Рахао)
    if rahao_theme:
        p_theme = doc.add_paragraph()
        run_t = p_theme.add_run(f"↳ {rahao_theme}")
        run_t.italic = True
        run_t.font.size = Pt(9)
        run_t.font.color.rgb = COLOR_RAHAO

    for line in result.get("lines", []):
        is_rahao = line.get("is_rahao", False)

        # ── Гурмукхи ──
        p_gm = doc.add_paragraph()
        p_gm.paragraph_format.space_before = Pt(6)
        run_gm = p_gm.add_run(line.get("gurmukhi", ""))
        run_gm.font.size = Pt(14)
        run_gm.font.color.rgb = COLOR_GURMUKHI
        if is_rahao:
            run_gm.bold = True

        # ── Романизация ──
        roman = line.get("roman", "")
        if roman:
            p_rm = doc.add_paragraph()
            run_rm = p_rm.add_run(roman)
            run_rm.font.size = Pt(9)
            run_rm.font.color.rgb = COLOR_ROMAN
            run_rm.italic = True

        # ── KSD-перевод ──
        ksd = line.get("ksd_translation", "")
        if ksd:
            p_tr = doc.add_paragraph()
            run_tr = p_tr.add_run(ksd)
            run_tr.font.size = Pt(11)
            run_tr.font.color.rgb = COLOR_TRANSLATION
            if is_rahao:
                run_tr.bold = True

        # ── Художественный вариант (если есть и отличается) ──
        artistic = line.get("artistic_ru", "")
        if artistic and artistic != ksd:
            p_art = doc.add_paragraph()
            run_art = p_art.add_run(f"〜 {artistic}")
            run_art.font.size = Pt(10)
            run_art.font.color.rgb = COLOR_ARTISTIC
            run_art.italic = True

        # ── Синий блок (context note) ──
        ctx = line.get("context_note", "")
        if ctx:
            p_ctx = doc.add_paragraph()
            run_ctx = p_ctx.add_run(ctx)
            run_ctx.font.size = Pt(9)
            run_ctx.font.color.rgb = COLOR_CONTEXT

    # Резюме шабда
    summary = result.get("shabad_summary", "")
    if summary:
        p_sum = doc.add_paragraph()
        p_sum.paragraph_format.space_before = Pt(4)
        run_sum = p_sum.add_run(f"[ {summary} ]")
        run_sum.font.size = Pt(9)
        run_sum.italic = True
        run_sum.font.color.rgb = COLOR_COMMENT

    # Разделитель
    doc.add_paragraph("─" * 40)


# ─── progress ─────────────────────────────────────────────────────────────────

def load_progress() -> set[str]:
    if not PROGRESS_FILE.exists():
        return set()
    return set(PROGRESS_FILE.read_text().splitlines())


def save_progress(done: set[str]):
    PROGRESS_FILE.write_text("\n".join(sorted(done)))


# ─── main pipeline ───────────────────────────────────────────────────────────

def process_shabad(
    client: anthropic.Anthropic,
    system_prompt: str,
    db_conn: sqlite3.Connection,
    ang_data: dict,
    shabad_lines: list[dict],
    few_shot: str,
) -> dict | None:
    """Обрабатывает один шабд."""
    ang = ang_data["ang"]
    shabad_id = shabad_lines[0]["shabad_id"]
    print(f"  → Шабд {shabad_id} ({len(shabad_lines)} строк) …", end=" ", flush=True)

    user_prompt = build_user_prompt(ang_data, shabad_lines, db_conn, few_shot)
    result = call_claude(client, system_prompt, user_prompt)

    if result:
        # Добавляем gurmukhi из оригинала если AI его не вернул
        orig_by_vid = {l["verse_id"]: l for l in shabad_lines}
        for line in result.get("lines", []):
            vid = line.get("verse_id")
            if vid and vid in orig_by_vid:
                if not line.get("gurmukhi"):
                    line["gurmukhi"] = orig_by_vid[vid]["gurmukhi"]
                if not line.get("roman"):
                    line["roman"] = orig_by_vid[vid].get("roman", "")
        result["ang"] = ang
        result["shabad_id"] = shabad_id
        conf = result.get("lines", [{}])
        avg_conf = (
            sum(l.get("confidence", 0.8) for l in conf) / len(conf)
            if conf else 0.8
        )
        badge = "✓✓ HIGH" if avg_conf >= 0.85 else ("✓ MED" if avg_conf >= 0.65 else "? LOW")
        print(f"OK [{badge} {avg_conf:.2f}]")
    else:
        print("FAIL")

    return result


def run(args):
    # Инициализация
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: нужен ANTHROPIC_API_KEY в окружении")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    db_conn = sqlite3.connect(str(DB_PATH))
    system_prompt = build_system_prompt(db_conn)
    few_shot = get_few_shot_examples(db_conn)

    # Определяем список ангов для обработки
    ang_list: list[int] = []
    if args.ang:
        if "-" in str(args.ang):
            a, b = str(args.ang).split("-")
            ang_list = list(range(int(a), int(b) + 1))
        else:
            ang_list = [int(args.ang)]
    elif args.all or args.resume:
        # Все доступные анги
        ang_list = sorted(
            int(p.stem.replace("ang_", ""))
            for p in ANG_JSON.glob("ang_*.json")
        )
    else:
        print("Укажи --ang N, --ang N-M, --all, или --resume")
        sys.exit(1)

    # Прогресс
    done_keys = load_progress()
    if not args.resume:
        done_keys = set()

    # Docx
    if OUTPUT_DOCX.exists() and args.resume:
        doc = Document(str(OUTPUT_DOCX))
    else:
        doc = Document()
        doc.core_properties.title = "СГГС — KSD-перевод"
        # Заголовочный абзац
        p_title = doc.add_paragraph()
        run_title = p_title.add_run("Шри Гуру Грантх Сахиб — KSD-перевод на русский")
        run_title.bold = True
        run_title.font.size = Pt(16)

    # Обработка
    results_log = open(OUTPUT_JSON, "a", encoding="utf-8")

    for ang_num in ang_list:
        ang_data = load_ang(ang_num)
        if not ang_data:
            print(f"  [SKIP] ang {ang_num} — файл не найден")
            continue

        shabads = group_by_shabad(ang_data)
        print(f"\nАнг {ang_num}: {len(shabads)} шабдов")

        for shabad_lines in shabads:
            shabad_id = shabad_lines[0]["shabad_id"]
            key = f"{ang_num}:{shabad_id}"
            if key in done_keys:
                print(f"  → Шабд {shabad_id} [SKIP — уже обработан]")
                continue

            result = process_shabad(
                client, system_prompt, db_conn,
                ang_data, shabad_lines, few_shot
            )

            if result:
                add_shabad_to_doc(doc, result, ang_num)
                results_log.write(json.dumps(result, ensure_ascii=False) + "\n")
                done_keys.add(key)
                save_progress(done_keys)
                doc.save(str(OUTPUT_DOCX))

            time.sleep(0.5)  # Пауза между запросами

    results_log.close()
    db_conn.close()
    print(f"\nГотово. DOCX: {OUTPUT_DOCX}")
    print(f"JSON log:    {OUTPUT_JSON}")


# ─── entry point ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AI KSD Translator для СГГС")
    parser.add_argument("--ang",    help="Анг или диапазон: 1 или 1-8")
    parser.add_argument("--shabad", help="Один шабд по номеру", type=int)
    parser.add_argument("--all",    action="store_true", help="Все анги")
    parser.add_argument("--resume", action="store_true", help="Продолжить с места остановки")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
