# custom_khoj_sahib_singh

Playwright-бот для перевода Шри Гуру Грантх Сахиб на русский язык через ChatGPT.
Источник: [KhojGurbani](https://khojgurbani.org/) — перевод Prof. Sahib Singh (поле `sahib_singh_pa`).

## Что делает

1. Скачивает данные анга с KhojGurbani API.
2. Отправляет в ChatGPT промпт с gurmukhi + панджабским переводом Sahib Singh.
3. Получает JSON: romanization + русский перевод построчно.
4. Сохраняет `ang_json/ang_XXXX.json` и собирает `khojgurbani_sahibsingh_chatgpt.docx`.

## Структура

```
custom_khoj_sahib_singh/
├── chatgpt_khojgurbani_sahibsingh_bot.py   # основной скрипт
├── ang_json/                                # JSON по ангам (ang_0001.json … ang_1430.json)
├── raw_logs/                                # сырые промпты и ответы ChatGPT
├── khojgurbani_sahibsingh_chatgpt.docx      # итоговый документ
└── bot_profile/                             # Chrome-профиль (в .gitignore)
```

### Формат ang_json

```json
{
  "ang": 1,
  "line_count": 30,
  "lines": [
    {
      "index": 1,
      "verse_id": 1,
      "shabad_num": 1,
      "shabad_id": 1,
      "gurmukhi": "ੴ ਸਤਿ ਨਾਮੁ ...",
      "site_roman": "ik ōunkār ...",
      "sahib_singh_pa": "ਅਕਾਲ ਪੁਰਖ ਇੱਕ ਹੈ ...",
      "roman": "ik ōankār sat nām ...",
      "translation_ru": "Акал Пуракх един ..."
    }
  ]
}
```

## Запуск

```bash
# Первый запуск (анги 1–1430)
python3 chatgpt_khojgurbani_sahibsingh_bot.py

# Продолжить с анга 106
python3 chatgpt_khojgurbani_sahibsingh_bot.py --start 106

# Конкретный диапазон
python3 chatgpt_khojgurbani_sahibsingh_bot.py --start 106 --end 700

# Пересобрать DOCX из готовых JSON (без ChatGPT)
python3 chatgpt_khojgurbani_sahibsingh_bot.py --start 1 --end 105 --rebuild-docx-from-json
```

## Параллельная работа (два человека)

Каждый работает над своим диапазоном ангов на отдельной ветке.
Конфликтов не будет: файлы в `ang_json/` не пересекаются.

```bash
# Человек A: анги 1–700
git checkout -b sahibsingh/1-700
python3 chatgpt_khojgurbani_sahibsingh_bot.py --start 1 --end 700

# Человек B: анги 701–1430
git checkout -b sahibsingh/701-1430
python3 chatgpt_khojgurbani_sahibsingh_bot.py --start 701 --end 1430
```

После завершения — merge веток в main, затем пересборка единого DOCX:

```bash
python3 chatgpt_khojgurbani_sahibsingh_bot.py --start 1 --end 1430 --rebuild-docx-from-json
```

## Ключевые аргументы

| Аргумент | По умолчанию | Описание |
|---|---|---|
| `--start` | 1 | Начальный анг |
| `--end` | 1430 | Конечный анг |
| `--output` | `khojgurbani_sahibsingh_chatgpt.docx` | Имя выходного DOCX |
| `--delay` | 3.0 | Пауза между ангами (сек) |
| `--max-retries` | 3 | Попыток на один анг |
| `--rebuild-docx-from-json` | — | Пересобрать DOCX из JSON, без ChatGPT |
| `--force-retranslate` | — | Перезаписать уже готовые JSON |
| `--reset-progress` | — | Сбросить файл прогресса |
| `--reset-json-range` | — | Удалить JSON текущего диапазона перед запуском |

## Прогресс

- Всего ангов в СГГС: **1430**
- Готово: **105** (ang 1–105)
- Осталось: **~1325**
