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
from xml.etree import ElementTree as ET
from zipfile import ZipFile

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

def read_docx_xml(path: Path) -> str:
    """Читает docx через XML, включая таблицы в порядке документа."""
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with ZipFile(path) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    body = root.find("w:body", ns)
    if body is None:
        return ""

    lines: list[str] = []

    def text_from(node: ET.Element) -> str:
        return "".join(t.text for t in node.findall(".//w:t", ns) if t.text).strip()

    for child in body:
        if child.tag == f"{{{ns['w']}}}p":
            line = text_from(child)
            if line:
                lines.append(line)
        elif child.tag == f"{{{ns['w']}}}tbl":
            for row in child.findall("./w:tr", ns):
                cells = []
                for cell in row.findall("./w:tc", ns):
                    cell_text = text_from(cell)
                    if cell_text:
                        cells.append(cell_text)
                if cells:
                    lines.append("\t".join(cells))

    return "\n".join(lines)


def read_docx(path: Path) -> str:
    """Читает docx → plain text."""
    try:
        return read_docx_xml(path)
    except Exception as xml_e:
        pass

    try:
        from docx import Document
        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        print(f"  [WARN] cannot read {path.name}: {xml_e}; fallback failed: {e}", file=sys.stderr)
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


def split_real_jbani_pauri_blocks(text: str) -> list[tuple[int, str]]:
    """
    Делит большой комментарий Джап Бани на реальные рабочие блоки Pauree N.
    Игнорирует верхнее оглавление, где Pauree 1..38 перечислены подряд без содержания.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    blocks: list[tuple[int, str]] = []

    starts: list[tuple[int, int]] = []
    for i, line in enumerate(lines):
        m = re.match(r"Pauree\s+(\d+)\:?", line, re.IGNORECASE)
        if not m:
            continue
        pauri_num = int(m.group(1))
        window = "\n".join(lines[i + 1:i + 18])
        if "Translation:" not in window and "Перевод:" not in window:
            continue
        starts.append((i, pauri_num))

    for idx, (start_i, pauri_num) in enumerate(starts):
        end_i = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines)
        block = "\n".join(lines[start_i:end_i]).strip()
        blocks.append((pauri_num, block))

    return blocks


def extract_words_from_jbani_pauri_blocks(text: str, source: str) -> list[dict]:
    """
    Извлекает словарные строки из реальных Pauree-блоков большого комментария.
    Формат:
      Term- значение (Lit); KSD meaning
      Translation: ...
    """
    words: list[dict] = []
    for pauri_num, block in split_real_jbani_pauri_blocks(text):
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith("Translation:") or line.startswith("Перевод:"):
                continue
            m = re.match(r"^([A-Za-zА-Яа-яёЁ][A-Za-zА-Яа-яёЁ0-9\s&',/().+-]{0,80}?)\s*[-–—]\s*(.{3,300})$", line)
            if not m:
                continue

            term = m.group(1).strip()
            rest = m.group(2).strip()

            skip_prefixes = {
                "Pauree", "Translation", "Перевод", "Дополнительно", "Примечание",
                "Комментарии", "Примерный перевод", "Q:", "SGGS", "http",
            }
            if any(term.startswith(prefix) for prefix in skip_prefixes):
                continue
            if len(term) > 100 or "II" == term.strip():
                continue

            lit_m = LIT_META_RE.match(rest)
            if lit_m:
                literal = lit_m.group(1).strip()
                ksd_meta = lit_m.group(3).strip()
            else:
                parts = rest.split(";", 1)
                if len(parts) == 2:
                    literal = parts[0].strip()
                    ksd_meta = parts[1].strip()
                else:
                    literal = rest
                    ksd_meta = ""

            words.append({
                "roman": term.lower(),
                "gurmukhi": "",
                "literal_ru": literal,
                "ksd_meta_ru": ksd_meta,
                "source": source,
                "confidence": 0.9,
                "notes": f"pauri={pauri_num}",
            })
    return words


def extract_examples_from_jbani_pauri_blocks(text: str, source: str) -> list[dict]:
    """
    Поднимает pauri-level examples из большого комментария:
    один блок Pauree N -> много Translation-строк, объединённых в few-shot пример.
    """
    examples: list[dict] = []
    for pauri_num, block in split_real_jbani_pauri_blocks(text):
        translations = []
        roman_lines = []
        for line in block.splitlines():
            line = line.strip()
            if line.startswith("Translation:"):
                translations.append(line.replace("Translation:", "", 1).strip())
            elif line.startswith("Перевод:"):
                translations.append(line.replace("Перевод:", "", 1).strip())
            elif re.match(r"^[A-Za-z][A-Za-z0-9\s&',/().+-]{3,120}$", line) and "Translation" not in line:
                roman_lines.append(line)

        word_rows = []
        for line in block.splitlines():
            line = line.strip()
            m = re.match(r"^([A-Za-z][A-Za-z0-9\s&',/().+-]{0,80}?)\s*[-–—]\s*(.{3,300})$", line)
            if not m or line.startswith("Translation:") or line.startswith("Перевод:"):
                continue
            term = m.group(1).strip()
            rest = m.group(2).strip()
            parts = rest.split(";", 1)
            literal = parts[0].strip()
            ksd_meta = parts[1].strip() if len(parts) == 2 else ""
            word_rows.append({
                "roman": term.lower(),
                "literal": literal,
                "ksd_meta": ksd_meta,
            })

        if translations:
            examples.append({
                "ang": 1,
                "pauri_num": pauri_num,
                "gurmukhi": "",
                "roman": " | ".join(roman_lines[:8]),
                "rahao_line": "",
                "word_analysis": json.dumps(word_rows[:20], ensure_ascii=False),
                "ksd_translation": " | ".join(translations)[:2000],
                "context_note": "",
                "principles_used": json.dumps([1, 2, 3, 4, 5, 6, 7, 8], ensure_ascii=False),
                "source": source,
            })
    return examples


def extract_ast_glossary_words(text: str, source: str) -> list[dict]:
    """
    Извлекает словарь терминов из AST.docx.
    Ожидаемый формат:
      Слово
      Синонимы
      Толкования
      <term>
      <synonyms>
      <meaning line 1>
      <meaning line 2> ...
      <next term>
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for i, line in enumerate(lines):
        cols = [col.strip() for col in line.split("\t")]
        if cols[:3] != ["Слово", "Синонимы", "Толкования"]:
            continue

        words = []
        for row in lines[i + 1:]:
            cols = [col.strip() for col in row.split("\t")]
            if len(cols) < 3:
                break
            term, synonyms, meaning = cols[0], cols[1], " ".join(cols[2:])
            if re.search(r"[\u0A00-\u0A7F]", term):
                break
            if not term or not synonyms or len(meaning) < 10:
                continue
            words.append({
                "roman": term.lower(),
                "gurmukhi": "",
                "literal_ru": synonyms,
                "ksd_meta_ru": re.sub(r"\s+", " ", meaning).strip(),
                "source": source,
                "confidence": 0.88,
            })
        return words

    start = None
    for i in range(len(lines) - 2):
        if lines[i] == "Слово" and lines[i + 1] == "Синонимы" and lines[i + 2] == "Толкования":
            start = i + 3
            break
    if start is None:
        return []

    def is_stop(line: str) -> bool:
        lower = line.lower()
        return lower.startswith("кратко о методике") or lower.startswith("принцип 1")

    def looks_like_entry_start(idx: int) -> bool:
        if idx + 2 >= len(lines):
            return False
        term = lines[idx]
        synonyms = lines[idx + 1]
        meaning = lines[idx + 2]
        if is_stop(term):
            return False
        if len(term) > 90 or len(term) < 2:
            return False
        if len(synonyms) > 220 or len(synonyms) < 2:
            return False
        if len(meaning) < 10:
            return False
        if term.endswith((".", ";", ":", "?", "!", "…")):
            return False
        return True

    words = []
    i = start
    while i + 2 < len(lines):
        if is_stop(lines[i]):
            break
        if not looks_like_entry_start(i):
            i += 1
            continue

        term = lines[i]
        synonyms = lines[i + 1]
        meaning_parts = [lines[i + 2]]
        i += 3

        while i < len(lines):
            if is_stop(lines[i]):
                break
            if looks_like_entry_start(i):
                break
            meaning_parts.append(lines[i])
            i += 1

        meaning = re.sub(r"\s+", " ", " ".join(meaning_parts)).strip()
        words.append({
            "roman": term.lower(),
            "gurmukhi": "",
            "literal_ru": synonyms.strip(),
            "ksd_meta_ru": meaning,
            "source": source,
            "confidence": 0.88,
        })

    return words


