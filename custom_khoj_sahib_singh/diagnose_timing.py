#!/usr/bin/env python3
"""
diagnose_timing.py — замеряет каждый шаг: API KhojGurbani + загрузку ChatGPT.
Запуск: python diagnose_timing.py [--ang 201]
Не трогает ang_json, docx, прогресс — только читает и смотрит.
"""

import argparse
import time
import urllib.request
import json
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from playwright_stealth import Stealth

BOT_PROFILE = Path(__file__).parent / "bot_profile"
CHAT_URL = "https://chatgpt.com/"
API_BASE = "https://apiprod.khojgurbani.org/api/v1"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Origin": "https://khojgurbani.org",
    "Referer": "https://khojgurbani.org/",
    "Accept": "application/json",
}

_stealth = Stealth()


def ts(label: str, start: float) -> None:
    print(f"  [{time.time() - start:6.1f}s]  {label}")


# ─── API DIAGNOSTICS ──────────────────────────────────────────────────────────

def api_get(path: str, timeout: int = 20) -> dict:
    req = urllib.request.Request(f"{API_BASE}{path}", headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def diagnose_api(ang: int):
    print(f"\n{'='*60}")
    print(f"=== API KhojGurbani — анг {ang} ===")
    print(f"{'='*60}")
    t0 = time.time()

    # 1. Первый запрос: shabad 1
    print(f"\n[1] GET /shabad/{ang}/1 ...")
    t1 = time.time()
    try:
        data = api_get(f"/shabad/{ang}/1")
        elapsed = time.time() - t1
        status = data.get("status")
        pages = data.get("data", {}).get("pages") if isinstance(data.get("data"), dict) else None
        print(f"    ответ за {elapsed:.2f}s | status={status!r} | pages={pages}")
        if pages:
            print(f"    → Страницы сразу известны: {pages} — discover будет мгновенным")
        else:
            print(f"    → pages пустые/нет — discover пойдёт в цикл прощупывания")
    except Exception as exc:
        print(f"    ОШИБКА за {time.time()-t1:.2f}s: {exc}")

    # 2. Имитация discover: 10 последовательных запросов, замеряем скорость
    print(f"\n[2] Скорость 10 запросов подряд (shabad 1..10):")
    times = []
    for probe in range(1, 11):
        t1 = time.time()
        try:
            api_get(f"/shabad/{ang}/{probe}")
            times.append(time.time() - t1)
        except Exception:
            times.append(time.time() - t1)

    avg = sum(times) / len(times)
    print(f"    мин={min(times):.2f}s  макс={max(times):.2f}s  среднее={avg:.2f}s")
    if avg > 1.0:
        print(f"    ⚠ API медленный! При 30 misses × {avg:.1f}s = {30*avg:.0f}s только на остановку")
    else:
        print(f"    ✓ API быстрый — 30 misses займут ≈{30*avg:.0f}s")

    ts(f"\nAPI итого", t0)


# ─── BROWSER DIAGNOSTICS ─────────────────────────────────────────────────────

def diagnose_browser():
    print(f"\n{'='*60}")
    print(f"=== Браузер + ChatGPT ===")
    print(f"{'='*60}")

    if not (BOT_PROFILE / "Default").exists():
        print("bot_profile не найден — сначала запусти основной бот для логина.")
        return

    with sync_playwright() as pw:
        print("\nЗапускаю браузер...")
        context = pw.chromium.launch_persistent_context(
            user_data_dir=str(BOT_PROFILE),
            headless=False,
            args=["--start-maximized"],
            no_viewport=True,
        )

        t0 = time.time()
        print(f"\nОткрываю вкладку: {CHAT_URL}")
        page = context.new_page()
        ts("new_page()", t0)

        _stealth.apply_stealth_sync(page)
        ts("stealth", t0)

        try:
            page.goto(CHAT_URL, wait_until="domcontentloaded", timeout=120_000)
            ts("domcontentloaded", t0)
        except PWTimeout:
            ts("ТАЙМАУТ domcontentloaded (120s)", t0)
            context.close()
            return

        try:
            page.wait_for_load_state("networkidle", timeout=60_000)
            ts("networkidle", t0)
        except PWTimeout:
            ts("networkidle не дождался за 60s", t0)

        try:
            page.locator("#prompt-textarea").wait_for(state="visible", timeout=120_000)
            ts("prompt-textarea виден", t0)
        except PWTimeout:
            ts("ТАЙМАУТ: prompt-textarea (120s)", t0)

        # Печатаем тестовый текст и смотрим на send-button
        print("\n  Вставляю тестовый текст в textarea...")
        try:
            page.evaluate("""() => {
                const el = document.getElementById("prompt-textarea");
                if (!el) return;
                el.focus();
                document.execCommand("selectAll", false, null);
                document.execCommand("insertText", false, "test");
            }""")
            page.wait_for_timeout(800)
            ts("текст вставлен", t0)
        except Exception as e:
            print(f"  ошибка вставки: {e}")

        try:
            page.locator('button[data-testid="send-button"]').wait_for(state="visible", timeout=15_000)
            ts("send-button виден (после ввода текста)", t0)
        except PWTimeout:
            ts("ТАЙМАУТ: send-button не появился даже после ввода (15s)", t0)
            # Покажем что за кнопки вообще есть
            btns = page.locator("button").all()
            print(f"  Кнопок на странице: {len(btns)}")
            for b in btns[:10]:
                try:
                    tid = b.get_attribute("data-testid") or ""
                    txt = (b.inner_text() or "").strip()[:40]
                    if tid or txt:
                        print(f"    data-testid={tid!r}  text={txt!r}")
                except Exception:
                    pass

        print(f"\n  Итого: {time.time()-t0:.1f}s")
        input("\n>> Enter чтобы закрыть браузер...")
        page.close()
        context.close()


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ang", type=int, default=203, help="Анг для теста API (default: 203)")
    parser.add_argument("--no-browser", action="store_true", help="Только API, без браузера")
    parser.add_argument("--no-api", action="store_true", help="Только браузер, без API")
    args = parser.parse_args()

    if not args.no_api:
        diagnose_api(args.ang)

    if not args.no_browser:
        diagnose_browser()

    print("\nДиагностика завершена.")


if __name__ == "__main__":
    main()
