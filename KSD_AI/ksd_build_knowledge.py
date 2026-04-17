#!/usr/bin/env python3
"""
ksd_build_knowledge.py

Строит базу знаний ksd_knowledge.db из всех материалов KSD_AI:
  - Джап Бани. Комментарии к переводу (2).docx  → слова + паури-примеры
  - Холст Гуру Нанака.docx / Концепты Сикхи.docx → Nanak Canvas концепты
  - Курс понимания Гурбани 1–4                   → KSD принципы
  - Гурбани грамматика.pdf                         → грамматические правила
  - custom_examples_how_to_work_with_voc.txt        → доп. примеры
  - ksd_reference_material/Джап Бани (1).docx       → доп. разборы
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
from pathlib import Path

# --- пути ---
SCRIPT_DIR = Path(__file__).parent
BASE_DIR    = SCRIPT_DIR.parent
DB_PATH     = SCRIPT_DIR / "ksd_knowledge.db"

KSD_AI = SCRIPT_DIR
REF_MAT = BASE_DIR / "ksd_reference_material"

JBANI_COMMENTS   = KSD_AI / "Джап Бани. Комментарии к переводу. Упрощенное издание (2).docx"
JBANI_REF        = REF_MAT / "Джап Бани. Комментарии к переводу. Упрощенное издание (1).docx"
CANVAS_KSD       = KSD_AI / "Холст Гуру Нанака. Карминдер Сингх Диллон.docx"
CANVAS_COMBINED  = BASE_DIR / "Nanak_Canvas" / "Nanak_Canvas_COMBINED.docx"
CONCEPTS_SIKHI   = KSD_AI / "Концепты Сикхи.docx"
GRAMMAR_PDF      = KSD_AI / "Гурбани грамматика.pdf"
CUSTOM_EXAMPLES  = KSD_AI / "custom_examples_how_to_work_with_voc.txt"
MUNDAVNI         = KSD_AI / "mundavni_example.txt"
SHABADS_WRONGLY  = KSD_AI / "номер_1_из_неправильно_приведенных_шабдов_с_разбором.txt"
AST_DOCX         = KSD_AI / "Джап Джи - Смысловой Перевод. Пример Перевода. Есть отсебятина. Но в целом хорошо. AST.docx"

COURSE_DOCS = [
    KSD_AI / "Курс понимания Гурбани - 1 Переход от буквального к метафорическому (1).docx",
    KSD_AI / "Курс понимания Гурбани - 2 Принцип Рахао (1).docx",
    KSD_AI / "Курс Понимания Гурбани — Часть 3 Контекст (1).docx",
    KSD_AI / "Курс Понимания Гурбани — Часть 4_ Для Себя - целевой принцип (1).docx",
]

# ─── helpers ────────────────────────────────────────────────────────────────

def read_docx(path: Path) -> str:
    """Читает docx → plain text."""
    try:
        from docx import Document
        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        print(f"  [WARN] cannot read {path.name}: {e}", file=sys.stderr)
        return ""


def read_txt(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  [WARN] cannot read {path.name}: {e}", file=sys.stderr)
        return ""


def read_pdf_pages(path: Path, max_pages: int = 123) -> str:
    """Читает PDF через pymupdf."""
    try:
        import fitz
        doc = fitz.open(str(path))
        pages = []
        for i in range(min(max_pages, len(doc))):
            pages.append(doc[i].get_text())
        return "\n".join(pages)
    except Exception as e:
        print(f"  [WARN] cannot read pdf {path.name}: {e}", file=sys.stderr)
        return ""


# ─── DB setup ───────────────────────────────────────────────────────────────

def init_db(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS words (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        gurmukhi    TEXT,           -- ਗਾਵੈ (Gurmukhi Unicode, may be empty if only roman known)
        roman       TEXT NOT NULL,  -- gavai
        literal_ru  TEXT,           -- петь (буквальное)
        ksd_meta_ru TEXT,           -- воспринимать Хукам как… (KSD-метафорическое)
        grammar_note TEXT,          -- Char(aunkard)=м.р.ед.ч.; Char(sihari)=4
        source      TEXT,           -- jbani_v2 / jbani_v1 / custom_example / manual
        confidence  REAL DEFAULT 0.8, -- 0.0–1.0
        notes       TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_words_roman ON words(roman);

    CREATE TABLE IF NOT EXISTS canvas_concepts (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        concept     TEXT NOT NULL,  -- "смерть", "реинкарнация", "Хукам", ...
        traditional TEXT,           -- традиционное/ведическое понимание
        ksd_meaning TEXT NOT NULL,  -- KSD/Nanak переопределение
        gurbani_ref TEXT,           -- ссылка на СГГС если есть
        source      TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_canvas_concept ON canvas_concepts(concept);

    CREATE TABLE IF NOT EXISTS ksd_principles (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        num         INTEGER,        -- 1..8
        title       TEXT,
        description TEXT,
        example_gurbani TEXT,
        example_analysis TEXT,
        source      TEXT
    );

    CREATE TABLE IF NOT EXISTS grammar_rules (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        category    TEXT,           -- "suffix", "ending", "case", "gender", ...
        pattern     TEXT,           -- aunkard / sihari / mukta / ...
        meaning     TEXT,           -- мужской род, единственное число, ...
        example_word TEXT,
        example_meaning TEXT,
        source      TEXT
    );

    CREATE TABLE IF NOT EXISTS ksd_examples (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        ang         INTEGER,
        pauri_num   INTEGER,
        gurmukhi    TEXT,
        roman       TEXT,
        rahao_line  TEXT,           -- строка Рахао
        word_analysis TEXT,         -- JSON: [{word, roman, literal, ksd_meta}]
        ksd_translation TEXT,       -- итоговый KSD-перевод
        context_note TEXT,          -- синий блок — "crossing over"
        principles_used TEXT,       -- JSON: [1, 2, 3]
        source      TEXT
    );

    CREATE TABLE IF NOT EXISTS meta (
        key  TEXT PRIMARY KEY,
        val  TEXT
    );
    """)
    conn.commit()


