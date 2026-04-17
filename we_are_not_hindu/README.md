# Мы — не индуисты (Ham Hindu Nahin)

Кан Сингх Набха (Kahn Singh Nabha) — «Sikhs: We Are Not Hindus»

Перевод с английского на русский через ChatGPT: страница за страницей по изображениям PDF.

## Зачем

Книга показывает пример корректного диалога Сикха и Хинду при попытках «притянуть за уши» строки СГГС к индуистским интерпретациям (Веды, Пураны, Шастры и т.д.). Полезна также при диалоге с кундалини-йогами.

Автор — Кан Сингх Набха, составитель **Махан Кош** (Mahān Kosh), первой энциклопедии сикхской религии, истории и культуры на панджаби.

## Структура

```
we_are_not_hindu/
├── we_are_not_hindu_bot.py                           # основной скрипт
├── Sikhs_We_Are_Not_Hindus_By_Kahan_Singh_Nabha.pdf  # исходник
├── pages/                                            # PNG-изображения страниц
├── page_json/                                        # JSON по страницам (page_0001.json …)
├── raw_logs/                                         # сырые ответы ChatGPT
└── we_are_not_hindu_ru.docx                          # итоговый документ
```

### Формат page_json

```json
{
  "page": 1,
  "raw_text": "...оригинальный английский текст со страницы...",
  "translation_ru": "...русский перевод..."
}
```

## Зависимости

```bash
pip3 install pymupdf python-docx playwright playwright-stealth
playwright install chromium
```

## Запуск

```bash
# Первый запуск: страницы 1–15
python3 we_are_not_hindu_bot.py --start 1 --end 15

# Следующая порция
python3 we_are_not_hindu_bot.py --start 16 --end 30

# Только конвертировать PDF в картинки (без ChatGPT)
python3 we_are_not_hindu_bot.py --render-only

# Пересобрать DOCX из готовых JSON (без ChatGPT)
python3 we_are_not_hindu_bot.py --rebuild-docx
```

Бот использует `bot_profile` из проекта `custom_khoj_sahib_singh` — ChatGPT уже авторизован.  
При первом запуске проверь, что браузер открылся и ChatGPT готов, затем нажми ENTER в терминале.

## Параметры

| Аргумент | По умолчанию | Описание |
|---|---|---|
| `--start` | 1 | Начальная страница |
| `--end` | последняя | Конечная страница |
| `--dpi` | 200 | Качество рендера PDF (200 достаточно) |
| `--delay` | 4.0 | Пауза между страницами (сек) |
| `--max-retries` | 3 | Попыток на одну страницу |
| `--output` | `we_are_not_hindu_ru.docx` | Имя выходного DOCX |
| `--rebuild-docx` | — | Собрать DOCX из JSON, без ChatGPT |
| `--render-only` | — | Только конвертировать PDF в картинки |
| `--force` | — | Перевести заново уже готовые страницы |

## Прогресс

- Всего страниц: **151**
- Переведено: 0
