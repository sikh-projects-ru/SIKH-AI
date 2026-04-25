from __future__ import annotations

import re


LATIN_TOKEN_RE = re.compile(r"[A-Za-zāīūēōṭḍṇṛñśṣṃṅḥĀĪŪĒŌṬḌṆṚÑŚṢṂṄḤ]+")
GURMUKHI_TOKEN_RE = re.compile(r"[\u0A00-\u0A7F]+")

GURMUKHI_CONSONANTS = set("ਕਖਗਘਙਚਛਜਝਞਟਠਡਢਣਤਥਦਧਨਪਫਬਭਮਯਰਲਵਸਹੜ")


# Shared deterministic romanization display rules for all project scripts.
# Use this for display/output normalization, not as a semantic translator.
SCRIPT_TO_LATIN: dict[str, str] = {
    "ਕ": "k", "ਖ": "kh", "ਗ": "g", "ਘ": "gh", "ਙ": "ṅ",
    "ਚ": "ch", "ਛ": "chh", "ਜ": "j", "ਝ": "jh", "ਞ": "ñ",
    "ਟ": "ṭ", "ਠ": "ṭh", "ਡ": "ḍ", "ਢ": "ḍh", "ਣ": "ṇ",
    "ਤ": "t", "ਥ": "th", "ਦ": "d", "ਧ": "dh", "ਨ": "n",
    "ਪ": "p", "ਫ": "ph", "ਬ": "b", "ਭ": "bh", "ਮ": "m",
    "ਯ": "y", "ਰ": "r", "ਲ": "l", "ਵ": "v",
    "ਸ": "s", "ਹ": "h", "ੜ": "ṛ",
    "ਸ਼": "sh", "ਖ਼": "kh", "ਗ਼": "g", "ਜ਼": "z", "ਫ਼": "f",
    "ਅ": "a", "ਆ": "ā", "ਇ": "i", "ਈ": "ī",
    "ਉ": "u", "ਊ": "ū", "ਏ": "e", "ਐ": "e",
    "ਓ": "o", "ਔ": "au",
    "\u0A3E": "ā", "\u0A3F": "i", "\u0A40": "ī",
    "\u0A41": "u", "\u0A42": "ū", "\u0A47": "e",
    "\u0A48": "ai", "\u0A4B": "o", "\u0A4C": "au",
    "\u0A02": "ṃ", "\u0A70": "ṃ", "\u0A71": "",
    "\u0A3C": "", "\u0A4D": "",
}

RETROFLEX_BY_GURMUKHI = {
    "ਟ": ("t", "ṭ"),
    "ਠ": ("th", "ṭh"),
    "ਡ": ("d", "ḍ"),
    "ਢ": ("dh", "ḍh"),
    "ਣ": ("n", "ṇ"),
    "ੜ": ("r", "ṛ"),
}


def _single_base_consonant(gurmukhi_word: str) -> str | None:
    consonants = [ch for ch in gurmukhi_word if ch in GURMUKHI_CONSONANTS]
    if len(consonants) == 1:
        return consonants[0]
    return None


def _apply_short_single_letter_vowels(gurmukhi_word: str, roman_word: str) -> str:
    base = _single_base_consonant(gurmukhi_word)
    if not base:
        return roman_word

    expected_base = SCRIPT_TO_LATIN.get(base, "")
    if roman_word.lower() != expected_base:
        return roman_word

    if "\u0A3F" in gurmukhi_word:
        return f"{roman_word}i"
    if "\u0A41" in gurmukhi_word:
        return f"{roman_word}u"
    return roman_word


def _apply_ai_display(gurmukhi_word: str, roman_word: str) -> str:
    if "ੈ" not in gurmukhi_word and "ਐ" not in gurmukhi_word:
        return roman_word

    if not (gurmukhi_word.endswith("ੈ") or gurmukhi_word.endswith("ਐ")):
        return roman_word

    roman_word = re.sub(r"īai$", "īe", roman_word, flags=re.IGNORECASE)
    return re.sub(r"ai$", "e", roman_word, flags=re.IGNORECASE)


def _apply_retroflex_marks(gurmukhi_word: str, roman_word: str) -> str:
    if any(mark in roman_word for mark in ("ṭ", "ḍ", "ṇ", "ṛ")):
        return roman_word

    out = roman_word
    for gm, (plain, marked) in RETROFLEX_BY_GURMUKHI.items():
        if gm not in gurmukhi_word:
            continue
        out = re.sub(plain, marked, out, count=1)
    return out


def _apply_project_terms(gurmukhi_word: str, roman_word: str) -> str:
    if gurmukhi_word.startswith("ਸਤਿਗੁਰ"):
        roman_word = re.sub(r"satigur", "satgur", roman_word, flags=re.IGNORECASE)
    return roman_word


def _fix_foreign_script_in_roman(text: str) -> str:
    return "".join(SCRIPT_TO_LATIN.get(ch, ch) for ch in text)


def roman_display_from_gurmukhi(gurmukhi: str, roman: str) -> str:
    if not roman:
        return ""

    roman = _fix_foreign_script_in_roman(roman)
    gm_words = GURMUKHI_TOKEN_RE.findall(gurmukhi or "")
    roman_parts = re.findall(
        r"[A-Za-zāīūēōṭḍṇṛñśṣṃṅḥĀĪŪĒŌṬḌṆṚÑŚṢṂṄḤ]+|[^A-Za-zāīūēōṭḍṇṛñśṣṃṅḥĀĪŪĒŌṬḌṆṚÑŚṢṂṄḤ]+",
        roman,
    )
    roman_indexes = [
        i for i, part in enumerate(roman_parts)
        if LATIN_TOKEN_RE.search(part)
    ]

    for gm_word, part_idx in zip(gm_words, roman_indexes):
        word = roman_parts[part_idx]
        word = _apply_project_terms(gm_word, word)
        word = _apply_short_single_letter_vowels(gm_word, word)
        word = _apply_ai_display(gm_word, word)
        word = _apply_retroflex_marks(gm_word, word)
        roman_parts[part_idx] = word

    display = "".join(roman_parts)
    if "ਸਤਿਗੁਰ" in (gurmukhi or ""):
        display = re.sub(r"satigur", "satgur", display, flags=re.IGNORECASE)
    return display