# ─── extractors ─────────────────────────────────────────────────────────────

# Регекс для разбора строк вида:
#   Gavai- Петь(Lit); Воспринимать Хукам...
#   Gavai Ko Taan- Mощь(Lit); ...
WORD_ANALYSIS_RE = re.compile(
    r"""^([A-Za-zА-Яа-яёЁਅ-ੴ][A-Za-zА-Яа-яёЁਅ-ੴ\s&,/]*?)\s*[-–—]\s*(.+)$""",
    re.MULTILINE,
)

# Буквальное + KSD: "X(Lit); Y" или "X (буквально); Y"
LIT_META_RE = re.compile(
    r"(.+?)\s*[(\[](Lit|буквально|букв|literal)[)\]][\s;:,]+(.+)",
    re.IGNORECASE,
)

# Строки Translation:
TRANS_RE = re.compile(r"^Translation\s*:\s*(.+)$", re.MULTILINE | re.IGNORECASE)


def extract_words_from_jbani(text: str, source: str) -> list[dict]:
    """
    Разбирает текст Джап Бани Комментариев и вытаскивает анализ слов.
    Формат строк: WordRoman- Literal(Lit); KSD_meaning
    """
    words = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Ищем строки вида: "Слово- значение" или "Слово – значение"
        m = re.match(
            r"^([A-Za-zА-Яа-яёЁ][A-Za-zА-Яа-яёЁ\s&',/]{0,50}?)"
            r"\s*[-–—]\s*"
            r"(.{5,}?)$",
            line,
        )
        if m and not line.startswith("http") and len(line) < 300:
            roman_raw = m.group(1).strip()
            rest = m.group(2).strip()

            # Отсекаем служебные строки
            skip_words = {"Translation", "Перевод", "Источник", "Примечание",
                          "Анализ", "Итог", "Смысл", "Текст", "Строка",
                          "Гурбани", "Nanak", "Gunn", "http", "www"}
            if any(roman_raw.startswith(w) for w in skip_words):
                i += 1
                continue
            if re.search(r"[.!?]{2,}", roman_raw):
                i += 1
                continue

            # Разбиваем на literal / ksd_meta
            lit_m = LIT_META_RE.match(rest)
            if lit_m:
                literal = lit_m.group(1).strip()
                ksd_meta = lit_m.group(3).strip()
            else:
                # Попробуем разбить по ";"
                parts = rest.split(";", 1)
                if len(parts) == 2:
                    literal = parts[0].strip()
                    ksd_meta = parts[1].strip()
                else:
                    literal = rest
                    ksd_meta = ""

            words.append({
                "roman": roman_raw.lower(),
                "gurmukhi": "",
                "literal_ru": literal,
                "ksd_meta_ru": ksd_meta,
                "source": source,
                "confidence": 0.85,
            })
        i += 1

    return words


