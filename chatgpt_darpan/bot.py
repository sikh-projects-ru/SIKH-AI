"""
chatgpt_darpan/bot.py

Берёт страницы gurugranthdarpan.net по порядку,
вставляет текст в ChatGPT, ждёт ответа, сохраняет в docx.

Запуск:
    python3 bot.py --start 23 --end 50 --output output.docx

Первый запуск: войди в ChatGPT в открывшемся браузере, затем нажми Enter.
Последующие запуски: браузер стартует уже залогиненным.
"""

import argparse
import time
import re
import os
from pathlib import Path
from datetime import datetime

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from playwright_stealth import Stealth

_stealth = Stealth()
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# ─── Настройки ────────────────────────────────────────────────────────────────

DARPAN_URL = "https://www.gurugranthdarpan.net/{page:04d}.html"
CHATGPT_URL = "https://chatgpt.com/c/69d2aae5-2a38-832c-86c5-0d561788cf1d"

# Что отправлять в ChatGPT — измени промпт под свои нужды
PROMPT_TEMPLATE = """\
Переведи следующий текст из комментария к Гуру Грантх Сахиб (Guru Granth Sahib Darpan, проф. Сахиб Сингх) на русский язык. \
Сохрани структуру: сначала текст шабда, затем толкование. Перевод должен быть точным и литературным.

{content}
"""

# Отдельный профиль для бота (не конфликтует с открытым Chrome/Chromium)
BOT_PROFILE = Path(__file__).parent / "bot_profile"

# ─── Извлечение текста с Дарпана ──────────────────────────────────────────────

def extract_darpan_page(page, ang: int) -> str | None:
    url = DARPAN_URL.format(page=ang)
    print(f"  → Загружаю {url}")
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30_000)
    except PWTimeout:
        print(f"  ✗ Таймаут при загрузке {url}")
        return None

    # Собираем все блоки Bani и Arath по порядку
    blocks = page.query_selector_all("p.Bani, p.Arath")
    if not blocks:
        print(f"  ✗ Нет блоков на странице {ang}")
        return None

    lines = []
    for block in blocks:
        text = block.inner_text().strip()
        if text:
            lines.append(text)

    return "\n\n".join(lines)


# ─── Отправка в ChatGPT и ожидание ответа ────────────────────────────────────

def send_to_chatgpt(page, content: str) -> str | None:
    prompt = PROMPT_TEMPLATE.format(content=content)

    # Переходим на ChatGPT (если ещё не там)
    if "chatgpt.com" not in page.url and "chat.openai.com" not in page.url:
        page.goto(CHATGPT_URL, wait_until="domcontentloaded", timeout=30_000)
        page.wait_for_timeout(2000)

    # Поле ввода
    textarea = page.locator("#prompt-textarea")
    try:
        textarea.wait_for(state="visible", timeout=15_000)
    except PWTimeout:
        print("  ✗ Поле ввода ChatGPT не найдено")
        return None

    # Очищаем и вставляем текст
    textarea.click()
    page.keyboard.press("Control+a")
    page.keyboard.press("Delete")
    page.wait_for_timeout(300)

    # Вставляем через clipboard (быстрее и надёжнее, чем type)
    page.evaluate(
        """(text) => {
            const el = document.getElementById('prompt-textarea');
            el.focus();
            document.execCommand('insertText', false, text);
        }""",
        prompt,
    )
    page.wait_for_timeout(500)

    # Кнопка отправки
    send_btn = page.locator('button[data-testid="send-button"]')
    try:
        send_btn.wait_for(state="visible", timeout=5_000)
        send_btn.click()
    except PWTimeout:
        # Fallback: Enter
        textarea.press("Enter")

    print("  → Жду ответа ChatGPT...")

    # Ждём появления кнопки Stop (значит генерация началась)
    try:
        page.locator('button[data-testid="stop-button"]').wait_for(
            state="visible", timeout=20_000
        )
    except PWTimeout:
        pass  # Иногда генерация слишком быстрая

    # Ждём пока Stop исчезнет (генерация завершена)
    try:
        page.locator('button[data-testid="stop-button"]').wait_for(
            state="hidden", timeout=900_000  # 15 минут
        )
    except PWTimeout:
        print("  ⚠ Таймаут ожидания ответа (15 мин) — беру то что есть")

    page.wait_for_timeout(1000)

    # Берём последний ответ ассистента
    messages = page.locator('[data-message-author-role="assistant"]')
    count = messages.count()
    if count == 0:
        print("  ✗ Ответ ассистента не найден")
        return None

    last = messages.nth(count - 1)
    return last.inner_text().strip()


