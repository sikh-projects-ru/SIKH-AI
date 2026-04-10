#!/usr/bin/env python3
"""
Patch COMBINED.docx in place:

1. Gurmukhi verse paragraphs:
   - space_after → Pt(1)  (eliminates the default ~8pt gap before transliteration)

2. Transliteration paragraph immediately following a Gurmukhi verse:
   - detected by: starts with ASCII letter, not Gurmukhi, follows a Gurmukhi paragraph
   - space_before → Pt(0)
   - space_after  → Pt(4)
   - left_indent  → 1.2 cm
   - font: Arial 10pt italic gray (#404040)

Only the COMBINED.docx is touched — no rebuild from parts.
"""

import re
from pathlib import Path
from docx import Document
from docx.shared import Pt, Cm, RGBColor

INPUT = Path(__file__).parent / 'Nanak_Canvas_COMBINED.docx'

TRANSLIT_COLOR = RGBColor(0x40, 0x40, 0x40)
FONT_NAME      = 'Arial'


def is_gurmukhi_text(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    if not ('\u0A00' <= stripped[0] <= '\u0A7F'):
        return False
    non_ws = [ch for ch in text if ch.strip()]
    if not non_ws:
        return False
    g = sum(1 for ch in non_ws if '\u0A00' <= ch <= '\u0A7F')
    return (g / len(non_ws)) >= 0.40


def para_text(para) -> str:
    return ''.join(r.text or '' for r in para.runs)


def main():
    doc   = Document(str(INPUT))
    paras = doc.paragraphs

    gur_fixed = 0
    trl_fixed = 0

    for i, para in enumerate(paras):
        text = para_text(para)
        if not text.strip():
            continue

        if is_gurmukhi_text(text):
            # Remove the default paragraph gap that pushes transliteration away
            para.paragraph_format.space_after = Pt(1)
            gur_fixed += 1

            # Look at the very next non-empty paragraph
            j = i + 1
            while j < len(paras) and not para_text(paras[j]).strip():
                j += 1
            if j >= len(paras):
                continue

            nxt      = paras[j]
            nxt_text = para_text(nxt)

            # Transliteration: starts with ASCII letter, not Gurmukhi
            if re.match(r'^[A-Za-z]', nxt_text) and not is_gurmukhi_text(nxt_text):
                nxt.paragraph_format.space_before = Pt(0)
                nxt.paragraph_format.space_after  = Pt(4)
                nxt.paragraph_format.left_indent  = Cm(1.2)
                for run in nxt.runs:
                    run.font.name      = FONT_NAME
                    run.font.italic    = True
                    run.font.bold      = False
                    run.font.size      = Pt(10)
                    run.font.color.rgb = TRANSLIT_COLOR
                trl_fixed += 1

    doc.save(str(INPUT))
    print(f'Saved: {INPUT}')
    print(f'  Gurmukhi paragraphs patched:       {gur_fixed}')
    print(f'  Transliteration paragraphs patched: {trl_fixed}')


if __name__ == '__main__':
    main()
