"""
darpan_rebuild.py

Читает локальный docx Guru Granth Darpan (проф. Сахиб Сингх) и пересобирает
его в структурированный русский docx:

  - Bani2   → гурмукхи (тёмно-красный) + транслитерация ниже (коричневый)
  - PadArath → русский перевод (фиолетовый); если нет — оригинал с пометкой [PN]
  - Arath    → русский перевод (синий); если нет — оригинал с пометкой [PN]
  - Bhav     → русский перевод (бирюзовый); если нет — оригинал [PN]
  - Note     → русский перевод (зелёный); если нет — оригинал [PN]

Переводы берутся из create_sggs_docx.py (RU_TRANSLATIONS + TRANSLIT_KEYS).
GPT не нужен. Всё локально.

Запуск:
    python3 darpan_rebuild.py
    python3 darpan_rebuild.py --start 448 --end 700
    python3 darpan_rebuild.py --reset          # начать заново
"""

import argparse
import json
import unicodedata
import sys
from pathlib import Path

from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ── Импортируем переводы из существующего скрипта ─────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from create_sggs_docx import RU_TRANSLATIONS, TRANSLIT_KEYS

SOURCE_DOCX = Path(__file__).parent / 'reference_material' / 'GuruGranth Darpan by Prof Sahib Singh (Uni).docx'
OUTPUT_DEFAULT = 'Darpan_Rebuilt.docx'
CONTENT_START = 448          # Мул-мантар
SAVE_INTERVAL = 500          # сохранять docx каждые N обработанных непустых параграфов

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
    'bani':    '',
    'padarth': 'Пад-артх: ',
    'arath':   'Арат: ',
    'bhav':    'Бхав: ',
    'note':    'Примечание: ',
}


# ── Нормализация ───────────────────────────────────────────────────────────────
def _norm(s: str) -> str:
    return unicodedata.normalize('NFC', s).replace('\u2019', "'").replace('\u2018', "'")


# ── Поиск перевода ─────────────────────────────────────────────────────────────
_norm_translations = [(unicodedata.normalize('NFC', k), v) for k, v in RU_TRANSLATIONS]

def get_translation(text: str) -> str | None:
    text_n = _norm(text)
    for key_n, val in _norm_translations:
        if key_n and key_n in text_n:
            return val
    return None


# ── Поиск транслитерации ──────────────────────────────────────────────────────
_norm_translit = {unicodedata.normalize('NFC', k): v for k, v in TRANSLIT_KEYS.items()}

def get_translit(text: str) -> str | None:
    text_n = _norm(text)
    for key_n, val in _norm_translit.items():
        if key_n and key_n in text_n:
            return val
    return None


# ── Запись абзаца в docx ──────────────────────────────────────────────────────
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
    print(f"Читаю источник: {SOURCE_DOCX.name}")
    src = Document(str(SOURCE_DOCX))
    paragraphs = src.paragraphs

    total = len(paragraphs)
    end = para_end if para_end is not None else total
    end = min(end, total)

    # ── Прогресс и resume ────────────────────────────────────────────────────
    state = load_progress(output_path)
    if reset or state['last_para'] < para_start:
        state = {'last_para': -1, 'translated': 0, 'untranslated': 0, 'bani': 0}
        doc = Document()
        section = doc.sections[0]
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)
        if reset:
            print("⟳ Сброс прогресса, начинаю заново.")
        else:
            print(f"Параграфы {para_start}–{end} из {total}")
    else:
        actual_start = state['last_para'] + 1
        print(f"↩ Возобновляю с параграфа {actual_start} (до {end}), "
              f"уже переведено: {state['translated']}, пропущено: {state['untranslated']}")
        if output_path.exists():
            doc = Document(str(output_path))
        else:
            doc = Document()
            section = doc.sections[0]
            section.top_margin = Cm(2)
            section.bottom_margin = Cm(2)
            section.left_margin = Cm(2.5)
            section.right_margin = Cm(2.5)
        para_start = actual_start

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

        # Прогресс каждые 200 параграфов
        done = i - para_start + 1
        if done % 200 == 0:
            pct = round(done / total_range * 100)
            total_done = state['translated'] + state['untranslated']
            tr_pct = round(state['translated'] / total_done * 100) if total_done else 0
            print(f"  [{pct}%] параграф {i}/{end} | переведено {state['translated']} ({tr_pct}%)")

        text = _norm(text)
        style_name = para.style.name
        cls = STYLE_TO_CLS.get(style_name, 'blackuni')

        # ── Bani ─────────────────────────────────────────────────────────────
        if cls in ('bani', 'banicenter'):
            if prev_cls in ('arath', 'bhav', 'note', 'padarth', 'blackuni'):
                add_separator(doc)

            state['bani'] += 1
            add_para(doc, text, COLORS['bani'], size_pt=12, bold=True, space_before=6)

            translit = get_translit(text)
            if translit:
                add_para(doc, translit, COLORS['translit'], size_pt=10, italic=True)

        # ── PadArath / Arath / Bhav / Note ───────────────────────────────────
        elif cls in ('padarth', 'arath', 'bhav', 'note'):
            ru = get_translation(text)
            if ru and '【' not in ru:
                state['translated'] += 1
                color = COLORS[CLS_COLOR.get(cls, 'blackuni')]
                label = LABEL.get(cls, '')
                add_para(doc, label + ru, color, size_pt=11)
            else:
                state['untranslated'] += 1

        # ── Заголовки ─────────────────────────────────────────────────────────
        elif cls in ('sidetitle', 'title1'):
            ru = get_translation(text)
            if ru:
                state['translated'] += 1
                doc.add_heading(ru, level=2)
            else:
                state['untranslated'] += 1

        # ── Обычный текст ─────────────────────────────────────────────────────
        else:
            ru = get_translation(text)
            if ru:
                state['translated'] += 1
                add_para(doc, ru, COLORS['blackuni'], size_pt=11)
            else:
                state['untranslated'] += 1

        prev_cls = cls
        state['last_para'] = i
        processed_since_save += 1

        # Периодическое сохранение
        if processed_since_save >= SAVE_INTERVAL:
            doc.save(str(output_path))
            save_progress(output_path, state)
            processed_since_save = 0
            print(f"  💾 Сохранено ({output_path.name}), параграф {i}")

    # Финальное сохранение
    doc.save(str(output_path))
    save_progress(output_path, state)

    total_blocks = state['translated'] + state['untranslated']
    pct = round(state['translated'] / total_blocks * 100) if total_blocks else 0
    print(f"\n✓ Готово: {output_path.name}")
    print(f"  Бани-блоков:    {state['bani']}")
    print(f"  Переведено:     {state['translated']}/{total_blocks} ({pct}%)")
    print(f"  [PN] блоков:    {state['untranslated']}")


# ── CLI ────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='Rebuild Darpan → structured Russian docx')
    parser.add_argument('--start', type=int, default=CONTENT_START,
                        help=f'Первый параграф (по умолчанию: {CONTENT_START})')
    parser.add_argument('--end', type=int, default=None,
                        help='Последний параграф (по умолчанию: весь документ)')
    parser.add_argument('--output', type=str, default=OUTPUT_DEFAULT,
                        help=f'Имя выходного файла (по умолчанию: {OUTPUT_DEFAULT})')
    parser.add_argument('--reset', action='store_true',
                        help='Начать заново, игнорируя сохранённый прогресс')
    args = parser.parse_args()

    output = Path(__file__).parent / args.output
    build(args.start, args.end, output, reset=args.reset)


if __name__ == '__main__':
    main()