# ─── Сохранение в docx ───────────────────────────────────────────────────────

def append_to_docx(docx_path: Path, ang: int, original: str, translation: str):
    if docx_path.exists():
        doc = Document(str(docx_path))
    else:
        doc = Document()
        doc.core_properties.author = "ChatGPT Darpan Bot"

    # Заголовок страницы
    heading = doc.add_heading(f"Анг {ang}", level=2)
    heading.alignment = WD_ALIGN_PARAGRAPH.LEFT

    # Оригинальный текст (курсив, серый)
    p = doc.add_paragraph()
    run = p.add_run("[ Оригинал ]\n" + original)
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
    run.font.italic = True

    doc.add_paragraph()  # отступ

    # Перевод
    p2 = doc.add_paragraph()
    run2 = p2.add_run(translation)
    run2.font.size = Pt(11)

    doc.add_paragraph()  # отступ между ангами

    doc.save(str(docx_path))
    print(f"  ✓ Сохранено в {docx_path.name}")


# ─── Прогресс (чтобы не начинать заново) ─────────────────────────────────────

def load_progress(progress_file: Path) -> int:
    if progress_file.exists():
        return int(progress_file.read_text().strip())
    return 0


def save_progress(progress_file: Path, ang: int):
    progress_file.write_text(str(ang))


# ─── Главная функция ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Darpan → ChatGPT → docx")
    parser.add_argument("--start", type=int, default=1, help="Начальный анг (по умолчанию: 1)")
    parser.add_argument("--end", type=int, default=1430, help="Конечный анг (по умолчанию: 1430)")
    parser.add_argument("--output", type=str, default="darpan_chatgpt.docx", help="Имя выходного файла")
    parser.add_argument("--delay", type=float, default=3.0, help="Пауза между ангами в секундах")
    args = parser.parse_args()

    output_path = Path(__file__).parent / args.output
    progress_file = Path(__file__).parent / f".progress_{args.output}.txt"

    BOT_PROFILE.mkdir(exist_ok=True)
    first_run = not (BOT_PROFILE / "Default").exists()

    with sync_playwright() as pw:
        print("Запускаю браузер...")
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(BOT_PROFILE),
            headless=False,
            args=["--start-maximized"],
            no_viewport=True,
        )

        # Вкладка для Дарпана
        darpan_page = ctx.new_page()
        _stealth.apply_stealth_sync(darpan_page)

        # Вкладка для ChatGPT (stealth — чтобы не определяли автоматизацию)
        chatgpt_page = ctx.new_page()
        _stealth.apply_stealth_sync(chatgpt_page)
        chatgpt_page.goto(CHATGPT_URL, wait_until="domcontentloaded", timeout=30_000)

        if first_run:
            print("\n⚠ Первый запуск: войди в ChatGPT в открывшемся браузере.")
            print("После входа нажми Enter здесь...")
            input()
        else:
            chatgpt_page.wait_for_timeout(2000)
            print("ChatGPT открыт.\n")

        # Определяем стартовый анг (учитываем прогресс)
        saved = load_progress(progress_file)
        start = max(args.start, saved + 1) if saved >= args.start else args.start
        if saved:
            print(f"Продолжаю с анга {start} (предыдущий прогресс: {saved})")

        for ang in range(start, args.end + 1):
            print(f"\n══ Анг {ang}/{args.end} ══")

            # 1. Берём текст с Дарпана
            original = extract_darpan_page(darpan_page, ang)
            if not original:
                print(f"  ⚠ Пропускаю анг {ang}")
                continue

            # 2. Отправляем в ChatGPT
            chatgpt_page.bring_to_front()
            translation = send_to_chatgpt(chatgpt_page, original)
            if not translation:
                print(f"  ⚠ Нет ответа для анга {ang}, пропускаю")
                continue

            # 3. Сохраняем в docx
            append_to_docx(output_path, ang, original, translation)
            save_progress(progress_file, ang)

            # Пауза перед следующим ангом
            if ang < args.end:
                print(f"  ⏳ Пауза {args.delay}с...")
                time.sleep(args.delay)

        print(f"\n✓ Готово! Результат: {output_path}")
        ctx.close()


if __name__ == "__main__":
    main()
