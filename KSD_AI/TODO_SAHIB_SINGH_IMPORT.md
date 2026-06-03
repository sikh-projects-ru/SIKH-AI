# TODO: Sahib Singh RU — исправление и деплой на сайт

## Контекст

Переводы Sahib Singh RU на сайте `sikhizm.ru` содержат несколько классов ошибок.
Исходники: `custom_khoj_sahib_singh/ang_json/ang_NNNN.json` (flat-формат).
Деплой идёт через `KSD_AI/ksd_ang_json/` → `scripts/publish_sggs_import.py`.

Промежуточный шаг — backfill: merge из flat-формата в ksd_ang_json multi-translator.

---

## Известные проблемные анги

### Пенджабский вместо русского (дубликат sahib_singh_pa)
- Анги: 603, 604, 644, 866, 867
- 87 строк, где `translation_ru` = копия `sahib_singh_pa`
- Источник в: `custom_khoj_sahib_singh/ang_json/ang_0603.json` и др.

### Хинди вместо русского
- Анги: 3, 36, 57, 75, 88, 95, 98, 102, 108, 109, 131, 149, 168–171, 183, 188,
  192, 224, 233, 236, 255, 269, 270, 291, 310
- Corrupted `translation_ru` (хинди-текст вместо русского)

### Критический разрыв
- Анги 938+ — `sahib_singh_pa` есть до 937, дальше пусто
- Требует отдельного источника данных

### Уже исправлено, но не задеплоено
- Анги 917–922 — backfill сделан (`backfill_917_922.py` запускался),
  нужно проверить актуальность и задеплоить через `publish_sggs_import.py`

---

## Что нужно сделать

- [ ] **Написать `scripts/backfill_angs.py`** — рефакторинг `backfill_917_922.py`,
  принимает `--angs 603 604 644 ...` или диапазон `--range 603-644`
- [ ] **Исправить flat-файлы** для пенджабских дублей (603, 604, 644, 866, 867):
  заменить `translation_ru` на реальный русский текст
- [ ] **Исправить flat-файлы** для хинди-ангов (список выше)
- [ ] **Прогнать backfill** для всех исправленных ангов
- [ ] **Задеплоить** через `publish_sggs_import.py`
- [ ] **Playwright-скан против live-сайта** — сравнить `sikhizm.ru` с локальными
  файлами для полного аудита; скриптов против сайта пока нет, только против
  локальных файлов и banidb

---

## Команды (после исправления файлов)

```bash
# Backfill (после написания generalized-скрипта)
python3 scripts/backfill_angs.py --angs 603 604 644 866 867

# Dry-run импорта
python3 scripts/publish_sggs_import.py --dry-run \
  ksd_ang_json/ksd_ang_0603.json \
  ksd_ang_json/ksd_ang_0604.json \
  ksd_ang_json/ksd_ang_0644.json \
  ksd_ang_json/ksd_ang_0866.json \
  ksd_ang_json/ksd_ang_0867.json

# Деплой
python3 scripts/publish_sggs_import.py \
  --updates "Fix Sahib Singh RU: punjabi duplicates in 603, 604, 644, 866, 867" \
  ksd_ang_json/ksd_ang_0603.json ...
```
