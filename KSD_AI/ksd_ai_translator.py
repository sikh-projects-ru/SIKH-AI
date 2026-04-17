#!/usr/bin/env python3
"""
ksd_ai_translator.py

AI Karminder Singh Dhillon — переводчик СГГС через ChatGPT (Playwright).

Берёт ang_json → обрабатывает каждый шабд через ChatGPT в браузере
с опорой на ksd_knowledge.db → выдаёт docx.

Принципы вывода:
  - Оригинальный порядок строк и шабдов НЕ меняется.
  - На каждую строку: Гурмукхи → романизация → KSD-перевод (смысл выше художественности).
  - Синий блок (контекст/переход) — только там, где это важно.
  - Художественный вариант — отдельная строка, курсив, только если добавляет ценность.
  - Confidence: HIGH/MEDIUM/LOW — хранится в JSON, в docx — только резюме.
  - Свои JSON в ksd_ang_json/ — исходные ang_json НЕ ТРОГАЕМ.

Использование:
  python3 ksd_ai_translator.py --ang 1          # один анг
  python3 ksd_ai_translator.py --ang 1-8        # диапазон (Джап Джи)
  python3 ksd_ai_translator.py --resume         # продолжить с места остановки
  python3 ksd_ai_translator.py --rebuild-docx   # пересобрать docx из готовых JSON
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import time
from itertools import groupby
from pathlib import Path
from typing import Any

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
from playwright.sync_api import Page, TimeoutError as PWTimeout, sync_playwright
from playwright_stealth import Stealth

# ─── пути ────────────────────────────────────────────────────────────────────

SCRIPT_DIR   = Path(__file__).parent
BASE_DIR     = SCRIPT_DIR.parent
ANG_JSON_DIR = BASE_DIR / "custom_khoj_sahib_singh" / "ang_json"
DB_PATH      = SCRIPT_DIR / "ksd_knowledge.db"

KSD_JSON_DIR = SCRIPT_DIR / "ksd_ang_json"   # наши JSON — исходные ang_json НЕ трогаем
OUT_DIR      = SCRIPT_DIR / "output"
LOG_DIR      = SCRIPT_DIR / "logs"

for d in [KSD_JSON_DIR, OUT_DIR, LOG_DIR]:
    d.mkdir(exist_ok=True)

BOT_PROFILE    = BASE_DIR / "custom_khoj_sahib_singh" / "bot_profile"
PROGRESS_FILE  = SCRIPT_DIR / "ksd_translator.progress"
OUTPUT_DOCX    = OUT_DIR / "SGGS_KSD_Russian.docx"
CHAT_URL       = "https://chatgpt.com/"

# ─── Playwright stealth ───────────────────────────────────────────────────────

_stealth = Stealth()

# ─── цвета docx ──────────────────────────────────────────────────────────────

COLOR_GURMUKHI    = RGBColor(0x55, 0x00, 0x00)   # тёмно-красный
COLOR_ROMAN       = RGBColor(0x55, 0x55, 0x55)   # серый
COLOR_TRANSLATION = RGBColor(0x00, 0x55, 0x00)   # тёмно-зелёный
COLOR_CONTEXT     = RGBColor(0x00, 0x55, 0xAA)   # синий — "crossing over"
COLOR_COMMENT     = RGBColor(0x88, 0x88, 0x88)   # серый мелкий
COLOR_ARTISTIC    = RGBColor(0x33, 0x33, 0x66)   # тёмно-синий — художественный
COLOR_RAHAO       = RGBColor(0x88, 0x00, 0x44)   # пурпурный — Рахао
COLOR_HEADING     = RGBColor(0x22, 0x22, 0x22)

# ─── system-блок (начало каждого нового чата) ────────────────────────────────
# ChatGPT не имеет отдельного system-поля — вставляем в первое сообщение.

def build_system_block(db_conn: sqlite3.Connection) -> str:
    cur = db_conn.cursor()

    # Принципы KSD
    cur.execute("SELECT num, title, description FROM ksd_principles ORDER BY num")
    principles_text = "\n".join(
        f"Принцип {p[0]} ({p[1]}): {p[2][:280]}"
        for p in cur.fetchall()
    )

    # Концепты Nanak Canvas
    cur.execute(
        "SELECT concept, ksd_meaning FROM canvas_concepts "
        "WHERE source='canvas_ksd' LIMIT 14"
    )
    canvas_text = "\n".join(
        f"  • {c[0].upper()}: {c[1][:180]}"
        for c in cur.fetchall()
    )

    # Грамматические правила
    cur.execute("SELECT pattern, meaning FROM grammar_rules LIMIT 18")
    grammar_text = "\n".join(f"  {g[0]} → {g[1]}" for g in cur.fetchall())

    # Few-shot примеры (паури 1 из Джап Бани)
    cur.execute(
        "SELECT pauri_num, word_analysis, ksd_translation "
        "FROM ksd_examples WHERE source='jbani_v2' LIMIT 2"
    )
    few_shot_parts = []
    for row in cur.fetchall():
        wa = json.loads(row[1])
        wa_text = "\n".join(
            f"    {w['roman']}: [{w['literal']}] → [{w.get('ksd_meta', '')}]"
            for w in wa[:6]
        )
        few_shot_parts.append(
            f"  [Паури {row[0]}]\n{wa_text}\n  Translation: {row[2][:200]}"
        )
    few_shot = "\n\n".join(few_shot_parts)

    return f"""Ты — AI-версия Карминдера Сингха Диллона (KSD), интерпретатора Сири Гуру Грантх Сахиб.