def extract_ast_examples(text: str, source: str) -> list[dict]:
    """
    Извлекает примеры/строфы из AST.docx по шаблону:
      [header with pauri]
      <gurmukhi line>
      <roman line>
      <1..N lines русского перевода/комментария>
    Используется как дополнительный few-shot/контекстный корпус.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    examples = []
    current_pauri = None
    example_seq = 0
    i = 0

    def is_gurmukhi(s: str) -> bool:
        return bool(re.search(r"[\u0A00-\u0A7F]", s))

    def is_roman_line(s: str) -> bool:
        return bool(re.search(r"[A-Za-z]", s)) and not bool(re.search(r"[А-Яа-яЁё]", s))

    def is_header(s: str) -> bool:
        return bool(re.match(r"(?:Pauree|Pauri|Паури)\s+(\d+)", s, re.IGNORECASE))

    while i < len(lines):
        line = lines[i]
        m = re.match(r"(?:Pauree|Pauri|Паури)\s+(\d+)", line, re.IGNORECASE)
        if m:
            current_pauri = int(m.group(1))
            i += 1
            continue

        if not is_gurmukhi(line):
            i += 1
            continue

        gm_lines = [line]
        j = i + 1
        while j < len(lines) and is_gurmukhi(lines[j]):
            gm_lines.append(lines[j])
            j += 1

        roman_lines = []
        while j < len(lines) and is_roman_line(lines[j]):
            roman_lines.append(lines[j])
            j += 1

        translation_parts = []
        while j < len(lines):
            probe = lines[j]
            if is_header(probe) or is_gurmukhi(probe):
                break
            translation_parts.append(probe)
            j += 1

        gurmukhi = " ".join(gm_lines).strip()
        roman = " ".join(roman_lines).strip()
        translation = re.sub(r"\s+", " ", " ".join(translation_parts)).strip()

        if roman and translation:
            example_seq += 1
            examples.append({
                "ang": 1,
                "pauri_num": current_pauri if current_pauri is not None else 1000 + example_seq,
                "gurmukhi": gurmukhi,
                "roman": roman,
                "rahao_line": "",
                "word_analysis": "[]",
                "ksd_translation": translation[:1400],
                "context_note": "",
                "principles_used": json.dumps([1, 2, 3, 4, 5, 6, 7, 8], ensure_ascii=False),
                "source": source,
            })
        i = max(j, i + 1)

    return examples


def extract_ast_translation_lines(text: str, source: str) -> list[dict]:
    """
    Извлекает готовый построчный перевод Джап Джи из таблицы AST.docx.
    Эти строки нужны не как few-shot, а как primary reference для Playwright:
    модель должна редактировать/нормализовать уже готовый перевод, а не
    переводить Джап Джи с нуля.
    """
    examples = []
    seq = 0
    for line in text.splitlines():
        cols = [col.strip() for col in line.split("\t")]
        if len(cols) < 3:
            continue
        gurmukhi, roman, translation = cols[0], cols[1], " ".join(cols[2:])
        if not re.search(r"[\u0A00-\u0A7F]", gurmukhi):
            continue
        if not roman or not translation:
            continue
        seq += 1
        examples.append({
            "ang": 1,
            "pauri_num": seq,
            "gurmukhi": gurmukhi,
            "roman": roman,
            "rahao_line": "",
            "word_analysis": json.dumps([{
                "roman": roman,
                "literal": "",
                "ksd_meta": "готовый русский AST-reference",
            }], ensure_ascii=False),
            "ksd_translation": re.sub(r"\s+", " ", translation).strip(),
            "context_note": "",
            "principles_used": json.dumps([1, 2, 3, 4, 5, 6, 7, 8], ensure_ascii=False),
            "source": source,
        })
    return examples


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


def insert_manual_ksd_knowledge(conn: sqlite3.Connection) -> tuple[int, int]:
    """Ручные KSD-определения пользователя, которые должны переживать rebuild БД."""
    source = "manual_ksd_user_terms"
    concepts = [
        {
            "concept": "Simran / Симран (ਸਿਮਰਨ)",
            "traditional": (
                "Санскритское simran буквально означает памятование / вспоминание. "
                "Панджабские эквиваленты: ਯਾਦ (yaad) — память, воспоминание; "
                "ਚੇਤਾ (chayta) — помнить, держать в уме."
            ),
            "ksd_meaning": (
                "Симран в Гурбани — не механическое повторение слова, а памятование, "
                "восприятие и созерцательное удерживание Творца внутри ума. В Sodar "
                "строка ਮਨ ਮਹਿ ਸਿਮਰਨੁ ਕਰਿਆ показывает бытовой смысл: флорикан, улетев "
                "далеко от птенцов, держит их в уме; это памятование поддерживает связь. "
                "Духовный эквивалент такого памятования — восприятие Создателя. "
                "Naam Simran означает удерживать в уме и воспринимать Наам — качества, "
                "присутствие и внутренний закон всепронизывающего Раама. Поскольку у "
                "Творца нет вообразимой формы, Симран сосредоточен на Наам, а не на "
                "визуальном образе."
            ),
            "gurbani_ref": (
                "SGGS 10: ਮਨ ਮਹਿ ਸਿਮਰਨੁ ਕਰਿਆ — florican remembers the young in the mind. "
                "SGGS 263: ਪ੍ਰਭ ਕਾ ਸਿਮਰਨੁ ਸਭ ਤੇ ਊਚਾ — держать Творца в уме и воспринимать Его "
                "выше всех духовных деяний. SGGS 803: ਸਿਮਰਿ ਮਨਾ ਰਾਮ ਨਾਮੁ ਚਿਤਾਰੇ — "
                "ум, собрав внимание, памятуй Наам всепронизывающего Раама."
            ),
            "source": source,
        },
        {
            "concept": "Naam / Наам (ਨਾਮ)",
            "traditional": (
                "Наам часто переводят как имя, атрибут, качество или добродетель Бога. "
                "Это не неверно, но может скрывать неосязаемое мистическое качество Наама."
            ),
            "ksd_meaning": (
                "Наам — не просто имя как слово и не только качество Бога. Это принцип "
                "самопроявления Божественного Сознания: закон, ритм и разумная энергия, "
                "через которую Непроявленное становится Проявленным. Наам относится к "
                "Единому и является Хукамом: вектором Его намерения, высшей формой "
                "Самоосознания Творца, ставшей внутренним законом существования. Когда "
                "Высшее Сознание осознаёт Себя через Наам, оно проецирует Себя в форму — "
                "Кудрат, оставаясь внутри творения как Закон."
            ),
            "gurbani_ref": (
                "Asa Ki Var, SGGS 462: ਆਪੀਨ੍ਹੈ ਆਪੁ ਸਾਜਿਓ ਆਪੀਨ੍ਹੈ ਰਚਿਓ ਨਾਉ — Он Сам "
                "сотворил Себя и Сам установил Себе Наам; ਦੁਯੀ ਕੁਦਰਤਿ ਸਾਜੀਐ — затем "
                "сотворил Кудрат и пребывает в ней. SGGS 71: ਏਕੋ ਨਾਮੁ ਹੁਕਮੁ ਹੈ ਨਾਨਕ "
                "ਸਤਿਗੁਰਿ ਦੀਆ ਬੁਝਾਇ ਜੀਉ — Наам Единого есть Хукам; Сатгуру даёт это осознание."
            ),
            "source": source,
        },
        {
            "concept": "Sikhi / Сикхи (ਸਿਖੀ)",
            "traditional": (
                "Обычно понимается как религиозная принадлежность или название сикхской традиции."
            ),
            "ksd_meaning": (
                "Сикхи в определении Гуру Нанака — это учение, обретаемое через опытное "
                "исследование Гуру / Слова Гуру: ਸਿਖੀ ਸਿਖਿਆ ਗੁਰ ਵੀਚਾਰਿ. Следующая строка "
                "уточняет плод этого процесса: Его Милость, приходящая в ответ на усердие "
                "в таком исследовании, переправляет через реку Майи."
            ),
            "gurbani_ref": (
                "SGGS 465: ਸਿਖੀ ਸਿਖਿਆ ਗੁਰ ਵੀਚਾਰਿ ॥ ਨਦਰੀ ਕਰਮਿ ਲਘਾਏ ਪਾਰਿ ॥"
            ),
            "source": source,
        },
        {
            "concept": "Guru / Гуру (ਗੁਰੂ)",
            "traditional": (
                "Часто понимается как внешний учитель, мастер или духовный авторитет."
            ),
            "ksd_meaning": (
                "Гуру в Сикхи — не просто учитель и не мастер-человек. Гуру — это "
                "наставляющее Божественное Слово, через которое Безграничный Создатель, "
                "присутствующий в творении, выразил Себя в Сири Гуру Грантх Сахиб как "
                "Учитель. Бани — это Гуру, и Гуру — это Бани. Это Слово содержит смысловое "
                "наставление, рас / вкус, внутреннее состояние, вибрацию и гармонию, через "
                "которые происходит ученичество. Гуру проявляется как Хукам и как обучающий "
                "принцип, заложенный во всём творении: процесс ведения от невежества к "
                "Божественному Свету."
            ),
            "gurbani_ref": (
                "SGGS 982, Guru Ram Das: ਬਾਣੀ ਗੁਰੂ ਗੁਰੂ ਹੈ ਬਾਣੀ ਵਿਚਿ ਬਾਣੀ ਅੰਮ੍ਰਿਤੁ ਸਾਰੇ — "
                "Бани есть Гуру, Гуру есть Бани; внутри Бани находятся все амритные "
                "источники духовной жизни."
            ),
            "source": source,
        },
        {
            "concept": "Vichar / Вичар (ਵੀਚਾਰ)",
            "traditional": (
                "Обычно переводится как размышление, обдумывание, рассуждение."
            ),
            "ksd_meaning": (
                "Вичар выходит за пределы простого размышления. Этимологически vi + char "
                "указывает на движение с различением: исследовать, осмысливать и проверять "
                "через внутреннее движение ума и опыта. Вичар — это деятельное исследование "
                "темы Бога, Наам и Его Хукама в собственной жизни."
            ),
            "gurbani_ref": (
                "Jap Ji Pauree 4: ਅੰਮ੍ਰਿਤ ਵੇਲਾ ਸਚੁ ਨਾਉ ਵਡਿਆਈ ਵੀਚਾਰੁ — наполнить время "
                "жизни амритой через исследование Слова, в котором живёт Закон Превышнего. "
                "Jap Ji Pauree 12: ਮੰਨੇ ਕਾ ਬਹਿ ਕਰਨਿ ਵੀਚਾਰੁ — ввериться Слову через "
                "усидчивое деятельное самоисследование."
            ),
            "source": source,
        },
        {
            "concept": "Sikhi-Guru-Vichar / Ученичество-Гуру-Вичар",
            "traditional": (
                "Сикхи часто понимается как религия или конфессиональная принадлежность."
            ),
            "ksd_meaning": (
                "Сикхи — это изучение и претворение в жизнь мудрости Гуру, содержащейся "
                "в Его священном Слове, Бани. Такого рода ученичество вызывает Милость "
                "Создателя. Бани здесь означает Гурбани — Сири Гуру Грантх Сахиб. "
                "Содержание СГГС говорит, что Письмо Его Воли вместе с наставлением, "
                "заключённым в него, проявлено в законах вселенной, видимой и невидимой: "
                "в законах природы, устройстве тела, совести, ума и естественности. "
                "Слова Создателя непосредственно выражают Его Волю — Хукам. Следование "
                "этой Воле вызывает Милость Того, из кого эта Воля исходит. Символ ੴ "
                "напоминает, что Волей Создателя пронизана даже человеческая природа. "
                "Сикх — панджабское слово, означающее ученика или учащегося религии, "
                "философии и образу жизни; оно отличается от санскритского shishya как "
                "обычного ученика или последователя."
            ),
            "gurbani_ref": (
                "Для опытного понимания совершать Вичар над 1-й и 2-й паури Джап Джи: "
                "Мул Мантар, Сат Наам, Хукам как основание Творения и Жизни."
            ),
            "source": source,
        },
        {
            "concept": "Sat Naam / Сат Наам (ਸਤਿ ਨਾਮੁ)",
            "traditional": (
                "Обычно переводится как «Истинное Имя»: sat как истинный, naam как имя."
            ),
            "ksd_meaning": (
                "Сат Наам означает: Единый Бог, пребывающий в Едином Существовании через "
                "Свой Наам. Сат (ਸਤਿ) имеет санскритское происхождение: бытие, "
                "существование, реальность. Сихари в ਸਤਿ грамматически указывает на "
                "«внутри существования / реальности / постоянного пребывания», даже если "
                "это не произносится. Поэтому Сат Наам не сводится к «Истинному Имени»: "
                "он указывает, что Наам — принцип самопроявления и Хукам Творца — "
                "присутствует непосредственно внутри нашего существования."
            ),
            "gurbani_ref": (
                "Мул Мантар: ਸਤਿ ਨਾਮੁ. Jap Ji opening shalok: ਆਦਿ ਸਚੁ ਜੁਗਾਦਿ ਸਚੁ — "
                "Сач в начале, Сач внутри всех периодов. Грамматическое примечание: "
                "ਸਿਹਾਰੀ часто указывает на содержимое понятия; ਮਨਿ = внутри ума."
            ),
            "source": source,
        },
        {
            "concept": "Ooangkar / Ооангкар (ਓਅੰਕਾਰ)",
            "traditional": (
                "Основное слово, которым Сикхи описывает Бога; часто передаётся как "
                "Онгкар / Оанкар без развёрнутого внутреннего чтения букв."
            ),
            "ksd_meaning": (
                "Ооангкар — не то, что можно исчерпывающе облечь в буквы. Через Patti "
                "Гуру Нанака можно созерцать три смысловые части: ਓ / ਊੜੈ указывает на "
                "отсутствие пределов; ਅੰ / Airra указывает на Причинность всего, Источник "
                "причинности и Его свободность от творения при присутствии в нём; ਕਾਰ "
                "указывает на непрерывное, однообразное, неизменное осуществление. "
                "Ооангкар можно приблизительно созерцать как Мастера без пределов, "
                "Причину всего, непрерывно осуществляющего всё во всём, но буквы "
                "исчерпываются перед вечным. Знание этих букв служит духовным "
                "транспортным средством к Невыразимому, особенно при сосредоточенном "
                "произнесении Оо-ан(г)-каар в Мул Мантар."
            ),
            "gurbani_ref": (
                "Patti, SGGS 432: ਊੜੈ ਉਪਮਾ ਤਾ ਕੀ ਕੀਜੈ ਜਾ ਕਾ ਅੰਤੁ ਨ ਪਾਇਆ — восхвалять "
                "Того, чьи пределы не найдены. ਆਇੜੈ ਆਪਿ ਕਰੇ... — Тот, кто создал и "
                "расположил вселенское бытие, делает что пожелает. ਕਰਿ ਕਰਿ ਵੇਖੈ ਹੁਕਮੁ "
                "ਚਲਾਏ... — создавая и созерцая, направляет Хукамом. Kabir Bavan Akhri: "
                "ਬਾਵਨ ਅਛਰ... ਏ ਅਖਰ ਖਿਰਿ ਜਾਹਿਗੇ — буквы исчерпываются перед вечным."
            ),
            "source": source,
        },
        {
            "concept": "Devte / Vedantic Gods / Боги в Гурбани",
            "traditional": (
                "Ведические и пуранические фигуры вроде Ишара/Шивы, Брахмы, Индры, "
                "Рама, Кришны, аватаров, дэвов и дэват часто читаются как реальные "
                "божественные существа или духовные статусы."
            ),
            "ksd_meaning": (
                "Гурбани не принимает индуистских богов, богинь, аватаров и пуранические "
                "истории как духовный идеал. Когда такие имена встречаются в Гурбани, "
                "они обычно раскрывают подлинную внутреннюю, историческую или "
                "мифологическую реальность этих фигур, либо переопределяются в сторону "
                "Единого Создателя и Его Хукама. Поэтому строка ਸੁਣਿਐ ਈਸਰੁ ਬਰਮਾ ਇੰਦੁ "
                "не означает, что слушание Шабда даёт человеку статус Шивы, Брахмы или "
                "Индры. Она означает: через подлинное слышание Гурбани раскрывается "
                "реальность этих так называемых богов; снимается мифологический ореол "
                "и становится видно, что они не являются духовной целью. В Гурбани Шива, "
                "Брахма, Индра, Рамчандра, Кришна, Дурга, аватары, дэвы, Ямрай, Дхарам "
                "Радж и Читрагупт не должны становиться положительными образцами или "
                "уровнями достижения. Они либо ограниченные мифологические/исторические "
                "фигуры, часто связанные с арийско-брахманическим угнетением и "
                "пуранической гиперболой, либо символы, которые Гурбани использует для "
                "разоблачения внешней религиозности, кастовой власти и духовной слепоты."
            ),
            "gurbani_ref": (
                "Jap Ji Pauree 9: ਸੁਣਿਐ ਈਸਰੁ ਬਰਮਾ ਇੰਦੁ — слышание раскрывает реальность "
                "Ишара, Брахмы, Индры, а не обещает их статус. SGGS 874: ਸਿਵ ਸਿਵ ਕਰਤੇ... "
                "— созерцание Шивы не даёт духовного возвышения. SGGS 1158: ਮੈਲਾ ਬ੍ਰਹਮਾ "
                "ਮੈਲਾ ਇੰਦੁ... ਮੈਲੇ ਸਿਵ ਸੰਕਰਾ ਮਹੇਸ — Брахма, Индра, Шива/Махеш описаны "
                "как загрязнённые. SGGS 1344: история Индры и Ахальи раскрывает "
                "безнравственность Индры. SGGS 422: ਜੁਗਹ ਜੁਗਹ ਕੇ ਰਾਜੇ ਕੀਏ ਗਾਵਹਿ ਕਰਿ "
                "ਅਵਤਾਰੀ — цари эпохами объявляли себя аватарами, но не постигли предела "
                "Творца. Основано на Moninder Singh, In Search of Gods, Sikh Bulletin 2019 Issue 3."
            ),
            "source": source,
        },
    ]
    words = [
        {
            "roman": "simran",
            "gurmukhi": "ਸਿਮਰਨ",
            "literal_ru": "памятование, вспоминание; держать в уме",
            "ksd_meta_ru": "созерцательное восприятие Творца через удерживание Наам внутри ума",
            "source": source,
            "confidence": 0.96,
        },
        {
            "roman": "naam",
            "gurmukhi": "ਨਾਮ",
            "literal_ru": "имя; добродетель; божественное присутствие",
            "ksd_meta_ru": "принцип самопроявления Творца; Наам Единого есть Хукам, внутренний закон существования",
            "source": source,
            "confidence": 0.96,
        },
        {
            "roman": "sikhi",
            "gurmukhi": "ਸਿਖੀ",
            "literal_ru": "учение; ученичество",
            "ksd_meta_ru": "учение, обретаемое через опытное исследование Гуру / Слова Гуру",
            "source": source,
            "confidence": 0.94,
        },
        {
            "roman": "guru",
            "gurmukhi": "ਗੁਰੂ",
            "literal_ru": "Гуру; наставляющее начало",
            "ksd_meta_ru": "Бани как наставляющее Божественное Слово; обучающий принцип Хукама, ведущий от невежества к Свету",
            "source": source,
            "confidence": 0.96,
        },
        {
            "roman": "vichar",
            "gurmukhi": "ਵੀਚਾਰ",
            "literal_ru": "размышление, исследование, осмысление",
            "ksd_meta_ru": "деятельное исследование Бога, Наам и Хукама в собственной жизни через различающий опыт",
            "source": source,
            "confidence": 0.94,
        },
        {
            "roman": "sat naam",
            "gurmukhi": "ਸਤਿ ਨਾਮੁ",
            "literal_ru": "Сат Наам; в существовании пребывающий Наам",
            "ksd_meta_ru": "Единый Бог, пребывающий в Едином Существовании через Свой Наам; Наам как Хукам внутри существования",
            "source": source,
            "confidence": 0.96,
        },
        {
            "roman": "ooangkar",
            "gurmukhi": "ਓਅੰਕਾਰ",
            "literal_ru": "Ооангкар; имя Творца",
            "ksd_meta_ru": "Мастер без пределов, Причина всего, непрерывно осуществляющий всё во всём; Невыразимый через буквы",
            "source": source,
            "confidence": 0.94,
        },
        {
            "roman": "ik ooangkar",
            "gurmukhi": "ੴ",
            "literal_ru": "Единый Ооангкар",
            "ksd_meta_ru": "Единый Создатель, присутствующий в своём творении и пронизывающий человеческую природу своим Хукамом",
            "source": source,
            "confidence": 0.95,
        },
        {
            "roman": "isar",
            "gurmukhi": "ਈਸਰੁ",
            "literal_ru": "Ишар / Шива",
            "ksd_meta_ru": "не духовный статус; пураническая фигура, реальность которой Гурбани раскрывает и демифологизирует через слышание Шабда",
            "source": source,
            "confidence": 0.95,
        },
        {
            "roman": "brahma",
            "gurmukhi": "ਬਰਮਾ",
            "literal_ru": "Брахма",
            "ksd_meta_ru": "не духовный статус; ограниченная пураническая фигура, не образец реализации Единого",
            "source": source,
            "confidence": 0.95,
        },
        {
            "roman": "ind",
            "gurmukhi": "ਇੰਦੁ",
            "literal_ru": "Индра",
            "ksd_meta_ru": "не духовный статус; в Гурбани раскрывается как нравственно загрязнённая/мифологизированная фигура, а не духовная цель",
            "source": source,
            "confidence": 0.95,
        },
        {
            "roman": "dev",
            "gurmukhi": "ਦੇਵ",
            "literal_ru": "дэв, бог",
            "ksd_meta_ru": "не божественная сущность в смысле Сикхи; пураническая/социально-историческая категория, которую Гурбани демифологизирует",
            "source": source,
            "confidence": 0.93,
        },
        {
            "roman": "avtar",
            "gurmukhi": "ਅਵਤਾਰੀ",
            "literal_ru": "аватар, воплощение",
            "ksd_meta_ru": "цари и властители объявляли себя аватарами; Гурбани не принимает это как постижение предела Творца",
            "source": source,
            "confidence": 0.93,
        },
        {
            "roman": "suniai isar brahma ind",
            "gurmukhi": "ਸੁਣਿਐ ਈਸਰੁ ਬਰਮਾ ਇੰਦੁ",
            "literal_ru": "через слышание — Ишар, Брахма, Индра",
            "ksd_meta_ru": "через подлинное слышание Шабда раскрывается реальность этих так называемых богов; это не получение их статуса",
            "source": source,
            "confidence": 0.97,
        },
    ]
    inserted_concepts = insert_concepts(conn, concepts)
    inserted_words, _ = insert_words(conn, words)
    return inserted_concepts, inserted_words


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
        block_words = extract_words_from_jbani_pauri_blocks(text, "jbani_v2_blocks")
        ins_bw, skip_bw = insert_words(conn, block_words)
        print(f"    слова из pauri-блоков: {ins_bw} добавлено, {skip_bw} пропущено")
        examples = extract_ksd_examples_from_jbani(text, "jbani_v2")
        ins_e = insert_examples(conn, examples)
        print(f"    паури-примеры: {ins_e} добавлено")
        block_examples = extract_examples_from_jbani_pauri_blocks(text, "jbani_v2_blocks")
        ins_be = insert_examples(conn, block_examples)
        print(f"    pauri-block few-shot: {ins_be} добавлено")
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
        words = extract_ast_glossary_words(text, "ast_example")
        ins, skip = insert_words(conn, words)
        print(f"    словарь терминов: {ins} добавлено")
        principles = extract_principles(text, "ast_example")
        ins_p = insert_principles(conn, principles)
        print(f"    принципы: {ins_p} добавлено")
        examples = extract_ast_examples(text, "ast_example")
        ins_e = insert_examples(conn, examples)
        print(f"    ast-примеры: {ins_e} добавлено")
        ast_lines = extract_ast_translation_lines(text, "ast_translation_line")
        ins_l = insert_examples(conn, ast_lines)
        print(f"    ast-построчные переводы: {ins_l} добавлено")
    else:
        print("    [SKIP]")

    # ── 10. Ручные KSD-термины пользователя ─────────────────────
    print("\n[10] Ручные KSD-термины пользователя …")
    ins_c, ins_w = insert_manual_ksd_knowledge(conn)
    print(f"    концепты: {ins_c} добавлено")
    print(f"    слова: {ins_w} добавлено")

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
