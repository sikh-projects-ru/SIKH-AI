# KSD_AI — Рабочий процесс

Этот файл описывает обязательные правила работы для Claude и Codex.

---

## 1. Обновление контента Нитнем-приложения

### Источник истины

Все переводы хранятся в:
```
ksd_ang_json/ksd_ang_0001.json  ..  ksd_ang_0013.json
ksd_ang_json/ksd_ang_0917.json  ..  ksd_ang_0922.json
```

**Никогда не редактировать напрямую:**
- `nitnem_app/content/nitnem_ru_ksd_v1.json` — генерируется автоматически
- `nitnem_mobile/app/src/main/assets/nitnem_ru_ksd_v1.json` — копируется автоматически

### Цикл обновления

```
# 1. Правки — только в source-файлах:
ksd_ang_json/ksd_ang_XXXX.json
  └── translations.ksd_ru.main / artistic / context_note

# 2. Пересборка контент-пака и автокопирование в assets:
python3 nitnem_app/export_nitnem_content.py
  → Wrote nitnem_app/content/nitnem_ru_ksd_v1.json
  → Copied → nitnem_mobile/app/src/main/assets/nitnem_ru_ksd_v1.json

# 3. Сборка и деплой на телефон:
cd nitnem_mobile && ./deploy.sh
```

### Точечные правки без перегенерации

Для одиночных правок перевода — использовать систему патчей:
```
# Добавить запись в nitnem_app/patches.json:
{"verse_id": 482, "field": "main", "old": "старый текст", "new": "новый текст"}

# Применить:
python3 nitnem_app/apply_patches.py

# Затем пересобрать:
python3 nitnem_app/export_nitnem_content.py
```

### Markdown-ассеты приложения

Файлы, загружаемые приложением напрямую (не через экспортёр):
```
nitnem_mobile/app/src/main/assets/dictionary.md
nitnem_mobile/app/src/main/assets/ek_granth_maryada.md
nitnem_mobile/app/src/main/assets/updates.md
```
После правки этих файлов — запустить `./deploy.sh` (без экспортёра, т.к. изменились только .md).
Если Gradle кеширует и не подхватывает .md: `./gradlew clean assembleDebug` вместо обычной сборки.

---

## 2. Структура ang_json (мультиавторский формат)

Каждый `ksd_ang_*.json` имеет структуру:

```json
{
  "ang": 1,
  "shabads": [
    {
      "shabad_id": 1,
      "rahao_verse_id": null,
      "rahao_theme": "...",
      "shabad_summary": "...",
      "lines": [
        {
          "verse_id": 1,
          "is_rahao": false,
          "gurmukhi": "...",
          "roman": "...",
          "translations": {
            "ksd_ru":         {"main": "...", "artistic": "...", "context_note": "...", "confidence": 0.9},
            "sahib_singh_pa": {"main": "..."},
            "sahib_singh_ru": {"main": ""},
            "ipotseluev_ru":  {"main": ""}
          }
        }
      ]
    }
  ]
}
```

Правила романизации (применяются через `migrate_ang_json.py`):
- Dulavan (ੈ) → `ē`, не `ai`
- Final sihari (ਿ) → не произносится: `ਹਰਿ` → `har`
- Final onkar (ੁ) в многобуквенных словах → опускается: `ਨਾਮੁ` → `nām`

Источник правил: `../custom_khoj_sahib_singh/fix_romanization_rules.py`

---

## 3. Логирование изменений

**Каждое изменение в коде, базе знаний или контенте логировать в `CHANGELOG.md`.**

Формат:
```
YYYY-MM-DD | Агент | файл/таблица | что сделано
```

Секции CHANGELOG:
- `ksd_knowledge.db — canvas_concepts`
- `ksd_knowledge.db — words`
- `nitnem_mobile — Android app`
- `ksd_ang_json — переводы ангов`
- `sggs_meta — индекс СГГС`
- `Скрипты`

---

## 4. База знаний (ksd_knowledge.db)

Таблицы:
- `canvas_concepts` — концепты перевода (id, concept, traditional, ksd_meaning, gurbani_ref, source)
- `words` — словарь (gurmukhi, roman, literal_ru, ksd_meta_ru, grammar_note)
- `grammar_rules` — грамматические правила (category, pattern, meaning, example_word, example_meaning, source)
- `ksd_principles` — принципы перевода KSD
- `ksd_examples` — примеры применения

Source-теги грамматики:
- `grammar_pdf_p*` — Гурбани грамматика.pdf (123 стр., завершено)
- `shackle_L01_*` .. `shackle_L16_*` — Shackle SLS уроки 1–16 (завершено)
- `shackle_L17_*` и далее — TODO (см. `CODEX_TASK_shackle_L17_24.md`)

---

## 5. SGGS-метаданные

```
sggs_meta/authors.json      — 36 авторов (id, name_ru, name_gu, type, mahalla)
sggs_meta/raags.json        — 46 рагов/разделов (id, ang_start, ang_end, authors)
sggs_meta/shabad_index.json — 5542 шабада (shabad_id, ang, raag_id, author_id)
```

Источник: `banidb/sggs.db`. Перегенерация: `python3 build_sggs_meta.py`.

---

## 6. Деплой на телефон

```bash
cd nitnem_mobile && ./deploy.sh
```

- Работает как бесшовное обновление (`adb install -r`) если debug-keystore совпадает.
- Если ключ сменился (новая машина/агент): сначала `adb uninstall org.ksd.nitnem`, затем `./deploy.sh`.
- Телефон: USB-кабель + USB-отладка включена.
- `/dev/kvm` недоступен — эмулятор не используем.