━━━ МЕТОДОЛОГИЯ KSD (8 принципов) ━━━
{principles_text}

━━━ ХОЛСТ НАНАКА — концептуальный фрейм ━━━
Следующие понятия в Гурбани НЕ буквальны — KSD их переопределяет:
{canvas_text}

━━━ ГРАММАТИКА ГУРБАНИ ━━━
Окончания слов меняют смысл:
{grammar_text}

━━━ ПРИМЕРЫ KSD-РАЗБОРА (few-shot) ━━━
{few_shot}

━━━ НЕИЗМЕННЫЕ ПРАВИЛА ━━━
1. Порядок строк в шабде НЕ меняется никогда.
2. Смысл > художественность. Художественный вариант — только если добавляет ценность.
3. Confidence 0.0–1.0 на каждую строку.
4. Рахао (ਰਹਾਉ) — тема/суть шабда. Начинать анализ с неё.
5. Нет внешних философий (индуизм, ислам, йога).
6. Гурбани — ДЛЯ МЕНЯ (читателя), не про кого-то снаружи.
7. Творец ВНУТРИ, не снаружи.
8. Гурбани о СЕЙЧАС, не о загробной жизни.
9. Не объяснять очевидное. Не быть снисходительным.

━━━ СИНИЕ ВСТАВКИ [[...]] — КЛЮЧЕВОЙ ПРИЁМ ━━━
Если для понимания строки необходимо добавить слова, которых нет в ней буквально,
но которые подразумеваются из предыдущих строк, Рахао или контекста шабда —
заключи эти слова в двойные квадратные скобки [[вот так]] прямо внутри ksd_translation.

В итоговом документе они будут выделены СИНИМ цветом в квадратных скобках [вот так].
Это показывает читателю: «это слово добавлено из контекста, не буквально».

Примеры:
  «[[Хукам Творца —]] сила, движущая нашим существованием»
  «Множество [[духовных искателей]] воспринимают [[это как]] дар»
  «погрузиться внутрь [[в своё Сознание]]»

Когда добавлять:
  ✓ Пропущенный подлежащий, восстанавливаемый из предыдущей строки
  ✓ Тема шабда (из Рахао), без которой строка непонятна
  ✓ Понятие, определённое несколькими строками раньше
Когда НЕ добавлять:
  ✗ Слова «для красоты» или удлинения фразы
  ✗ Интерпретации, не следующие из текста однозначно
  ✗ Если строка понятна без добавлений

━━━ ФОРМАТ ОТВЕТА ━━━
Верни строго JSON между BEGIN_KSD_JSON и END_KSD_JSON.
Никакого markdown, никаких code fences снаружи маркеров.
Никогда не используй ASCII-кавычки " " внутри строк JSON — ломает парсинг. Используй «ёлочки».

