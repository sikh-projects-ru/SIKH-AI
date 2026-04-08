"""
darpan_rebuild.py

Читает локальный docx Guru Granth Darpan (проф. Сахиб Сингх) и пересобирает
его в структурированный русский docx.

Источник переводов: gpt_darpan_python.docx
  - Бани-строки → русский перевод (тёмно-красный) + транслитерация (коричневый)
  - PadArath    → пад-артх из gpt docx (фиолетовый)
  - Arath       → перевод (синий)
  - Bhav        → перевод (бирюзовый)
  - Note        → перевод (зелёный)

Запуск:
    python3 darpan_rebuild.py
    python3 darpan_rebuild.py --start 448 --end 746
    python3 darpan_rebuild.py --reset
"""

import argparse
import json
import re
import unicodedata
import sys
from pathlib import Path

from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SOURCE_DOCX  = Path(__file__).parent / 'reference_material' / 'GuruGranth Darpan by Prof Sahib Singh (Uni).docx'
GPT_DOCX     = Path(__file__).parent / 'gpt_darpan_python.docx'
OUTPUT_DEFAULT = 'Darpan_Rebuilt.docx'
CONTENT_START  = 448
SAVE_INTERVAL  = 500

# ── Маппинг стилей ─────────────────────────────────────────────────────────────
STYLE_TO_CLS = {
    'Bani2':         'bani',
    'Bani-Centered': 'bani',
    'Arath':         'arath',
    'PadArath':      'padarth',
    'Note':          'note',
    'Bhav':          'bhav',
    'Body Text1':    'blackuni',
    'text':          'blackuni',
    'text bold':     'baniblack',
    'side title':    'sidetitle',
    'title1':        'title1',
}

# ── Цвета ──────────────────────────────────────────────────────────────────────
COLORS = {
    'bani':      RGBColor(0x80, 0x00, 0x00),
    'translit':  RGBColor(0x8B, 0x45, 0x13),
    'padarth':   RGBColor(0x80, 0x00, 0x80),
    'arath':     RGBColor(0x00, 0x00, 0x80),
    'bhav':      RGBColor(0x00, 0x80, 0x80),
    'note':      RGBColor(0x00, 0x80, 0x00),
    'sidetitle': RGBColor(0x00, 0x00, 0x00),
    'title1':    RGBColor(0x00, 0x00, 0x00),
    'blackuni':  RGBColor(0x00, 0x00, 0x00),
}

CLS_COLOR = {
    'padarth':  'padarth',
    'arath':    'arath',
    'bhav':     'bhav',
    'note':     'note',
    'blackuni': 'blackuni',
    'baniblack':'blackuni',
    'sidetitle':'sidetitle',
    'title1':   'title1',
}

LABEL = {
    'padarth': 'Пад-артх: ',
    'arath':   'Арат: ',
    'bhav':    'Бхав: ',
    'note':    'Примечание: ',
}


# ── Утилиты ───────────────────────────────────────────────────────────────────
def _norm(s: str) -> str:
    return unicodedata.normalize('NFC', s).replace('\u2019', "'").replace('\u2018', "'")

def _has_gurmukhi(text: str) -> bool:
    return any('\u0A00' <= c <= '\u0A7F' for c in text)

def _has_cyrillic(text: str) -> bool:
    return any('\u0400' <= c <= '\u04FF' for c in text)

def _guru_only(text: str) -> str:
    """Оставляем только символы гурмукхи и пробелы."""
    return ''.join(c for c in text if '\u0A00' <= c <= '\u0A7F' or c == ' ').strip()


