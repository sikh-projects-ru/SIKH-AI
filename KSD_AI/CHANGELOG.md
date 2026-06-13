# KSD_AI Changelog

Хронологический лог изменений в базе знаний, скриптах и контенте.
Ведётся совместно Claude + Codex. При каждом изменении добавлять строку в начало соответствующего раздела.

Формат: `YYYY-MM-DD | агент | файл/таблица | что сделано`

---

## Выпуски — пользовательский уровень

- 2026-05-14 | Ilia | sikhizm.ru / Nitnem app | **Ананд Бани — перевод Карминдера Сингха Дхиллона.** Добавлен авторский перевод Ананд Сахиба (анги 917–922) по книге «Understand Anand» KSD. Перевод следует KSD-методологии: Гурбани как внутреннее послание, терминология на основе слова, объяснения по словам и аналитические примечания к каждой строке. Предыдущая AI-версия перевода сохранена как резервная.

## ksd_ang_json — Anand Sahib (angs 917–922)

- 2026-05-15 | Claude | ksd_ang_0917–0922.json | Внедрены переводы из книги KSD «Understand Anand»: 144/210 строк → ksd_ru из книги; 66 строк → AI-перевод сохранён; все 210 строк → ksd_ai_gurbani_framework (бэкап). Список непокрытых: ANAND_KSD_BOOK/pending_verses.md. Деплой на sikhizm.ru corpus 2026-05-15-190850
- 2026-05-15 | Claude | scripts/anand_build_ang_patches.py | Новый скрипт: собирает ksd_ru из ANAND_KSD_BOOK/model_responses, матчит OCR Гурмукхи → verse_id, бэкапит старый ksd_ru как ksd_ai_gurbani_framework

## Документация и навигация

