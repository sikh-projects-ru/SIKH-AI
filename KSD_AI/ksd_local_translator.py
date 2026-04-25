#!/usr/bin/env python3
"""
ksd_local_translator.py

Локальный KSD-переводчик через Ollama (qwen2.5:3b или любую другую модель).
Не требует браузера — работает через HTTP API Ollama (localhost:11434).

Использование:
  python3 ksd_local_translator.py --ang 1
  python3 ksd_local_translator.py --ang 1 --shabad 0   # конкретный шабд
  python3 ksd_local_translator.py --ang 1-3
  python3 ksd_local_translator.py --model llama3        # другая модель
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import unicodedata
from itertools import groupby
from pathlib import Path

import requests

SCRIPT_DIR   = Path(__file__).parent
BASE_DIR     = SCRIPT_DIR.parent
ANG_JSON_DIR = BASE_DIR / "custom_khoj_sahib_singh" / "ang_json"
DB_PATH      = SCRIPT_DIR / "ksd_knowledge.db"
OUT_DIR      = SCRIPT_DIR / "output" / "local"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
OLLAMA_CHAT_URL     = "http://localhost:11434/api/chat"
OLLAMA_TAGS_URL     = "http://localhost:11434/api/tags"
DEFAULT_MODEL = "qwen2.5:3b"

# ─── токенизация ──────────────────────────────────────────────────────────────

_ROMAN_RE    = re.compile(r"[A-Za-zāīūṭḍṇṛñśṃṅĀĪŪṬḌṆṚÑŚṂṄ]+")
_GURMUKHI_RE = re.compile(r"[਀-੿]+")
_COMMON      = {
    "har", "gur", "jan", "jin", "tin", "kau", "mo", "mai", "main", "hau",
    "tu", "toon", "mera", "mere", "meri", "ham", "te", "so", "jo", "sab",
    "sabh", "nahi", "sat", "rahau", "mahala", "rag", "kar",
}

def _norm(token: str) -> str:
    t = unicodedata.normalize("NFKD", token.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z]", "", t)

def roman_tokens(text: str) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for tok in _ROMAN_RE.findall(text or ""):
        n = _norm(tok)
        if len(n) >= 2 and n not in seen:
            seen.add(n)
            out.append(n)
    return out

def gurmukhi_tokens(text: str) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for tok in _GURMUKHI_RE.findall(text or ""):
        t = tok.strip("।॥")
        if len(t) >= 2 and t not in seen:
            seen.add(t)
            out.append(t)
    return out


# ─── загрузка данных ──────────────────────────────────────────────────────────

def load_ang(ang_num: int) -> dict | None:
    path = ANG_JSON_DIR / f"ang_{ang_num:04d}.json"
    if not path.exists():
        print(f"  [WARN] ang_json not found: {path}", file=sys.stderr)
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def group_by_shabad(ang_data: dict) -> list[list[dict]]:
    shabads = []
    for _, grp in groupby(ang_data["lines"], key=lambda l: l["shabad_id"]):
        shabads.append(list(grp))
    return shabads

def best_roman(line: dict) -> str:
    r = line.get("roman", "")
    if r and not re.search(r"[؀-ۿऀ-ॿ਀-੿]", r):
        return r
    return line.get("site_roman", "")


# ─── DB lookups ───────────────────────────────────────────────────────────────

def db_word_hints(conn: sqlite3.Connection, roman_terms: list[str], gurmukhi_terms: list[str]) -> list[str]:
    cur = conn.cursor()
    cur.execute("SELECT roman, gurmukhi, literal_ru, ksd_meta_ru FROM words")
    rows = cur.fetchall()
    rt = set(roman_terms)
    gt = set(gurmukhi_terms)
    hits: list[str] = []
    for roman, gm, literal, meta in rows:
        if not literal and not meta:
            continue
        rtoks = set(roman_tokens(roman or ""))
        match = bool((rtoks - _COMMON) & rt) or bool(gm and gm in gt)
        if not match:
            continue
        label = gm or roman
        meaning = meta or literal
        hits.append(f"  {label}: {meaning[:80]}")
    return hits[:12]

def db_grammar_hints(conn: sqlite3.Connection, roman_terms: list[str], gurmukhi_terms: list[str]) -> list[str]:
    """Finds grammar rules relevant to tokens found in the shabad."""
    cur = conn.cursor()
    cur.execute("SELECT pattern, meaning, example_word, source FROM grammar_rules")
    rows = cur.fetchall()
    rt = set(roman_terms)
    gt = set(gurmukhi_terms)
    hits: list[str] = []
    for pattern, meaning, ex_word, source in rows:
        ex_toks = set(roman_tokens(ex_word or ""))
        ex_gm   = set(gurmukhi_tokens(ex_word or ""))
        if (ex_toks - _COMMON) & rt or ex_gm & gt:
            hits.append(f"  [{source}] {pattern}: {meaning[:100]}")
    return hits[:8]

CONCEPT_ALIASES: dict[str, tuple[str, ...]] = {
    "наам": ("naam", "nam", "ਨਾਮ", "ਨਾਮੁ"),
    "хукам": ("hukam", "ਹੁਕਮ"),
    "симран": ("simran", "ਸਿਮਰਨ"),
    "Guru / Гуру (ਗੁਰੂ)": ("guru", "gur", "ਗੁਰੂ", "ਗੁਰ"),
    "Ooangkar / Ооангкар (ਓਅੰਕਾਰ)": ("ooangkar", "oangkar", "ੴ", "ਓਅੰਕਾਰ"),
    "Sant (ਸੰਤ/ਸੰਤੁ) — Sant, святой, сант": ("sant", "ਸੰਤ", "ਸੰਤੁ"),
    "Naam / Наам (ਨਾਮ)": ("naam", "nam", "ਨਾਮ", "ਨਾਮੁ"),
    "Simran / Симран (ਸਿਮਰਨ)": ("simran", "ਸਿਮਰਨ"),
    "Devte / Vedantic Gods / Боги в Гурбани": (
        "isar", "brahma", "ind", "dev", "devta", "avtar",
        "ਈਸਰੁ", "ਬਰਮਾ", "ਦੇਵ",
    ),
    "мукти": ("mukti", "mukat", "ਮੁਕਤਿ", "ਮੁਕਤ"),
    "джам": ("jam", "ਜਮ"),
}

def db_concept_hints(conn: sqlite3.Connection, roman_terms: list[str], gurmukhi_terms: list[str]) -> list[str]:
    cur = conn.cursor()
    cur.execute("SELECT concept, ksd_meaning FROM canvas_concepts ORDER BY concept")
    concepts = cur.fetchall()
    rt = set(roman_terms)
    gt = set(gurmukhi_terms)
    hits: list[str] = []
    seen: set[str] = set()
    for concept, meaning in concepts:
        if concept in seen:
            continue
        aliases = {concept.lower()}
        for alias in CONCEPT_ALIASES.get(concept, ()):
            aliases.add(alias.lower())
        matched = any(
            (_norm(a) in rt) or (a in gt)
            for a in aliases if a
        )
        if matched:
            seen.add(concept)
            hits.append(f"  {concept}: {(meaning or '')[:140].replace(chr(10),' ')}")
    return hits[:5]

def db_principles(conn: sqlite3.Connection) -> str:
    cur = conn.cursor()
    cur.execute("SELECT num, title, description FROM ksd_principles ORDER BY num")
    return "\n".join(f"  П{p[0]} ({p[1]}): {p[2][:180]}" for p in cur.fetchall())


# ─── промпт ───────────────────────────────────────────────────────────────────

SYSTEM = """\
Ты — переводчик Гурбани в стиле Карминдера Сингха Диллона (KSD).
Язык оригинала: SLS (Sacred Language of the Sikhs). Язык перевода: русский.

