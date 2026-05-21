#!/usr/bin/env python3
"""
Generate artistic Russian translations for Anand Sahib pauris via ChatGPT browser UI.

Reads existing_json_to_fill_artistic.json, groups verses by pauri,
sends each pauri to ChatGPT with word-by-word meanings and style guidelines,
saves responses to ANAND_KSD_BOOK/artistic_responses/.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

try:
    from playwright.sync_api import TimeoutError as PWTimeout, sync_playwright
    from playwright_stealth import Stealth
except ImportError as exc:
    raise SystemExit("Missing dependency: install playwright and playwright-stealth") from exc


ROOT = Path(__file__).resolve().parents[1]
BOOK_DIR = ROOT / "ANAND_KSD_BOOK"
SOURCE_JSON = BOOK_DIR / "existing_json_to_fill_artistic.json"
RESPONSE_DIR = BOOK_DIR / "artistic_responses"
LOCAL_BOT_PROFILE = BOOK_DIR / "bot_profile"
FALLBACK_BOT_PROFILE = ROOT.parent / "custom_khoj_sahib_singh" / "bot_profile"
BOT_PROFILE = LOCAL_BOT_PROFILE if LOCAL_BOT_PROFILE.exists() else FALLBACK_BOT_PROFILE
CHAT_URL = "https://chatgpt.com/"

GURMUKHI_DIGITS = str.maketrans("੦੧੨੩੪੫੬੭੮੯", "0123456789")

SECTION_CONTEXT = {
    range(1, 7): "Паури 1–6: описание духовной любви, радости и Блаженства, составляющих духовность Ананда.",
    range(7, 16): "Паури 7–15: первичность Гуру Шабда как источника духовного Блаженства и радости.",
    range(16, 26): "Паури 16–25: уточнение того, что Гуру — это Бани как Гуру Шабд.",
    range(26, 40): "Паури 26–39: отвлечения и препятствия на пути к духовному Блаженству, и способы их преодоления.",
    range(40, 41): "Паури 40: итоговое описание духовного Блаженства.",
}

SYSTEM_PREAMBLE = """\
Ты — поэтический переводчик Гурбани. Ты переводишь «Ананд Сахиб» — духовный гимн Гуру Амардаса (третий Гуру), написанный в рааге Рамкали.

«Ананд Сахиб» — цельное произведение из 40 паури. Каждая строка — как стих. Финальная строка каждой паури начинается «Kahey Nanak» и подводит итог. Ты должен чувствовать произведение как единый поток.

СТИЛЬ: высокая суфийская поэзия, близкая к Джаваду Нурбахшу. Язык живой, образный, певучий. Тяга к точности образа, а не к буквальности слова. Но при этом — строгая верность духовному смыслу, который тебе дан. Никакой отсебятины.

СТРОГИЕ ПРАВИЛА:
— Никогда не заменяй имена Божественного на «Господь», «Бог», «Всевышний» и т.п.
— Сохраняй все духовные имена и термины как есть: Хар, Ооангкар, Сатгуру, Шабд, Гуру Шабд, Нам, Майа, Ананд, Сахадж, Нирмал, Банвари, Хари — оставляй в русской транскрипции.
— Используй «Творец» или «Создатель» вместо «Бог»/«Господь», если нужна русская замена.
— Каждая строка паури — отдельная строфа перевода. Не сливай строки.
— Строго следуй смыслу, данному в «Буквальный/духовный перевод» и «Значения слов».
— Не добавляй богословских объяснений и комментариев в текст перевода.
— «Редакторская заметка (фон)» — это справочный контекст для тебя. Она не является строкой паури и не переводится.
— Язык — русский, высокий, поэтический, без архаизмов типа «вящий» или церковнославянизмов.