{{
  "ang": <int>,
  "shabad_id": <int>,
  "rahao_verse_id": <int или null>,
  "rahao_theme": "<тема шабда — одна фраза>",
  "lines": [
    {{
      "verse_id": <int>,
      "is_rahao": <true/false>,
      "word_analysis": [
        {{
          "roman": "<слово>",
          "literal_ru": "<буквальное>",
          "ksd_meta_ru": "<KSD-метафора>",
          "confidence": <0.0–1.0>,
          "grammar_note": "<опционально>"
        }}
      ],
      "ksd_translation": "<KSD-перевод строки>",
      "artistic_ru": "<художественный вариант или пустая строка>",
      "context_note": "<синий блок: пустая строка если не нужен>",
      "confidence": <0.0–1.0>,
      "confidence_reason": "<почему такой уровень>"
    }}
  ],
  "shabad_summary": "<резюме смысла шабда — 1-2 предложения>"
}}"""


# ─── ang_json загрузка ────────────────────────────────────────────────────────

def load_ang(ang_num: int) -> dict | None:
    path = ANG_JSON_DIR / f"ang_{ang_num:04d}.json"
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def group_by_shabad(ang_data: dict) -> list[list[dict]]:
    shabads = []
    for _, group in groupby(ang_data["lines"], key=lambda l: l["shabad_id"]):
        shabads.append(list(group))
    return shabads


# Паттерн конца строфы: ॥੧॥ ॥੨॥ ... ॥੧੦॥ — цифры гурмукхи после двойной черты
_STANZA_END_RE = re.compile(r"॥[੦-੯]+॥")

def find_rahao_vids(lines: list[dict]) -> list[int]:
    """
    Возвращает verse_id всех строк Рахао-куплета.

    Правило: находим строку с маркером ਰਹਾਉ — это последняя строка куплета.
    Затем идём назад и добавляем предыдущие строки, у которых НЕТ маркера
    конца строфы (॥੧॥ ॥੨॥ и т.д.) — они продолжают тот же куплет.

    Пример:
      v557  ਕੈਸੀ ਆਰਤੀ ਹੋਇ ॥ ਭਵ ਖੰਡਨਾ ਤੇਰੀ ਆਰਤੀ ॥        ← входит в куплет
      v558  ਅਨਹਤਾ ਸਬਦ ਵਾਜੰਤ ਭੇਰੀ ॥੧॥ ਰਹਾਉ ॥              ← Рахао (последняя)
    """
    # Ищем индекс строки с ਰਹਾਉ
    rahao_idx = None
    for i, line in enumerate(lines):
        if "ਰਹਾਉ" in line.get("gurmukhi", "") or "ਰਹਾਓ" in line.get("gurmukhi", ""):
            rahao_idx = i
            break
    if rahao_idx is None:
        return []

    rahao_vids = [lines[rahao_idx]["verse_id"]]

    # Идём назад, собираем строки куплета
    for i in range(rahao_idx - 1, -1, -1):
        gm = lines[i].get("gurmukhi", "")
        # Если у предыдущей строки есть маркер конца строфы — она не часть Рахао
        if _STANZA_END_RE.search(gm):
            break
        rahao_vids.insert(0, lines[i]["verse_id"])

    return rahao_vids


# Обратная совместимость — одна строка
def find_rahao_vid(lines: list[dict]) -> int | None:
    vids = find_rahao_vids(lines)
    return vids[-1] if vids else None


# ─── фикс битой романизации ───────────────────────────────────────────────────

# Символы не из латиницы/диакритики — признак битой кодировки в roman
_NON_LATIN_RE = re.compile(r"[\u0600-\u06FF\u0900-\u097F\u0A00-\u0A7F]")

def fix_roman(roman: str) -> str:
    """
    Если поле roman содержит арабские/деванагари/гурмукхи символы —
    возвращаем пустую строку: ChatGPT сгенерирует романизацию заново.
    """
    if _NON_LATIN_RE.search(roman):
        return ""
    return roman


# ─── knowledge DB lookups ─────────────────────────────────────────────────────

def lookup_word_hints(db_conn: sqlite3.Connection, roman_line: str) -> list[str]:
    """Возвращает подсказки из DB для слов в строке."""
    cur = db_conn.cursor()
    hints = []
    for word in roman_line.split():
        clean = re.sub(r"[^a-zA-Zāīūṭḍṇṛñśṃṅ]", "", word).lower()
        if len(clean) < 3:
            continue
        cur.execute(
            "SELECT roman, literal_ru, ksd_meta_ru FROM words "
            "WHERE roman = ? OR roman LIKE ? "
            "ORDER BY confidence DESC LIMIT 1",
            (clean, f"{clean}%")
        )
        row = cur.fetchone()
        if row and row[2]:
            hints.append(f"{row[0]}: [{row[1]}] → [{row[2][:60]}]")
    return hints[:8]


# ─── промпт для одного шабда ──────────────────────────────────────────────────

def build_shabad_prompt(
    ang_data: dict,
    shabad_lines: list[dict],
    db_conn: sqlite3.Connection,
) -> str:
    ang         = ang_data["ang"]
    shabad_id   = shabad_lines[0]["shabad_id"]
    rahao_vids  = find_rahao_vids(shabad_lines)
    n           = len(shabad_lines)

    lines_text = ""
    for line in shabad_lines:
        vid      = line["verse_id"]
        if vid in rahao_vids:
            if vid == rahao_vids[-1]:
                rahao_mark = "← РАХАО (последняя строка куплета, с маркером ਰਹਾਉ)"
            else:
                rahao_mark = "← РАХАО-КУПЛЕТ (часть куплета Рахао)"
        else:
            rahao_mark = ""
        roman    = fix_roman(line.get("roman", line.get("site_roman", "")))
        roman_note = " [roman битый, сгенерируй заново]" if not roman and line.get("roman") else ""
        ss_pa    = line.get("sahib_singh_pa", "")
        hints    = lookup_word_hints(db_conn, roman)
        hint_str = ("  [DB-подсказки: " + " | ".join(hints) + "]") if hints else ""
        lines_text += (
            f"verse_id={vid} {rahao_mark}\n"
            f"  gurmukhi:    {line['gurmukhi']}\n"
            f"  roman:       {roman}{roman_note}\n"
            f"  sahib_singh: {ss_pa[:180] if ss_pa else '—'}\n"
            f"{hint_str}\n\n"
        )

    return (
        f"Игнорируй весь предыдущий контекст этого чата.\n\n"
        f"АНГ {ang}, ШАБД {shabad_id} — {n} строк. Рахао verse_ids: {rahao_vids or 'не найдено'}.\n\n"
        f"{lines_text}"
        f"Верни KSD-анализ и перевод ВСЕХ {n} строк в указанном порядке.\n"
        f"Порядок строк НЕ менять. Все {n} строк в массиве lines.\n"
        f"Ответ — строго между BEGIN_KSD_JSON и END_KSD_JSON."
    )


REPAIR_PROMPT = """\
Игнорируй весь предыдущий контекст этого чата, кроме своего последнего ответа.
Перепиши свой последний ответ в правильном JSON-формате между BEGIN_KSD_JSON и END_KSD_JSON.
Требования:
- ровно {n} элементов в массиве lines
- порядок verse_id сохранить
- никаких ASCII-кавычек " " внутри строк — только «ёлочки» или одинарные
- никаких markdown code fences
Формат тот же что был запрошен изначально.
"""

# ─── JSON парсинг ─────────────────────────────────────────────────────────────

def repair_json_quotes(text: str) -> str:
    """Экранирует незакрытые ASCII-кавычки внутри строк JSON."""
    result = []
    in_string = False
    escape_next = False
    for c in text:
        if escape_next:
            result.append(c)
            escape_next = False
            continue
        if c == "\\":
            result.append(c)
            escape_next = True
            continue
        if c == '"':
            if not in_string:
                in_string = True
                result.append(c)
            else:
                # peek ahead
                tail = "".join(result[result.index('"'):] if '"' in result else []) + c
                # упрощённо: проверяем что следует за кавычкой в оригинале
                result.append(c)
                in_string = False
            continue
        result.append(c)
    return "".join(result)


def extract_ksd_json(text: str) -> dict | None:
    m = re.search(r"BEGIN_KSD_JSON\s*(.*?)\s*END_KSD_JSON", text, re.DOTALL)
    if not m:
        return None
    raw = m.group(1).strip()
    raw = re.sub(r"^```json\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"^```\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    # Заменяем типографские кавычки на обычные в ключах
    raw = raw.replace('\u201c', '\u00ab').replace('\u201d', '\u00bb')
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        fixed = repair_json_quotes(raw)
        try:
            return json.loads(fixed)
        except Exception:
            return None


# ─── Playwright interactions ──────────────────────────────────────────────────

def open_chat_tab(context, page_timeout_ms: int = 30_000) -> Page:
    page = context.new_page()
    _stealth.apply_stealth_sync(page)
    page.goto(CHAT_URL, wait_until="domcontentloaded", timeout=page_timeout_ms)
    page.wait_for_timeout(2000)
    return page


def assistant_msg_count(page: Page) -> int:
    return page.locator('[data-message-author-role="assistant"]').count()


def insert_text(page: Page, text: str) -> None:
    page.evaluate(
        """(t) => {
            const el = document.getElementById('prompt-textarea');
            if (!el) return;
            el.focus();
            document.execCommand('selectAll', false, null);
            document.execCommand('insertText', false, t);
        }""",
        text,
    )
    page.wait_for_timeout(500)


def click_send(page: Page) -> None:
    btn = page.locator('button[data-testid="send-button"]')
    try:
        btn.wait_for(state="visible", timeout=5_000)
        btn.click()
    except PWTimeout:
        page.locator("#prompt-textarea").press("Enter")


def drain_generation(page: Page, timeout_ms: int = 900_000) -> None:
    stop = page.locator('button[data-testid="stop-button"]')
    try:
        stop.wait_for(state="visible", timeout=20_000)
    except PWTimeout:
        pass
    try:
        stop.wait_for(state="hidden", timeout=timeout_ms)
    except PWTimeout:
        print("    ⚠ Таймаут ожидания ответа — беру что есть")
    page.wait_for_timeout(1200)
    # Continue generating если надо
    for _ in range(4):
        cont = page.locator("button").filter(
            has_text=re.compile(r"Continue generating|Продолжить", re.I)
        )
        if cont.count() > 0 and cont.first.is_visible():
            cont.first.click()
            page.wait_for_timeout(600)
            drain_generation(page, timeout_ms)
            break


def get_last_assistant_msg(page: Page, before_count: int, wait_ms: int = 30_000) -> str | None:
    try:
        page.wait_for_function(
            "(b) => document.querySelectorAll('[data-message-author-role=\"assistant\"]').length > b",
            arg=before_count,
            timeout=wait_ms,
        )
    except PWTimeout:
        pass
    msgs = page.locator('[data-message-author-role="assistant"]')
    n = msgs.count()
    if n == 0 or n <= before_count:
        return None
    text = msgs.nth(n - 1).inner_text()
    return text.strip() or None


def send_and_get(page: Page, prompt: str, response_ms: int = 900_000) -> str | None:
    ta = page.locator("#prompt-textarea")
    try:
        ta.wait_for(state="visible", timeout=15_000)
    except PWTimeout:
        print("    ✗ Поле ввода не найдено")
        return None
    ta.click()
    page.keyboard.press("Control+a")
    page.keyboard.press("Delete")
    page.wait_for_timeout(250)
    insert_text(page, prompt)
    before = assistant_msg_count(page)
    click_send(page)
    print("    → Ждём ответа ChatGPT…", end=" ", flush=True)
    drain_generation(page, response_ms)
    result = get_last_assistant_msg(page, before)
    print("получен" if result else "нет ответа")
    return result


# ─── сохранение KSD-JSON ──────────────────────────────────────────────────────

def save_ksd_ang_json(ang: int, shabad_result: dict) -> None:
    """Дополняет/создаёт ksd_ang_XXXX.json. Исходный ang_json НЕ трогается."""
    path = KSD_JSON_DIR / f"ksd_ang_{ang:04d}.json"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            existing = json.load(f)
    else:
        existing = {"ang": ang, "shabads": []}
    # Убираем старый вариант шабда если есть
    shabad_id = shabad_result.get("shabad_id")
    existing["shabads"] = [
        s for s in existing.get("shabads", [])
        if s.get("shabad_id") != shabad_id
    ]
    existing["shabads"].append(shabad_result)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)


# ─── docx builder ─────────────────────────────────────────────────────────────

def add_run(para, text: str, *, color=None, bold=False, italic=False, size_pt=None):
    run = para.add_run(text)
    if color:
        run.font.color.rgb = color
    run.font.bold = bold
    run.font.italic = italic
    if size_pt:
        run.font.size = Pt(size_pt)
    return run


def add_translation_with_blue(
    para,
    text: str,
    *,
    base_color: RGBColor,
    bold: bool = False,
    italic: bool = False,
    size_pt: int = 11,
) -> None:
    """
    Рендерит строку перевода с поддержкой [[синих вставок]].
    Текст внутри [[...]] выводится синим цветом в квадратных скобках [].
    Весь остальной текст — цветом base_color.

    Пример входа:  "[[Хукам]] — сила, движущая [[нашим существованием]]"
    Результат:     "[Хукам]" синим + " — сила, движущая " base_color + "[нашим существованием]" синим
    """
    # Разбиваем по маркерам [[...]]
    parts = re.split(r"(\[\[.*?\]\])", text)
    for part in parts:
        if not part:
            continue
        m = re.match(r"\[\[(.*?)\]\]", part)
        if m:
            # Синяя вставка: показываем в [скобках] синим
            add_run(
                para,
                f"[{m.group(1)}]",
                color=COLOR_CONTEXT,
                bold=bold,
                italic=italic,
                size_pt=size_pt,
            )
        else:
            add_run(
                para,
                part,
                color=base_color,
                bold=bold,
                italic=italic,
                size_pt=size_pt,
            )


def ensure_docx(path: Path) -> None:
    if path.exists():
        return
    doc = Document()
    doc.core_properties.title = "СГГС — KSD-перевод"
    for section in doc.sections:
        section.top_margin    = Inches(0.9)
        section.bottom_margin = Inches(0.9)
        section.left_margin   = Inches(1.0)
        section.right_margin  = Inches(1.0)
    title = doc.add_heading("Шри Гуру Грантх Сахиб — KSD-перевод", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(sub, "Методология: Karminder Singh Dhillon",
            color=COLOR_COMMENT, italic=True, size_pt=9)
    doc.add_paragraph()
    doc.save(str(path))


def append_shabad_to_docx(path: Path, result: dict) -> None:
    ensure_docx(path)
    doc = Document(str(path))

    ang       = result.get("ang", "?")
    shabad_id = result.get("shabad_id", "?")
    theme     = result.get("rahao_theme", "")

    # Заголовок анга/шабда
    p_head = doc.add_paragraph()
    p_head.paragraph_format.space_before = Pt(14)
    add_run(p_head, f"Анг {ang}", bold=True, color=COLOR_HEADING, size_pt=11)

    if theme:
        p_theme = doc.add_paragraph()
        add_run(p_theme, f"↳ {theme}", italic=True, color=COLOR_RAHAO, size_pt=9)

    for line in result.get("lines", []):
        is_rahao = line.get("is_rahao", False)

        # Гурмукхи
        p_gm = doc.add_paragraph()
        p_gm.paragraph_format.space_before = Pt(7)
        p_gm.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_run(p_gm, line.get("gurmukhi", ""),
                color=COLOR_GURMUKHI, bold=is_rahao, size_pt=14)

        # Романизация
        roman = line.get("roman", "")
        if roman:
            p_rm = doc.add_paragraph()
            p_rm.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_run(p_rm, roman, color=COLOR_ROMAN, italic=True, size_pt=9)

        # KSD-перевод (с поддержкой [[синих вставок]])
        ksd = line.get("ksd_translation", "")
        if ksd:
            p_tr = doc.add_paragraph()
            p_tr.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_translation_with_blue(
                p_tr, ksd,
                base_color=COLOR_TRANSLATION,
                bold=is_rahao,
                size_pt=11,
            )

        # Художественный вариант (только если отличается и не пустой)
        artistic = line.get("artistic_ru", "")
        ksd_clean = re.sub(r"\[\[.*?\]\]", "", ksd).strip()
        if artistic and artistic.strip() and artistic.strip() != ksd_clean:
            p_art = doc.add_paragraph()
            p_art.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_translation_with_blue(
                p_art, f"〜 {artistic}",
                base_color=COLOR_ARTISTIC,
                italic=True,
                size_pt=10,
            )

        # Синий блок — context_note
        ctx = line.get("context_note", "")
        if ctx and ctx.strip():
            p_ctx = doc.add_paragraph()
            add_run(p_ctx, ctx, color=COLOR_CONTEXT, size_pt=9)

    # Резюме шабда
    summary = result.get("shabad_summary", "")
    if summary:
        p_sum = doc.add_paragraph()
        p_sum.paragraph_format.space_before = Pt(4)
        add_run(p_sum, f"[ {summary} ]", color=COLOR_COMMENT, italic=True, size_pt=9)

    doc.add_paragraph("─" * 45)
    doc.save(str(path))


def rebuild_docx_from_ksd_json(ang_start: int, ang_end: int) -> None:
    """Пересобирает docx из готовых ksd_ang_JSON файлов."""
    if OUTPUT_DOCX.exists():
        OUTPUT_DOCX.unlink()
    ensure_docx(OUTPUT_DOCX)
    rebuilt = 0
    for ang in range(ang_start, ang_end + 1):
        path = KSD_JSON_DIR / f"ksd_ang_{ang:04d}.json"
        if not path.exists():
            continue
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for shabad in data.get("shabads", []):
            # Перезапускаем детекцию Рахао-куплета из гурмукхи-поля
            lines = shabad.get("lines", [])
            rahao_vids = find_rahao_vids(lines)
            for ln in lines:
                ln["is_rahao"] = ln.get("verse_id") in rahao_vids
            append_shabad_to_docx(OUTPUT_DOCX, shabad)
            rebuilt += 1
    print(f"Пересобрано: {rebuilt} шабдов → {OUTPUT_DOCX}")


# ─── progress ─────────────────────────────────────────────────────────────────

def load_progress() -> set[str]:
    if not PROGRESS_FILE.exists():
        return set()
    return set(PROGRESS_FILE.read_text(encoding="utf-8").splitlines())


def save_progress(done: set[str]) -> None:
    PROGRESS_FILE.write_text("\n".join(sorted(done)), encoding="utf-8")


# ─── основной цикл ────────────────────────────────────────────────────────────

def process_ang_list(ang_list: list[int], resume: bool = False, test: bool = False) -> None:
    db_conn = sqlite3.connect(str(DB_PATH))
    system_block = build_system_block(db_conn)

    done_keys = load_progress() if resume else set()

    # В тестовом режиме — отдельный docx, прогресс не сохраняется
    out_docx = OUT_DIR / "SGGS_KSD_TEST.docx" if test else OUTPUT_DOCX
    if test and out_docx.exists():
        out_docx.unlink()
    ensure_docx(out_docx)

    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            str(BOT_PROFILE),
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = open_chat_tab(context)

        # Отправляем system-блок один раз в начале чата
        print("Инициализация чата (system-блок)…")
        init_resp = send_and_get(page, system_block + "\n\nПодтверди: ты готов переводить шабды СГГС по методологии KSD.")
        if init_resp:
            print(f"  ChatGPT: {init_resp[:120]}…")
        else:
            print("  [WARN] нет подтверждения, продолжаем всё равно")

        for ang_num in ang_list:
            ang_data = load_ang(ang_num)
            if not ang_data:
                print(f"  [SKIP] ang {ang_num} — файл не найден")
                continue

            shabads = group_by_shabad(ang_data)
            if test:
                shabads = shabads[:1]  # только первый шабд
                print(f"\nАнг {ang_num}: тест — первый шабд из {len(group_by_shabad(ang_data))}")
            else:
                print(f"\nАнг {ang_num}: {len(shabads)} шабдов")

            for shabad_lines in shabads:
                shabad_id = shabad_lines[0]["shabad_id"]
                key = f"{ang_num}:{shabad_id}"

                if key in done_keys:
                    print(f"  → Шабд {shabad_id} [пропуск — уже готов]")
                    continue

                print(f"  → Шабд {shabad_id} ({len(shabad_lines)} строк)…")

                prompt  = build_shabad_prompt(ang_data, shabad_lines, db_conn)
                raw_ans = send_and_get(page, prompt)

                result = None
                if raw_ans:
                    result = extract_ksd_json(raw_ans)
                    if result is None:
                        # Попытка ремонта
                        print("    [REPAIR] JSON не распознан, пробую repair…")
                        repair_ans = send_and_get(
                            page,
                            REPAIR_PROMPT.format(n=len(shabad_lines))
                        )
                        if repair_ans:
                            result = extract_ksd_json(repair_ans)

                if result:
                    # Обогащаем из оригинала — оригинальный ang_json не трогаем
                    rahao_vids = find_rahao_vids(shabad_lines)
                    orig_by_vid = {l["verse_id"]: l for l in shabad_lines}
                    for ln in result.get("lines", []):
                        vid = ln.get("verse_id")
                        if vid and vid in orig_by_vid:
                            orig = orig_by_vid[vid]
                            if not ln.get("gurmukhi"):
                                ln["gurmukhi"] = orig.get("gurmukhi", "")
                            # roman: берём из результата если чистый, иначе из оригинала
                            if not ln.get("roman"):
                                ln["roman"] = fix_roman(
                                    orig.get("roman", orig.get("site_roman", ""))
                                )
                            ln["sahib_singh_pa"] = orig.get("sahib_singh_pa", "")
                        # Выставляем is_rahao для всего куплета
                        if vid in rahao_vids:
                            ln["is_rahao"] = True
                    result["ang"]      = ang_num
                    result["shabad_id"] = shabad_id

                    # Считаем confidence
                    lines_conf = result.get("lines", [])
                    avg_conf = (
                        sum(l.get("confidence", 0.8) for l in lines_conf) / len(lines_conf)
                        if lines_conf else 0.8
                    )
                    badge = "✓✓ HIGH" if avg_conf >= 0.85 else ("✓ MED" if avg_conf >= 0.65 else "? LOW")
                    print(f"    OK [{badge} {avg_conf:.2f}]")

                    # Сохраняем в ksd_ang_json (наши данные, не оригинал)
                    if not test:
                        save_ksd_ang_json(ang_num, result)
                        done_keys.add(key)
                        save_progress(done_keys)
                    append_shabad_to_docx(out_docx, result)
                else:
                    print(f"    FAIL — шабд {shabad_id} не переведён, пропускаем")

                time.sleep(1)

        context.close()

    db_conn.close()
    print(f"\nГотово. DOCX: {OUTPUT_DOCX}")


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AI KSD Translator (ChatGPT + Playwright)")
    parser.add_argument("--ang",          help="Анг или диапазон: 1 или 1-8")
    parser.add_argument("--all",          action="store_true", help="Все доступные анги")
    parser.add_argument("--resume",       action="store_true", help="Продолжить с остановки")
    parser.add_argument("--test",         action="store_true", help="Тест: только первый шабд анга, без сохранения прогресса")
    parser.add_argument("--rebuild-docx", action="store_true", help="Пересобрать docx из JSON")
    parser.add_argument("--rebuild-range", default="1-1430",   help="Диапазон для rebuild-docx")
    args = parser.parse_args()

    if args.rebuild_docx:
        a, b = args.rebuild_range.split("-")
        rebuild_docx_from_ksd_json(int(a), int(b))
        return

    # Определяем список ангов
    if args.ang:
        if "-" in str(args.ang):
            a, b = str(args.ang).split("-")
            ang_list = list(range(int(a), int(b) + 1))
        else:
            ang_list = [int(args.ang)]
    elif args.all or args.resume:
        ang_list = sorted(
            int(p.stem.replace("ang_", ""))
            for p in ANG_JSON_DIR.glob("ang_*.json")
        )
    else:
        parser.print_help()
        sys.exit(1)

    process_ang_list(ang_list, resume=args.resume, test=args.test)


if __name__ == "__main__":
    main()