# ── Парсинг gpt_darpan_python.docx ───────────────────────────────────────────
def load_gpt_translations(docx_path: Path):
    """
    Возвращает:
      bani_pairs   — list[(gurmukhi_key, russian_text)], сортировка: длиннее вперёд
      translit_map — dict[gurmukhi_key → roman_text]
      padarth_pairs— list[(gurmukhi_word, russian_explanation)], длиннее вперёд
    """
    doc = Document(str(docx_path))
    paras = doc.paragraphs
    n = len(paras)

    bani_pairs    = []
    translit_map  = {}
    padarth_pairs = []

    in_padarth = False
    i = 0

    while i < n:
        raw = paras[i].text
        text = raw.strip()
        style = paras[i].style.name

        if not text:
            i += 1
            continue

        # ── Вход в секцию пад-артха ───────────────────────────────────────────
        if 'ਪਦ ਅਰਥ' in text or ('Разбор слов' in text and style == 'Heading 3'):
            in_padarth = True
            i += 1
            continue

        # Заголовок (не пад-артховый) — выходим из режима пад-артха
        if style.startswith('Heading') and 'ਪਦ ਅਰਥ' not in text and 'Разбор' not in text:
            in_padarth = False

        # ── Пад-артх запись ───────────────────────────────────────────────────
        if in_padarth and _has_gurmukhi(text):
            for dash in ('—', ' — ', ' - '):
                if dash in text:
                    left, _, right = text.partition(dash)
                    right = right.strip()
                    if _has_cyrillic(right):
                        guru_key = _norm(_guru_only(left))
                        if guru_key:
                            padarth_pairs.append((guru_key, right))
                    break

        # ── Шабад-параграф с переводом (многострочный, ANG 2+) ───────────────
        if _has_gurmukhi(text) and '\n' in raw:
            lines = [l.strip() for l in raw.split('\n') if l.strip()]
            guru_lines, tr_lines, ru_lines = [], [], []
            state = 'guru'
            for line in lines:
                if line.startswith('Перевод на русский:'):
                    state = 'ru'
                    rest = line[len('Перевод на русский:'):].strip()
                    if rest:
                        ru_lines.append(rest)
                elif line.startswith('Transliteration:'):
                    state = 'tr'
                    rest = line[len('Transliteration:'):].strip()
                    if rest:
                        tr_lines.append(rest)
                elif state == 'guru':
                    if _has_gurmukhi(line):
                        guru_lines.append(line)
                    elif _has_cyrillic(line):
                        state = 'ru'; ru_lines.append(line)
                    else:
                        state = 'tr'; tr_lines.append(line)
                elif state == 'tr':
                    if _has_cyrillic(line):
                        state = 'ru'; ru_lines.append(line)
                    else:
                        tr_lines.append(line)
                else:
                    ru_lines.append(line)

            if guru_lines and ru_lines:
                key = _norm(' '.join(guru_lines))
                val = ' '.join(ru_lines)
                bani_pairs.append((key, val))
                if tr_lines:
                    translit_map[key] = ' '.join(tr_lines)

        # ── Шабад-параграф (однострочный гурмукхи, ANG 1 стиль) ──────────────
        elif (_has_gurmukhi(text) and '\n' not in raw
              and not in_padarth and '—' not in text):
            j = i + 1
            while j < n and not paras[j].text.strip():
                j += 1
            if j >= n:
                i += 1
                continue

            next_text = paras[j].text.strip()
            tr_text = None
            ru_text = None

            if next_text.startswith('Transliteration:'):
                tr_raw = paras[j].text
                tr_text = tr_raw.replace('Transliteration:', '', 1).strip().replace('\n', ' ')
                j += 1
                while j < n and not paras[j].text.strip():
                    j += 1
                if j < n:
                    next_text = paras[j].text.strip()

            if j < n and (next_text.startswith('Перевод на русский:') or
                          (_has_cyrillic(next_text) and not _has_gurmukhi(next_text))):
                ru_raw = paras[j].text
                if next_text.startswith('Перевод на русский:'):
                    ru_text = ru_raw.replace('Перевод на русский:', '', 1).strip().replace('\n', ' ')
                else:
                    ru_text = ru_raw.strip().replace('\n', ' ')

            if ru_text:
                key = _norm(text)
                bani_pairs.append((key, ru_text))
                if tr_text:
                    translit_map[key] = tr_text

        i += 1

    # Сортировка: длинные ключи — точнее совпадение
    bani_pairs.sort(key=lambda x: -len(x[0]))
    padarth_pairs.sort(key=lambda x: -len(x[0]))

    return bani_pairs, translit_map, padarth_pairs