СТРУКТУРА «АНАНД САХИБ»:
Паури 1–6: описание духовной любви, радости и Блаженства — духовность Ананда.
Паури 7–15: первичность Гуру Шабда как источника духовного Блаженства.
Паури 16–25: Гуру — это Бани как Гуру Шабд.
Паури 26–39: отвлечения и препятствия на пути к духовному Блаженству, способы их преодоления.
Паури 40: итоговое описание духовного Блаженства.
"""


class _HTMLStripper(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self._parts.append(data)

    def get_text(self) -> str:
        return "".join(self._parts).strip()


def strip_html(text: str) -> str:
    s = _HTMLStripper()
    s.feed(text or "")
    return s.get_text()


def gurmukhi_to_pauri_num(gurmukhi: str) -> int | None:
    normalized = gurmukhi.translate(GURMUKHI_DIGITS)
    m = re.search(r"॥(\d+)॥", normalized)
    if m:
        return int(m.group(1))
    return None


def section_for_pauri(n: int) -> str:
    for rng, desc in SECTION_CONTEXT.items():
        if n in rng:
            return desc
    return ""


def load_all_lines() -> list[dict[str, Any]]:
    data = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    lines: list[dict[str, Any]] = []
    for ang in data["angs"]:
        for shabad in ang["shabads"]:
            for line in shabad["lines"]:
                lines.append(line)
    return lines


def group_by_pauri(lines: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    """Return {pauri_number: [line, ...]}. Pauri 0 = header lines before pauri 1."""
    pauris: dict[int, list[dict[str, Any]]] = {}
    current: list[dict[str, Any]] = []
    current_num = 0

    for line in lines:
        current.append(line)
        num = gurmukhi_to_pauri_num(line["gurmukhi"])
        if num is not None:
            pauris[num] = current
            current = []
            current_num = num

    if current:
        pauris[current_num + 1] = current

    return pauris


def format_verse_block(line: dict[str, Any]) -> str:
    parts = []
    parts.append(f"  Гурмукхи: {line['gurmukhi']}")
    parts.append(f"  Транслитерация: {line['transliteration']}")
    src = strip_html(line.get("source_translation", "")).strip()
    if src:
        parts.append(f"  Буквальный/духовный перевод: {src}")
    rationale = strip_html(line.get("translation_rationale", "")).strip()
    if rationale:
        parts.append(f"  Значения слов: {rationale}")
    note = strip_html(line.get("context_note", "")).strip()
    if note:
        # Truncate long editorial notes; they are background context, not translation source
        short_note = note[:400] + ("…" if len(note) > 400 else "")
        parts.append(f"  Редакторская заметка (фон): {short_note}")
    return "\n".join(parts)


def build_prompt(pauri_num: int, lines: list[dict[str, Any]]) -> str:
    section = section_for_pauri(pauri_num)

    verse_blocks = []
    for i, line in enumerate(lines, start=1):
        block = f"--- Строка {i} (verse_id: {line['verse_id']}) ---\n{format_verse_block(line)}"
        verse_blocks.append(block)

    verses_text = "\n\n".join(verse_blocks)

    prompt = f"""{SYSTEM_PREAMBLE}

=== ТЕКУЩАЯ ПАУРИ: {pauri_num} ===
Раздел: {section}

Строки паури:

{verses_text}

=== ЗАДАЧА ===
Создай художественный поэтический перевод каждой строки этой паури.
Стиль: суфийская поэзия, образный живой язык, певучий ритм.
Помни о месте этой паури в цельном произведении (раздел указан выше).