- 2026-06-09 | Codex | NANAK_CANVAS_AUDIT.md | Зафиксирован аудит индексации Nanak Canvas: 12 глав, 99 explicit SGGS examples, покрытие полей, отсутствие дублей и manual QA queue по Gurmukhi-containing строкам без близкой явной SGGS-ссылки
- 2026-06-09 | Codex | PROJECT_INDEX.md, PROJECT_INDEX.json | Уточнён coverage для `Концепты Сикхи.docx`: добавлен chapter-level source-тег `nanak_canvas_chapters_v1` после индексации 12 глав и SGGS examples
- 2026-06-09 | Codex | PROJECT_INDEX.md | Уточнён DB coverage для `Концепты Сикхи.docx`: добавлен source-тег `nanak_canvas_concepts_sikhi` и таблицы `ksd_principles`, `ksd_examples` после продолжения индексации Nanak Canvas
- 2026-06-07 | Codex | PROJECT_INDEX.md, PROJECT_INDEX.json | Создан каталог root-level PDF/DOCX/TXT источников: роли, статусы индексации, размеры, SHA-256, source-теги БД; отмечен дубликат `Концепты Сикхи.docx` / `Холст Гуру Нанака...docx`
- 2026-06-07 | Codex | SOURCE_DOCUMENTS_PLAN.md | Зафиксирован план будущего переноса raw PDF/DOCX/TXT источников в `source_documents/` по категориям без фактического перемещения файлов
- 2026-06-07 | Codex | PROJECT_INDEX.md, PROJECT_INDEX.json | Уточнены статусы TXT-кандидатов: `52_a_khar_example.txt` отмечен как KSD source note для будущей extraction; `siddh_ghost_scratches.txt` как scratch
- 2026-06-04 | Codex | SGGS_SMART_DICTIONARY_CONCEPT.md | Зафиксирован концепт умного словаря для SGGS Reader: локальный индекс точных словоформ и вхождений, UI кликабельных слов, модель данных, оценка KhojGurbani/BaniDB, provenance и поэтапный план
- 2026-05-15 | Codex | ANAND_KSD_BOOK, .gitignore | Создана локальная staging-структура для обработки скриншотов `Understand Anand`; raw/generated артефакты исключены из git
- 2026-05-08 | Codex | AGENTS.md, CLAUDE.md, docs/obsidian/* | Добавлен первый Obsidian-каркас для ориентации Codex/Claude: входные файлы, карта проекта, источники истины, workflows, принципы перевода, решения и открытые задачи

## ksd_knowledge.db — canvas_concepts

- 2026-06-13 | Claude | canvas_concepts, ksd_examples (Nanak Canvas) | Починены 11 непривязанных строк концептов Холста через `fix_nanak_canvas_unmatched.py` (идемпотентно): опечатки анга в `gurbani_ref` #67/#68 (474→484, 696→969, 467→437) и в `ksd_examples` (ids 722/719/720/435/673 — ang typos; 692 ਜਿਸੁ→ਜਿਸ; 691 фрагмент→полная строка; 648/650 — заменён тег автора `ਮਃ ੫`/`ਮ :੧` на реальные строки из docx Part2/Part3, verse_id 41315/28043). После реэкспорта `ksd_concept_tags.json`: resolved_verse_id 96→107, unmatched 14→3 (остаток — `naam`/`devte` из manual_ksd_user_terms, вне Холста). Сахиб Сингх и данные ридера не затронуты
- 2026-06-09 | Codex | canvas_concepts, ksd_examples (nanak_canvas_chapters_v1) | Проиндексированы 12 глав Nanak Canvas / `Концепты Сикхи.docx`: добавлены 12 chapter-level концептов и 99 SGGS-ссылок/примеров по главам; итоговые счётчики: canvas_concepts 81, ksd_examples 536
- 2026-06-09 | Codex | canvas_concepts, ksd_principles, ksd_examples (nanak_canvas_concepts_sikhi) | Продолжена индексация Nanak Canvas / `Концепты Сикхи.docx`: добавлены 4 концепта, 6 методологических принципов и 4 примера по old canvas vs redefinition, mention vs endorsement, here-and-now, Teerath и Panch Doot; обновлены `ksd_knowledge_dump.sql` и `ksd_knowledge_snapshot.json`
- 2026-05-01 | Claude | canvas_concepts id=55 (Sant) | Добавлены все 4 грамматических значения ਸੰਤੁ/ਸੰਤਿ/ਸੰਤ с примерами из Гурбани и инструкциями для перевода
- 2026-05-01 | Claude | canvas_concepts id=65 (Punn/Paap) | Новый концепт: ведическая punn-paap логика vs Гурбани; SGGS 920, SGGS 153; инструкции для перевода

## ksd_knowledge.db — grammar_rules

- 2026-06-07 | Codex | grammar_rules, ksd_principles (52_a_khar_example) | Проиндексирован короткий KSD-грамматический источник по ਅਖਰ vs ਅ+ਖਰ: добавлены 2 grammar_rules и 1 ksd_principle; общий счётчик grammar_rules: 364
- 2026-06-07 | Codex | grammar_rules (jbani_v2_salok_kaytee) | Проиндексирован блок финального шлока Jap Bani по Kaytee/Kaytay/Kayteeya: добавлены 2 grammar_rules; общий счётчик grammar_rules: 366
- 2026-05-01 | Codex | grammar_rules (shackle_L17–L24) | Проиндексированы Shackle SLS §170–§240, добавлено 35 правил; общий счётчик grammar_rules: 362

## ksd_knowledge.db — words

_(изменения в словаре — вносить сюда)_

## sggs_mobile — Android app

- 2026-05-01 | Claude | export_sggs_content.py + works.json | Добавлены 14 именных произведений с точной фильтрацией по shabad_id: Барах Маха (Маджх М5 / Тукхари М1), Патти Ликхи (М1), Патти (М3), Дакхни (Гаури М1 / Онкар Рамкали М1), Баван Акхари (Гаури М5 / Кабир), Тхити (Гаури М5 / Билавал М1), Алахниа, Кучхаджи, Сучхаджи, Сидх Гости; итого 31 произведение
- 2026-05-01 | Claude | MainActivity.kt | `Work` data class: добавлено поле `shabadIdEnd: Int?`; фильтрация в `filteredShabads`/`filterSearchResults`/`angMatchesSelection` переключается на диапазон shabad_id когда он задан — это устраняет ложные пересечения ангов у Патти М1 и М3 на анге 434
- 2026-05-01 | Claude | MainActivity.kt | Поиск по ангу: `KeyboardType.Number` + `ImeAction.Go`, `angInput.trim().toIntOrNull()`, отдельная секция «Перейти к ангу» в drawer
- 2026-05-01 | Claude | MainActivity.kt | Глобальный поиск: `CircularProgressIndicator` вместо голого текста «Ищу», инлайн-спиннер в статус-строке, ошибки выделяются цветом `ReaderColors.Rahao`
- 2026-05-01 | Claude | fix_rahao_blocks.py | Одноразовый скрипт-фикс: распространение `is_rahao=true` на все строки блока рахао назад до предыдущего `॥N॥`; применён к 852 ангам (3534 строк)
- 2026-05-01 | Claude | expand_ksd_angs.py | Добавлена `expand_rahao_blocks()` с той же логикой — теперь новые анги создаются сразу корректно
- 2026-05-01 | Claude | build_sggs_meta.py | Исправлена атрибуция авторов: SQL-запрос теперь берёт `MAX(CASE WHEN writer_en != '' ...)`, пропагация на шабды без автора; 451 → 0 шабдов с `author_id: null`

## nitnem_mobile — Android app

- 2026-05-01 | Codex | sggs_app + sggs_mobile | Создан MVP Android-приложения Sri Guru Granth Sahib RU: exporter полного SGGS content pack, offline assets 1430 ангов, reader с поиском по текущему ангу, навигацией по ангам, drawer-фильтрами по рагам/авторам/произведениям
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

- 2026-05-01 | Codex | ksd_ang_json/ksd_ang_0014–1430.json + expand_ksd_angs.py | Закрыт TODO по единому формату: недостающие анги созданы в `shabads[]` формате, строки сгруппированы по `shabad_id` из BaniDB; генератор теперь сразу пишет unified multi-translator format
- 2026-05-01 | Claude | ksd_ang_json/ksd_ang_0001–0013.json | Влит sahib_singh_ru из custom_khoj_sahib_singh (577 строк по ангам 1–13); ang 917–922 пока не переведены в источнике
- 2026-05-01 | Claude | ksd_ang_json/*.json (все 19 файлов) | Мигрированы в мультиавторский формат: translations.{ksd_ru, sahib_singh_pa, sahib_singh_ru, ipotseluev_ru}; ksd_ru сохраняет confidence+confidence_reason; удалены word_analysis/roman_display; применены правила романизации (ai→ē, final sihari/onkar)

_(правки переводов — вносить сюда с номером анга и verse_id)_

## sggs_meta — индекс СГГС

- 2026-05-01 | Claude | sggs_meta/authors.json | 36 авторов СГГС (Махалла 1–9, бхагаты, бхатты) с id, name_ru, name_gu, ang-диапазонами
- 2026-05-01 | Claude | sggs_meta/raags.json | 46 рагов/разделов с ang-диапазонами, shabad_count, списком авторов
- 2026-05-01 | Claude | sggs_meta/shabad_index.json | 5542 шабада: shabad_id, ang, raag_id, author_id

## Скрипты

- 2026-06-09 | Codex | add_nanak_canvas_chapters.py, ksd_backup_db.py | Добавлен одноразовый chapter-level индексатор Nanak Canvas: читает DOCX, разбивает 12 глав, извлекает SGGS references в `ksd_examples`; обновлены SQL/JSON снапшоты БД
- 2026-06-09 | Codex | add_nanak_canvas_index.py, ksd_backup_db.py | Добавлен одноразовый скрипт индексации следующего слоя Nanak Canvas: концепты, принципы и примеры; обновлены переносимые снапшоты БД
- 2026-06-07 | Codex | add_grammar_52_a_khar.py, ksd_backup_db.py | Добавлен одноразовый скрипт вставки Akhar/A+Khar правила; обновлены `ksd_knowledge_dump.sql` и `ksd_knowledge_snapshot.json`
- 2026-06-07 | Codex | add_grammar_jbani_kaytee.py, ksd_backup_db.py | Добавлен одноразовый скрипт вставки Kaytee grammar block; обновлены `ksd_knowledge_dump.sql` и `ksd_knowledge_snapshot.json`
- 2026-05-15 | Codex | scripts/anand_chatgpt_page.py | Добавлен batch-режим `--from-page/--to-page` и `--skip-existing` для пачечной обработки страниц `Understand Anand`
- 2026-05-15 | Codex | scripts/anand_chatgpt_page.py, ANAND_KSD_BOOK/bot_profile | Runner переключён на локальную копию ChatGPT-профиля и 10-минутное ожидание ответа модели
- 2026-05-15 | Codex | scripts/anand_chatgpt_page.py, scripts/anand_ang_dry_run.py | Добавлены рабочие скрипты для обработки страниц `Understand Anand` через ChatGPT и dry-run проверки full ang JSON перед импортом
- 2026-05-01 | Codex | SGGS_RU_APP_CONCEPT.md | Обновлены решения по SGGS app: рабочее название Sri Guru Granth Sahib RU, первый релиз со всеми ангами offline, основной слой Sahib Singh, скрытие пустых слоёв, дизайн как Nitnem, будущий `works.json` для Ананд/Сукхмани и других баний
- 2026-05-01 | Codex | SGGS_RU_APP_CONCEPT.md | Добавлен концепт отдельного Android-приложения SGGS RU на базе unified `ksd_ang_json`, с фильтрами по рагам, авторам, разделам и ангам
- 2026-05-01 | Codex | add_grammar_shackle_L17_24.py, grammar_index_progress.md | Добавлен и выполнен скрипт индексации Shackle SLS L17–L24; прогресс зафиксирован отдельным блоком
- 2026-05-01 | Claude | ksd_coverage.py | Отчёт покрытия KSD-перевода: full/partial/empty по ангам, флаг строк для ревью (--review), поиск гурмукхи в BaniDB
- 2026-05-01 | Claude | WORKFLOW.md | Обязательные правила для Claude+Codex: источник истины, цикл обновления, формат ang_json, правила CHANGELOG
- 2026-05-01 | Claude | CHANGELOG.md | Создан лог координации Claude+Codex (текущий файл)
- 2026-05-01 | Claude | merge_sahib_singh_ru.py | Слияние sahib_singh_ru из custom_khoj_sahib_singh/ang_json в ksd_ang_json по verse_id
- 2026-05-01 | Claude | migrate_ang_json.py | Миграция ksd_ang_json в мультиавторский формат; применяет правила романизации из custom_khoj_sahib_singh/fix_romanization_rules.py
- 2026-05-01 | Claude | build_sggs_meta.py | Генерация sggs_meta/*.json из banidb/sggs.db
- 2026-05-01 | Claude | shackle_sacred_language_sikhs.pdf | Переименован из книга_по_грамматике_от_нахар_сингха.pdf (это Shackle SLS, уроки 1–16 уже в БД)
- 2026-05-01 | Claude | CODEX_TASK_shackle_L17_24.md | Инструкция Codex: продолжить индексацию Shackle SLS уроки 17–24