# ── Функции поиска ─────────────────────────────────────────────────────────────
def get_translation(text: str, pairs: list) -> str | None:
    text_n = _norm(text)
    for key_n, val in pairs:
        if key_n and key_n in text_n:
            return val
    return None

def get_translit(text: str, translit_map: dict) -> str | None:
    text_n = _norm(text)
    for key_n, val in translit_map.items():
        if key_n and key_n in text_n:
            return val
    return None

def get_all_padarth(text: str, padarth_pairs: list) -> list[str]:
    """Все пад-артх объяснения, чей ключ есть в тексте."""
    text_n = _norm(text)
    results = []
    seen = set()
    for key_n, val in padarth_pairs:
        if key_n and key_n not in seen and key_n in text_n:
            results.append(val)
            seen.add(key_n)
    return results


# ── Запись параграфа ──────────────────────────────────────────────────────────
def add_para(doc: Document, text: str, color: RGBColor, size_pt: float = 11,
             bold: bool = False, italic: bool = False,
             space_before: int = 0, space_after: int = 0) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    run = p.add_run(text)
    run.font.color.rgb = color
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic


def add_separator(doc: Document) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '4')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), 'CCCCCC')
    pBdr.append(bottom)
    pPr.append(pBdr)


# ── Прогресс ──────────────────────────────────────────────────────────────────
def _progress_file(output_path: Path) -> Path:
    return output_path.with_suffix('.progress')

def load_progress(output_path: Path) -> dict:
    pf = _progress_file(output_path)
    if pf.exists():
        try:
            return json.loads(pf.read_text())
        except Exception:
            pass
    return {'last_para': -1, 'translated': 0, 'untranslated': 0, 'bani': 0}

def save_progress(output_path: Path, state: dict) -> None:
    _progress_file(output_path).write_text(json.dumps(state))