def extract_canvas_concepts(text: str, source: str) -> list[dict]:
    """
    Ищет блоки вида: "Понятие X: традиционный смысл → KSD-смысл"
    из Холст Гуру Нанака / Концепты Сикхи.
    """
    concepts = []
    # Ключевые понятия которые KSD переопределяет
    known_concepts = [
        "смерть", "жизнь после смерти", "реинкарнация", "ава гаун",
        "чаураси лакх", "рай и ад", "мукти", "дарга", "дхарм радж",
        "яма дуты", "читрагупт", "питар", "хукам", "наам", "хоумэ",
        "симран", "джап", "гурбани", "сатнам", "эконкар", "ооангкар",
        "кал", "джам", "нарак", "сург",
    ]
    text_lower = text.lower()
    for concept in known_concepts:
        idx = text_lower.find(concept)
        if idx == -1:
            continue
        # Берём контекст вокруг первого вхождения
        start = max(0, idx - 200)
        end   = min(len(text), idx + 600)
        snippet = text[start:end].strip()
        # Нормализуем
        snippet = re.sub(r"\s+", " ", snippet)
        concepts.append({
            "concept": concept,
            "ksd_meaning": snippet,
            "source": source,
        })
    return concepts


def extract_principles(text: str, source: str) -> list[dict]:
    """
    Извлекает принципы из курсовых документов.
    Ищет паттерны "Принцип N:" или "Урок N:".
    """
    principles = []
    blocks = re.split(
        r"(?:Принцип\s+(\d+)|Урок\s*[-–]?\s*(\d+)|(\d+)\s+(?:принцип|урок))",
        text, flags=re.IGNORECASE
    )

    # Более надёжный подход — ищем заголовки принципов явно
    PRINCIPLE_HEADERS = {
        1: ["буквальн", "переход", "метафор", "crossing over", "literal"],
        2: ["рахао", "рахау", "rahao", "тема шабда", "ключевое послание"],
        3: ["контекст", "context", "окружение"],
        4: ["для себя", "spirituality of the self", "адресат", "целевой принцип"],
        5: ["творец внутри", "creator within", "внутри нас"],
        6: ["здесь и сейчас", "here and now", "не загробн"],
        7: ["гурбани объясняет", "gurbani explains", "перекрёстная ссылка"],
        8: ["грамматика", "grammar", "viakaran", "согласованность смыслов"],
    }

    text_lower = text.lower()
    lines = text.splitlines()

    for num, keywords in PRINCIPLE_HEADERS.items():
        for kw in keywords:
            idx = text_lower.find(kw)
            if idx != -1:
                # Берём абзац
                start = max(0, idx - 50)
                end   = min(len(text), idx + 800)
                snippet = text[start:end].strip()
                snippet = re.sub(r"\s+", " ", snippet)
                principles.append({
                    "num": num,
                    "title": kw,
                    "description": snippet,
                    "source": source,
                })
                break  # нашли один — достаточно для этого принципа

    return principles