Принципы KSD:
- Гурбани о духовной реализации внутри сознания, не о внешней космологии.
- Творец (Ооангкар) — внутри, а не снаружи.
- Гурбани обращается ко МНЕ (читателю), здесь и сейчас.
- Рахао (ਰਹਾਉ) — тема шабда, начинай анализ с неё.
- Sahib Singh — только как подсказка по лексике, не источник смысловой рамки.

Русские эквиваленты: naam→наам, hukam→хукам, maya→майя, sahaj→сахадж, simran→симран.

Ответь ТОЛЬКО валидным JSON следующей структуры (без markdown, без пояснений):
{
  "ang": <число>,
  "shabad_id": <число>,
  "rahao_theme": "<тема шабда одной фразой>",
  "lines": [
    {"verse_id": <число>, "is_rahao": <true|false>, "ksd_translation": "<перевод строки>", "confidence": <0.0-1.0>}
  ],
  "shabad_summary": "<резюме 1-2 предложения>"
}"""

def build_prompt(shabad_lines: list[dict], *, db_conn: sqlite3.Connection, ang: int) -> str:
    roman_terms: list[str] = []
    gurmukhi_terms: list[str] = []
    for line in shabad_lines:
        roman_terms.extend(roman_tokens(best_roman(line)))
        gurmukhi_terms.extend(gurmukhi_tokens(line.get("gurmukhi", "")))

    word_hints    = db_word_hints(db_conn, roman_terms, gurmukhi_terms)
    concept_hints = db_concept_hints(db_conn, roman_terms, gurmukhi_terms)

    shabad_id = shabad_lines[0]["shabad_id"]

    lines_block = "\n".join(
        f"verse_id={l['verse_id']} "
        f"{'[RAHAO] ' if 'ਰਹਾਉ' in l.get('gurmukhi', '') else ''}"
        f"| {best_roman(l)} "
        f"| Sahib Singh (Punjabi): {l.get('sahib_singh_pa', '')[:100]}"
        for l in shabad_lines
    )

    # JSON skeleton with ang/shabad_id pre-filled so the model only fills translation fields
    json_skeleton_lines = ",\n    ".join(
        f'{{"verse_id": {l["verse_id"]}, "is_rahao": false, "ksd_translation": "...", "confidence": 0.8}}'
        for l in shabad_lines
    )
    json_skeleton = (
        f'{{\n  "ang": {ang},\n  "shabad_id": {shabad_id},\n'
        f'  "rahao_theme": "...",\n  "lines": [\n    {json_skeleton_lines}\n  ],\n'
        f'  "shabad_summary": "..."\n}}'
    )

    parts: list[str] = [
        f"Translate this Gurbani shabad (ang {ang}, shabad_id {shabad_id}) to Russian in KSD style.",
        f"\nLines:\n{lines_block}",
    ]
    if concept_hints:
        parts.append("\nKey concepts:\n" + "\n".join(concept_hints))
    if word_hints:
        parts.append("\nWord glossary:\n" + "\n".join(word_hints))

    parts.append(
        f"\nFill in the JSON below. Set is_rahao=true for RAHAO lines. "
        f"Replace '...' with actual Russian translations. Return only valid JSON.\n\n{json_skeleton}"
    )

    return "\n".join(parts)


# ─── вызов Ollama ─────────────────────────────────────────────────────────────

def call_ollama(prompt: str, model: str, *, timeout: int = 180) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user",   "content": prompt},
        ],
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
            "num_predict": 1200,
        },
    }
    try:
        resp = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=timeout)
        resp.raise_for_status()
        return resp.json().get("message", {}).get("content", "")
    except requests.exceptions.ConnectionError:
        print("  [ERROR] Ollama не запущен. Запусти: ollama serve", file=sys.stderr)
        sys.exit(1)

def parse_json(text: str) -> dict | None:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # fallback: найти первый {...} блок
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError as e:
            print(f"  [WARN] JSON parse error: {e}", file=sys.stderr)
            print(f"  Raw: {text[:400]}", file=sys.stderr)
    return None


# ─── вывод в консоль ──────────────────────────────────────────────────────────

def print_result(data: dict, shabad_lines: list[dict]) -> None:
    print(f"\n{'='*60}")
    print(f"АНГ {data.get('ang')} | Шабд {data.get('shabad_id')}")
    print(f"Рахао-тема: {data.get('rahao_theme','?')}")
    print()

    by_vid = {l["verse_id"]: l for l in shabad_lines}
    for line_data in data.get("lines", []):
        vid = line_data.get("verse_id")
        src = by_vid.get(vid, {})
        rahao = line_data.get("is_rahao", False)
        prefix = "  [РАХАО] " if rahao else "  "
        print(f"{prefix}{src.get('gurmukhi','')}")
        print(f"  {src.get('site_roman','') or best_roman(src)}")
        print(f"  → {line_data.get('ksd_translation','')}")
        conf = line_data.get("confidence", 0)
        print(f"  [{conf:.2f}]")
        print()

    print(f"Резюме: {data.get('shabad_summary','')}")
    print('='*60)


# ─── main ─────────────────────────────────────────────────────────────────────

def translate_ang(ang_num: int, shabad_idx: int | None, model: str, db_conn: sqlite3.Connection) -> None:
    ang_data = load_ang(ang_num)
    if not ang_data:
        return

    shabads = group_by_shabad(ang_data)
    if not shabads:
        print(f"  [WARN] No shabads in ang {ang_num}", file=sys.stderr)
        return

    targets = [shabads[shabad_idx]] if shabad_idx is not None else shabads

    for i, shabad_lines in enumerate(targets):
        shabad_id = shabad_lines[0]["shabad_id"]
        print(f"\nПереводим анг {ang_num}, шабд {shabad_id} ({len(shabad_lines)} строк)...")

        prompt = build_prompt(shabad_lines, db_conn=db_conn, ang=ang_num)
        raw = call_ollama(prompt, model)
        data = parse_json(raw)

        if data is None:
            print(f"  [ERROR] Не удалось распарсить JSON для шабда {shabad_id}")
            print(f"  Сырой ответ:\n{raw[:600]}")
            continue

        # сохраняем
        out_path = OUT_DIR / f"ang_{ang_num:04d}_shabad_{shabad_id}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  Сохранено: {out_path}")

        print_result(data, shabad_lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="KSD Local Translator (Ollama)")
    parser.add_argument("--ang", required=True, help="Анг или диапазон: 1 или 1-5")
    parser.add_argument("--shabad", type=int, default=None, help="Индекс шабда внутри анга (0-based)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Модель Ollama (default: {DEFAULT_MODEL})")
    args = parser.parse_args()

    # проверяем доступность модели
    try:
        r = requests.get(OLLAMA_TAGS_URL, timeout=5)
        models = [m["name"] for m in r.json().get("models", [])]
        if args.model not in models and not any(args.model in m for m in models):
            print(f"  [WARN] Модель '{args.model}' не найдена в Ollama.")
            print(f"  Доступные: {models}")
            print(f"  Запусти: ollama pull {args.model}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("  [ERROR] Ollama не запущен. Запусти: ollama serve")
        sys.exit(1)

    db_conn = sqlite3.connect(DB_PATH)

    ang_arg = args.ang
    if "-" in ang_arg:
        a, b = ang_arg.split("-", 1)
        ang_range = range(int(a), int(b) + 1)
    else:
        ang_range = range(int(ang_arg), int(ang_arg) + 1)

    for ang_num in ang_range:
        translate_ang(ang_num, args.shabad, args.model, db_conn)

    db_conn.close()


if __name__ == "__main__":
    main()
