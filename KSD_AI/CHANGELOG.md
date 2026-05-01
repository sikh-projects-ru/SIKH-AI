# KSD_AI Changelog

Хронологический лог изменений в базе знаний, скриптах и контенте.
Ведётся совместно Claude + Codex. При каждом изменении добавлять строку в начало соответствующего раздела.

Формат: `YYYY-MM-DD | агент | файл/таблица | что сделано`

---

## ksd_knowledge.db — canvas_concepts

- 2026-05-01 | Claude | canvas_concepts id=55 (Sant) | Добавлены все 4 грамматических значения ਸੰਤੁ/ਸੰਤਿ/ਸੰਤ с примерами из Гурбани и инструкциями для перевода
- 2026-05-01 | Claude | canvas_concepts id=65 (Punn/Paap) | Новый концепт: ведическая punn-paap логика vs Гурбани; SGGS 920, SGGS 153; инструкции для перевода

## ksd_knowledge.db — words

_(изменения в словаре — вносить сюда)_

## nitnem_mobile — Android app

- 2026-05-01 | Claude | export_nitnem_content.py | Экспортёр теперь автоматически копирует JSON в nitnem_mobile/app/src/main/assets/ и выводит статистику (angs/shabads/lines)
- 2026-04-26 | Codex | MainActivity.kt, assets/* | Добавлен ночной режим, Анand Бани, настройки слоёв переживают поворот экрана
- 2026-04-25 | Codex/Claude | MainActivity.kt | Исправлена навигация: переход на работу (Со Дар и т.д.) теперь корректно устанавливает selectedAng
- 2026-04-25 | Claude | MainActivity.kt | InfoBlockCard и MarkdownCard переведены на MarkdownBody — поддержка тегов [g][r][t][ref] везде
- 2026-04-25 | Claude | assets/dictionary.md | Статья Симран: полная версия с 3 цитатами Гурбани в формате [g][r][t][ref]; Бани: убрана инструкция для ИИ
- 2026-04-25 | Claude | assets/ek_granth_maryada.md | Все Шабад→Шабд; добавлен дохра Гуру Гобинд Сингха; объяснение рачнавы; формула о полноте Бани
- 2026-04-25 | Claude | assets/nitnem_ru_ksd_v1.json | reader_note: руководство по чтению с цветами и объяснением Рахао; about_nitnem: цитата Eka Baani в [g][r][t][ref]
- 2026-04-25 | Claude | nitnem_app/patches.json + apply_patches.py | Система точечных правок перевода без GPT
- 2026-04-25 | Claude | nitnem_mobile/deploy.sh | Скрипт сборки и установки через adb install -r

## ksd_ang_json — переводы ангов

- 2026-05-01 | Claude | ksd_ang_json/*.json (все 19 файлов) | Мигрированы в мультиавторский формат: translations.{ksd_ru, sahib_singh_pa, sahib_singh_ru, ipotseluev_ru}; ksd_ru сохраняет confidence+confidence_reason; удалены word_analysis/roman_display; применены правила романизации (ai→ē, final sihari/onkar)

_(правки переводов — вносить сюда с номером анга и verse_id)_

## sggs_meta — индекс СГГС

- 2026-05-01 | Claude | sggs_meta/authors.json | 36 авторов СГГС (Махалла 1–9, бхагаты, бхатты) с id, name_ru, name_gu, ang-диапазонами
- 2026-05-01 | Claude | sggs_meta/raags.json | 46 рагов/разделов с ang-диапазонами, shabad_count, списком авторов
- 2026-05-01 | Claude | sggs_meta/shabad_index.json | 5542 шабада: shabad_id, ang, raag_id, author_id

## Скрипты

- 2026-05-01 | Claude | ksd_coverage.py | Отчёт покрытия KSD-перевода: full/partial/empty по ангам, флаг строк для ревью (--review), поиск гурмукхи в BaniDB
- 2026-05-01 | Claude | WORKFLOW.md | Обязательные правила для Claude+Codex: источник истины, цикл обновления, формат ang_json, правила CHANGELOG
- 2026-05-01 | Claude | CHANGELOG.md | Создан лог координации Claude+Codex (текущий файл)
- 2026-05-01 | Claude | migrate_ang_json.py | Миграция ksd_ang_json в мультиавторский формат; применяет правила романизации из custom_khoj_sahib_singh/fix_romanization_rules.py
- 2026-05-01 | Claude | ../custom_khoj_sahib_singh/migrate_to_multi_translator.py | Миграция 1430 ang_json Sahib Singh в мультиавторский формат; 60403/60403 строк
- 2026-05-01 | Claude | build_sggs_meta.py | Генерация sggs_meta/*.json из banidb/sggs.db
- 2026-05-01 | Claude | shackle_sacred_language_sikhs.pdf | Переименован из книга_по_грамматике_от_нахар_сингха.pdf (это Shackle SLS, уроки 1–16 уже в БД)
- 2026-05-01 | Claude | CODEX_TASK_shackle_L17_24.md | Инструкция Codex: продолжить индексацию Shackle SLS уроки 17–24