def extract_grammar_rules(text: str, source: str) -> list[dict]:
    """
    Из Гурбани Грамматика.pdf вытаскиваем правила суффиксов/окончаний.
    Ищем паттерны вида: "aunkard = мужской род единственного числа"
    """
    rules = []
    # Ищем известные грамматические окончания KSD
    GRAMMAR_PATTERNS = {
        "aunkard": "мужской род, единственное число (u-ending)",
        "mukta":   "множественное число или базовая форма",
        "sihari":  "в пределах / внутри (locative, sihari lavan)",
        "lanvan":  "падежный маркёр принадлежности / инструментальный",
        "bihari":  "женский род / субъект действия",
        "dulanvan": "носовое окончание, смягчение",
    }

    text_lower = text.lower()
    for pattern, meaning in GRAMMAR_PATTERNS.items():
        if pattern in text_lower:
            idx = text_lower.find(pattern)
            start = max(0, idx - 100)
            end   = min(len(text), idx + 500)
            snippet = text[start:end].strip()
            snippet = re.sub(r"\s+", " ", snippet)
            rules.append({
                "category": "ending",
                "pattern": pattern,
                "meaning": meaning,
                "context": snippet[:300],
                "source": source,
            })

    # Явные правила из KSD (из комментариев к Джап Бани)
    # Формат: "Char (aungkar - окончание на u)- единственное число..."
    EXPLICIT_RE = re.compile(
        r"(\w+)\s*\(([^)]+)\)\s*[-–—]\s*([^.\n]{5,80})",
    )
    for m in EXPLICIT_RE.finditer(text):
        word    = m.group(1)
        grammar = m.group(2).strip()
        meaning = m.group(3).strip()
        if any(g in grammar.lower() for g in
               ["aunkard", "sihari", "mukta", "bihari", "aungkar", "окончание"]):
            rules.append({
                "category": "word_form",
                "pattern": f"{word}({grammar})",
                "meaning": meaning,
                "context": "",
                "source": source,
            })

    return rules


def extract_ksd_examples_from_jbani(text: str, source: str) -> list[dict]:
    """
    Извлекает полные паури-примеры: Паури N → анализ → перевод.
    Формат в тексте:
      Паури N — ...
      [строки гурмукхи и транслитерация]
      [word analysis lines]
      Translation: ...
    """
    examples = []

    # Разбиваем по "Паури N"
    pauri_splits = re.split(r"(Паури\s+\d+[^\n]*)", text)

    current_pauri_num = None
    current_block = ""
    for chunk in pauri_splits:
        m = re.match(r"Паури\s+(\d+)", chunk, re.IGNORECASE)
        if m:
            # Сохраняем предыдущий блок
            if current_pauri_num and current_block.strip():
                ex = _parse_pauri_block(
                    current_pauri_num, current_block, source
                )
                if ex:
                    examples.append(ex)
            current_pauri_num = int(m.group(1))
            current_block = chunk
        else:
            current_block += chunk

    # Последний блок
    if current_pauri_num and current_block.strip():
        ex = _parse_pauri_block(current_pauri_num, current_block, source)
        if ex:
            examples.append(ex)

    return examples