# ── Основная сборка ───────────────────────────────────────────────────────────
def build(para_start: int, para_end: int | None, output_path: Path, reset: bool = False) -> None:
    # Загружаем переводы из gpt_darpan_python.docx
    print(f"Загружаю переводы из: {GPT_DOCX.name}")
    bani_pairs, translit_map, padarth_pairs = load_gpt_translations(GPT_DOCX)
    print(f"  Бани-переводов: {len(bani_pairs)}, транслитераций: {len(translit_map)}, пад-артх: {len(padarth_pairs)}")

    print(f"Читаю источник: {SOURCE_DOCX.name}")
    src = Document(str(SOURCE_DOCX))
    paragraphs = src.paragraphs

    total = len(paragraphs)
    end = para_end if para_end is not None else total
    end = min(end, total)

    # ── Прогресс / resume ────────────────────────────────────────────────────
    state = load_progress(output_path)
    if reset or state['last_para'] < para_start:
        state = {'last_para': -1, 'translated': 0, 'untranslated': 0, 'bani': 0}
        doc = Document()
        section = doc.sections[0]
        section.top_margin = Cm(2); section.bottom_margin = Cm(2)
        section.left_margin = Cm(2.5); section.right_margin = Cm(2.5)
        if reset:
            print("⟳ Сброс прогресса, начинаю заново.")
        else:
            print(f"Параграфы {para_start}–{end} из {total}")
    else:
        para_start = state['last_para'] + 1
        print(f"↩ Возобновляю с параграфа {para_start} (до {end}), "
              f"уже переведено: {state['translated']}, пропущено: {state['untranslated']}")
        doc = Document(str(output_path)) if output_path.exists() else Document()
        if not output_path.exists():
            section = doc.sections[0]
            section.top_margin = Cm(2); section.bottom_margin = Cm(2)
            section.left_margin = Cm(2.5); section.right_margin = Cm(2.5)

    if para_start >= end:
        print("✓ Документ уже собран полностью.")
        return

    total_range = end - para_start
    processed_since_save = 0
    prev_cls = None

    for i, para in enumerate(paragraphs[para_start:end], start=para_start):
        text = para.text.strip()
        if not text:
            continue

        done = i - para_start + 1
        if done % 200 == 0:
            pct = round(done / total_range * 100)
            total_done = state['translated'] + state['untranslated']
            tr_pct = round(state['translated'] / total_done * 100) if total_done else 0
            print(f"  [{pct}%] параграф {i}/{end} | переведено {state['translated']} ({tr_pct}%)")

        text = _norm(text)
        cls = STYLE_TO_CLS.get(para.style.name, 'blackuni')

        # ── Bani ─────────────────────────────────────────────────────────────
        if cls in ('bani', 'banicenter'):
            if prev_cls in ('arath', 'bhav', 'note', 'padarth', 'blackuni'):
                add_separator(doc)

            state['bani'] += 1
            add_para(doc, text, COLORS['bani'], size_pt=12, bold=True, space_before=6)

            tr = get_translit(text, translit_map)
            if tr:
                add_para(doc, tr, COLORS['translit'], size_pt=10, italic=True)

        # ── PadArath ─────────────────────────────────────────────────────────
        elif cls == 'padarth':
            entries = get_all_padarth(text, padarth_pairs)
            if entries:
                state['translated'] += len(entries)
                for entry in entries:
                    add_para(doc, 'Пад-артх: ' + entry, COLORS['padarth'], size_pt=11)
            else:
                state['untranslated'] += 1

        # ── Arath / Bhav / Note ───────────────────────────────────────────────
        elif cls in ('arath', 'bhav', 'note'):
            ru = get_translation(text, bani_pairs)
            if ru:
                state['translated'] += 1
                color = COLORS[CLS_COLOR.get(cls, 'blackuni')]
                label = LABEL.get(cls, '')
                add_para(doc, label + ru, color, size_pt=11)
            else:
                state['untranslated'] += 1

        # ── Заголовки ─────────────────────────────────────────────────────────
        elif cls in ('sidetitle', 'title1'):
            ru = get_translation(text, bani_pairs)
            if ru:
                state['translated'] += 1
                doc.add_heading(ru, level=2)
            else:
                state['untranslated'] += 1

        # ── Обычный текст ─────────────────────────────────────────────────────
        else:
            ru = get_translation(text, bani_pairs)
            if ru:
                state['translated'] += 1
                add_para(doc, ru, COLORS['blackuni'], size_pt=11)
            else:
                state['untranslated'] += 1

        prev_cls = cls
        state['last_para'] = i
        processed_since_save += 1

        if processed_since_save >= SAVE_INTERVAL:
            doc.save(str(output_path))
            save_progress(output_path, state)
            processed_since_save = 0
            print(f"  💾 Сохранено ({output_path.name}), параграф {i}")

    doc.save(str(output_path))
    save_progress(output_path, state)

    total_blocks = state['translated'] + state['untranslated']
    pct = round(state['translated'] / total_blocks * 100) if total_blocks else 0
    print(f"\n✓ Готово: {output_path.name}")
    print(f"  Бани-блоков:    {state['bani']}")
    print(f"  Переведено:     {state['translated']}/{total_blocks} ({pct}%)")
    print(f"  Пропущено:      {state['untranslated']}")


# ── CLI ────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='Rebuild Darpan → structured Russian docx')
    parser.add_argument('--start', type=int, default=CONTENT_START)
    parser.add_argument('--end',   type=int, default=None)
    parser.add_argument('--output', type=str, default=OUTPUT_DEFAULT)
    parser.add_argument('--reset', action='store_true',
                        help='Начать заново, игнорируя сохранённый прогресс')
    args = parser.parse_args()

    output = Path(__file__).parent / args.output
    build(args.start, args.end, output, reset=args.reset)


if __name__ == '__main__':
    main()