Верни ТОЛЬКО валидный JSON, без markdown и без пояснений:
[
  {{"verse_id": <int>, "artistic": "<перевод строки>"}},
  ...
]
Включи все {len(lines)} строк паури, в том же порядке."""

    return prompt


def insert_text(page: Any, text: str) -> None:
    page.evaluate(
        """(text) => {
            const el = document.getElementById('prompt-textarea');
            if (!el) return;
            el.focus();
            document.execCommand('selectAll', false, null);
            document.execCommand('insertText', false, text);
        }""",
        text,
    )


def assistant_count(page: Any) -> int:
    return page.locator('[data-message-author-role="assistant"]').count()


def click_send(page: Any) -> None:
    try:
        page.locator('button[data-testid="send-button"]').click(timeout=10000)
    except PWTimeout:
        page.locator("#prompt-textarea").press("Enter")


def wait_for_response(page: Any, before_count: int, timeout_ms: int) -> str:
    stop = page.locator('button[data-testid="stop-button"]')
    try:
        stop.wait_for(state="visible", timeout=20000)
    except PWTimeout:
        pass
    try:
        stop.wait_for(state="hidden", timeout=timeout_ms)
    except PWTimeout:
        print("WARN: timed out waiting for generation; saving current response")
    page.wait_for_timeout(1200)

    try:
        page.wait_for_function(
            "(n) => document.querySelectorAll('[data-message-author-role=\"assistant\"]').length > n",
            arg=before_count,
            timeout=30000,
        )
    except PWTimeout:
        pass

    messages = page.locator('[data-message-author-role="assistant"]')
    count = messages.count()
    if count <= before_count:
        return ""
    return messages.nth(count - 1).inner_text().strip()


def strip_json_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def process_pauri(context: Any, pauri_num: int, lines: list[dict[str, Any]], timeout_ms: int) -> None:
    RESPONSE_DIR.mkdir(parents=True, exist_ok=True)
    prompt = build_prompt(pauri_num, lines)

    prompt_path = RESPONSE_DIR / f"p{pauri_num:02d}.prompt.txt"
    prompt_path.write_text(prompt, encoding="utf-8")
    print(f"Prompt saved: {prompt_path}")

    page = context.new_page()
    try:
        Stealth().apply_stealth_sync(page)
        page.goto(CHAT_URL, wait_until="domcontentloaded", timeout=30000)
        page.locator("#prompt-textarea").wait_for(state="visible", timeout=60000)

        insert_text(page, prompt)
        before = assistant_count(page)
        click_send(page)
        print(f"Waiting for ChatGPT response for pauri {pauri_num}...")
        raw = wait_for_response(page, before, timeout_ms)

        raw_path = RESPONSE_DIR / f"p{pauri_num:02d}.raw.txt"
        raw_path.write_text(raw, encoding="utf-8")
        print(f"Raw response: {raw_path}")

        cleaned = strip_json_fence(raw)
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"WARN: response for pauri {pauri_num} is not valid JSON: {e}")
            return

        json_path = RESPONSE_DIR / f"p{pauri_num:02d}.json"
        json_path.write_text(json.dumps(parsed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"JSON saved: {json_path} ({len(parsed)} items)")
    finally:
        page.close()


def run(
    pauri_nums: list[int],
    all_pauris: dict[int, list[dict[str, Any]]],
    dry_run: bool,
    timeout_ms: int,
    skip_existing: bool,
) -> None:
    queued = []
    for n in pauri_nums:
        if n not in all_pauris:
            print(f"WARN: pauri {n} not found in source JSON, skipping")
            continue
        if skip_existing and (RESPONSE_DIR / f"p{n:02d}.json").exists():
            print(f"Skip existing: pauri {n}")
            continue
        queued.append(n)

    if dry_run:
        for n in queued:
            lines = all_pauris[n]
            prompt = build_prompt(n, lines)
            prompt_path = RESPONSE_DIR / f"p{n:02d}.prompt.txt"
            RESPONSE_DIR.mkdir(parents=True, exist_ok=True)
            prompt_path.write_text(prompt, encoding="utf-8")
            print(f"[dry-run] Pauri {n}: {len(lines)} lines, prompt -> {prompt_path}")
        return

    if not queued:
        print("Nothing to process.")
        return

    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            str(BOT_PROFILE),
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        try:
            for idx, n in enumerate(queued, start=1):
                print(f"[{idx}/{len(queued)}] Pauri {n}")
                process_pauri(context, n, all_pauris[n], timeout_ms)
                time.sleep(2)
        finally:
            context.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate artistic translations for Anand Sahib pauris via ChatGPT")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pauri", type=int, help="Single pauri number (1-40)")
    group.add_argument("--from-pauri", type=int, help="First pauri for batch mode")
    group.add_argument("--all", action="store_true", help="Process all pauris")
    parser.add_argument("--to-pauri", type=int, help="Last pauri for batch mode (used with --from-pauri)")
    parser.add_argument("--skip-existing", action="store_true", help="Skip pauris that already have .json in artistic_responses/")
    parser.add_argument("--dry-run", action="store_true", help="Build and save prompts only, do not open browser")
    parser.add_argument("--timeout-ms", type=int, default=300_000)
    args = parser.parse_args()

    lines = load_all_lines()
    all_pauris = group_by_pauri(lines)
    available = sorted(all_pauris.keys())
    print(f"Found pauris: {available}")

    if args.pauri:
        pauri_nums = [args.pauri]
    elif args.all:
        pauri_nums = available
    else:
        if args.to_pauri is None:
            raise SystemExit("--from-pauri requires --to-pauri")
        pauri_nums = list(range(args.from_pauri, args.to_pauri + 1))

    run(pauri_nums, all_pauris, args.dry_run, args.timeout_ms, args.skip_existing)


if __name__ == "__main__":
    main()