def _parse_pauri_block(num: int, block: str, source: str) -> dict | None:
    """Разбирает блок одной паури."""
    # Ищем Translation:
    trans_lines = TRANS_RE.findall(block)
    if not trans_lines:
        return None
    ksd_translation = " | ".join(trans_lines)

    # Ищем word analysis
    word_analysis_lines = []
    for line in block.splitlines():
        line = line.strip()
        m = re.match(
            r"^([A-Za-z][A-Za-z\s&',/]{0,40}?)\s*[-–—]\s*(.{5,200})$",
            line
        )
        if m:
            roman_raw = m.group(1).strip()
            rest = m.group(2).strip()
            skip_words = {"Translation", "Nanak", "Источник", "Перевод"}
            if any(roman_raw.startswith(w) for w in skip_words):
                continue
            if re.search(r"http|www", roman_raw):
                continue
            lit_m = LIT_META_RE.match(rest)
            if lit_m:
                word_analysis_lines.append({
                    "roman": roman_raw.lower(),
                    "literal": lit_m.group(1).strip(),
                    "ksd_meta": lit_m.group(3).strip(),
                })
            else:
                parts = rest.split(";", 1)
                if len(parts) == 2:
                    word_analysis_lines.append({
                        "roman": roman_raw.lower(),
                        "literal": parts[0].strip(),
                        "ksd_meta": parts[1].strip(),
                    })

    if not word_analysis_lines:
        return None

    return {
        "ang": None,
        "pauri_num": num,
        "gurmukhi": "",
        "roman": "",
        "rahao_line": "",
        "word_analysis": json.dumps(word_analysis_lines, ensure_ascii=False),
        "ksd_translation": ksd_translation,
        "context_note": "",
        "principles_used": json.dumps([1, 2, 3]),
        "source": source,
    }


# ─── insert helpers ──────────────────────────────────────────────────────────

def insert_words(conn: sqlite3.Connection, words: list[dict]):
    cur = conn.cursor()
    inserted = 0
    skipped  = 0
    for w in words:
        roman = w["roman"].strip().lower()
        if not roman or len(roman) > 100:
            skipped += 1
            continue
        # Проверка дубликата
        cur.execute(
            "SELECT id FROM words WHERE roman = ? AND source = ?",
            (roman, w["source"])
        )
        if cur.fetchone():
            skipped += 1
            continue
        cur.execute("""
            INSERT INTO words (gurmukhi, roman, literal_ru, ksd_meta_ru, source, confidence)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            w.get("gurmukhi", ""),
            roman,
            w.get("literal_ru", ""),
            w.get("ksd_meta_ru", ""),
            w.get("source", "unknown"),
            w.get("confidence", 0.8),
        ))
        inserted += 1
    conn.commit()
    return inserted, skipped


def insert_concepts(conn: sqlite3.Connection, concepts: list[dict]):
    cur = conn.cursor()
    inserted = 0
    for c in concepts:
        cur.execute(
            "SELECT id FROM canvas_concepts WHERE concept = ? AND source = ?",
            (c["concept"], c.get("source", ""))
        )
        if cur.fetchone():
            continue
        cur.execute("""
            INSERT INTO canvas_concepts (concept, traditional, ksd_meaning, gurbani_ref, source)
            VALUES (?, ?, ?, ?, ?)
        """, (
            c["concept"],
            c.get("traditional", ""),
            c["ksd_meaning"],
            c.get("gurbani_ref", ""),
            c.get("source", ""),
        ))
        inserted += 1
    conn.commit()
    return inserted


def insert_principles(conn: sqlite3.Connection, principles: list[dict]):
    cur = conn.cursor()
    inserted = 0
    for p in principles:
        cur.execute(
            "SELECT id FROM ksd_principles WHERE num = ? AND title = ?",
            (p["num"], p["title"])
        )
        if cur.fetchone():
            continue
        cur.execute("""
            INSERT INTO ksd_principles (num, title, description, source)
            VALUES (?, ?, ?, ?)
        """, (p["num"], p["title"], p["description"], p["source"]))
        inserted += 1
    conn.commit()
    return inserted


def insert_grammar(conn: sqlite3.Connection, rules: list[dict]):
    cur = conn.cursor()
    inserted = 0
    for r in rules:
        cur.execute(
            "SELECT id FROM grammar_rules WHERE pattern = ? AND source = ?",
            (r["pattern"], r["source"])
        )
        if cur.fetchone():
            continue
        cur.execute("""
            INSERT INTO grammar_rules (category, pattern, meaning, example_word, example_meaning, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            r.get("category", ""),
            r["pattern"],
            r["meaning"],
            r.get("example_word", ""),
            r.get("example_meaning", ""),
            r["source"],
        ))
        inserted += 1
    conn.commit()
    return inserted


def insert_examples(conn: sqlite3.Connection, examples: list[dict]):
    cur = conn.cursor()
    inserted = 0
    for e in examples:
        cur.execute(
            "SELECT id FROM ksd_examples WHERE pauri_num = ? AND source = ?",
            (e["pauri_num"], e["source"])
        )
        if cur.fetchone():
            continue
        cur.execute("""
            INSERT INTO ksd_examples
            (ang, pauri_num, gurmukhi, roman, rahao_line, word_analysis,
             ksd_translation, context_note, principles_used, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            e.get("ang"),
            e["pauri_num"],
            e.get("gurmukhi", ""),
            e.get("roman", ""),
            e.get("rahao_line", ""),
            e.get("word_analysis", "[]"),
            e.get("ksd_translation", ""),
            e.get("context_note", ""),
            e.get("principles_used", "[]"),
            e["source"],
        ))
        inserted += 1
    conn.commit()
    return inserted


# ─── main ────────────────────────────────────────────────────────────────────

def run():
    print("=" * 60)
    print("ksd_build_knowledge.py — построение базы знаний KSD")
    print("=" * 60)

    conn = sqlite3.connect(str(DB_PATH))
    init_db(conn)
    print(f"\nDB: {DB_PATH}")

    # ── 1. Джап Бани Комментарии v2 ──────────────────────────────
    print("\n[1] Джап Бани Комментарии (v2) …")
    if JBANI_COMMENTS.exists():
        text = read_docx(JBANI_COMMENTS)
        words = extract_words_from_jbani(text, "jbani_v2")
        ins, skip = insert_words(conn, words)
        print(f"    слова: {ins} добавлено, {skip} пропущено")
        examples = extract_ksd_examples_from_jbani(text, "jbani_v2")
        ins_e = insert_examples(conn, examples)
        print(f"    паури-примеры: {ins_e} добавлено")
        rules = extract_grammar_rules(text, "jbani_v2")
        ins_g = insert_grammar(conn, rules)
        print(f"    грамм. правила: {ins_g} добавлено")
    else:
        print("    [SKIP] файл не найден")

    # ── 2. Джап Бани Комментарии v1 (если есть) ─────────────────
    print("\n[2] Джап Бани Комментарии (v1) …")
    if JBANI_REF.exists():
        text = read_docx(JBANI_REF)
        words = extract_words_from_jbani(text, "jbani_v1")
        ins, skip = insert_words(conn, words)
        print(f"    слова: {ins} добавлено, {skip} пропущено")
        examples = extract_ksd_examples_from_jbani(text, "jbani_v1")
        ins_e = insert_examples(conn, examples)
        print(f"    паури-примеры: {ins_e} добавлено")
    else:
        print("    [SKIP] файл не найден")

    # ── 3. Холст Гуру Нанака (KSD_AI) ───────────────────────────
    print("\n[3] Холст Гуру Нанака (KSD) …")
    if CANVAS_KSD.exists():
        text = read_docx(CANVAS_KSD)
        concepts = extract_canvas_concepts(text, "canvas_ksd")
        ins_c = insert_concepts(conn, concepts)
        print(f"    концепты: {ins_c} добавлено")
    else:
        print("    [SKIP]")

    # ── 4. Nanak Canvas COMBINED (RU) ────────────────────────────
    print("\n[4] Nanak Canvas COMBINED (RU) …")
    if CANVAS_COMBINED.exists():
        text = read_docx(CANVAS_COMBINED)
        concepts = extract_canvas_concepts(text, "canvas_combined_ru")
        ins_c = insert_concepts(conn, concepts)
        print(f"    концепты: {ins_c} добавлено")
        # Доп. слова из Canvas
        words = extract_words_from_jbani(text, "canvas_combined_ru")
        ins, skip = insert_words(conn, words)
        print(f"    слова из Canvas: {ins} добавлено")
    else:
        print("    [SKIP]")

    # ── 5. Концепты Сикхи.docx ───────────────────────────────────
    print("\n[5] Концепты Сикхи …")
    if CONCEPTS_SIKHI.exists():
        text = read_docx(CONCEPTS_SIKHI)
        concepts = extract_canvas_concepts(text, "concepts_sikhi")
        ins_c = insert_concepts(conn, concepts)
        print(f"    концепты: {ins_c} добавлено")
        words = extract_words_from_jbani(text, "concepts_sikhi")
        ins, skip = insert_words(conn, words)
        print(f"    слова: {ins} добавлено")
    else:
        print("    [SKIP]")

    # ── 6. Курс понимания Гурбани 1–4 ────────────────────────────
    print("\n[6] Курс понимания Гурбани (1–4) …")
    total_p = 0
    for i, path in enumerate(COURSE_DOCS, 1):
        if path.exists():
            text = read_docx(path)
            principles = extract_principles(text, f"course_{i}")
            ins_p = insert_principles(conn, principles)
            words = extract_words_from_jbani(text, f"course_{i}")
            ins_w, _ = insert_words(conn, words)
            rules = extract_grammar_rules(text, f"course_{i}")
            ins_g = insert_grammar(conn, rules)
            print(f"    [{i}] {path.name[:50]}: "
                  f"{ins_p} принципов, {ins_w} слов, {ins_g} правил")
            total_p += ins_p
        else:
            print(f"    [{i}] SKIP")
    print(f"    Итого принципов: {total_p}")

    # ── 7. Гурбани Грамматика PDF ─────────────────────────────────
    print("\n[7] Гурбани Грамматика (PDF) …")
    if GRAMMAR_PDF.exists():
        text = read_pdf_pages(GRAMMAR_PDF)
        rules = extract_grammar_rules(text, "grammar_pdf")
        ins_g = insert_grammar(conn, rules)
        print(f"    правила: {ins_g} добавлено")
    else:
        print("    [SKIP]")

    # ── 8. Custom examples ────────────────────────────────────────
    print("\n[8] Custom examples …")
    for path in [CUSTOM_EXAMPLES, MUNDAVNI, SHABADS_WRONGLY]:
        if path.exists():
            text = read_txt(path)
            words = extract_words_from_jbani(text, f"custom_{path.stem}")
            ins, skip = insert_words(conn, words)
            print(f"    {path.name}: {ins} слов")

    # ── 9. AST.docx (пример перевода) ────────────────────────────
    print("\n[9] AST.docx (Смысловой перевод — пример) …")
    if AST_DOCX.exists():
        text = read_docx(AST_DOCX)
        words = extract_words_from_jbani(text, "ast_example")
        ins, skip = insert_words(conn, words)
        print(f"    слова: {ins} добавлено")
        principles = extract_principles(text, "ast_example")
        ins_p = insert_principles(conn, principles)
        print(f"    принципы: {ins_p} добавлено")
    else:
        print("    [SKIP]")

    # ── STATS ─────────────────────────────────────────────────────
    cur = conn.cursor()
    stats = {}
    for tbl in ["words", "canvas_concepts", "ksd_principles",
                "grammar_rules", "ksd_examples"]:
        cur.execute(f"SELECT COUNT(*) FROM {tbl}")
        stats[tbl] = cur.fetchone()[0]

    # Метаданные
    cur.execute("INSERT OR REPLACE INTO meta VALUES ('built_at', datetime('now'))")
    conn.commit()

    print("\n" + "=" * 60)
    print("ИТОГ базы знаний:")
    print(f"  Слова (words):             {stats['words']}")
    print(f"  Концепты Canvas:           {stats['canvas_concepts']}")
    print(f"  Принципы KSD:              {stats['ksd_principles']}")
    print(f"  Грамм. правила:            {stats['grammar_rules']}")
    print(f"  Паури-примеры (few-shot):  {stats['ksd_examples']}")
    print("=" * 60)
    print(f"\nБД сохранена: {DB_PATH}")
    conn.close()


if __name__ == "__main__":
    run()
