# Задача для Codex: индексация Shackle SLS, уроки 17–24

## Контекст

Книга: **C. Shackle, "An Introduction to the Sacred Language of the Sikhs"** (Heritage Publishers).  
Файл: `/home/royal/Work/Spiritual/KSD_AI/shackle_sacred_language_sikhs.pdf` (218 страниц PDF).  
База данных: `/home/royal/Work/Spiritual/KSD_AI/ksd_knowledge.db`, таблица `grammar_rules`.

Уроки 1–16 уже проиндексированы (source-теги `shackle_L01_*` .. `shackle_L16_*`, 327 правил всего в таблице).  
**Задача: проиндексировать уроки 17–24.**

Книга: Part II = 24 урока. Урок 17 начинается на книжной странице 108 = PDF-странице 118.  
Смещение: PDF-страница = книжная страница + 10.

---

## Схема таблицы grammar_rules

```sql
CREATE TABLE grammar_rules (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,        -- тип правила (см. ниже)
    pattern  TEXT,        -- короткий snake_case идентификатор
    meaning  TEXT,        -- полное описание правила на английском
    example_word    TEXT, -- примеры слов/форм на Гурмукхи
    example_meaning TEXT, -- английский перевод примеров
    source   TEXT         -- 'shackle_L17_p108' и т.д.
);
```

Категории (category):
- `word_form` — падежи, склонения, парадигмы местоимений/прилагательных
- `tense` — временны́е формы глагола
- `principle` — синтаксические принципы, особые конструкции
- `ending` — суффиксы и их грамматическое значение
- `case` — падежные функции
- `number` — единственное/множественное
- `gender` — мужской/женский
- `vowel_mark` — лагааны и их роль

---

## Формат вставки (Python)

```python
import sqlite3
conn = sqlite3.connect('ksd_knowledge.db')
cur = conn.cursor()

rules = [
    ('word_form', 'short_pattern_name',
     'Full English description of the rule. Include all forms, exceptions, notes from the book.',
     'ਗੁਰਮੁਖੀ ਉਦਾਹਰਣਾਂ | ਇੱਥੇ',
     'gurmukhi_form = English meaning | next_form = meaning',
     'shackle_L17_p108'),
    # ... more rules
]

for r in rules:
    cur.execute(
        'INSERT INTO grammar_rules (category, pattern, meaning, example_word, example_meaning, source) VALUES (?,?,?,?,?,?)',
        r
    )
conn.commit()
conn.close()
print(f'Inserted {len(rules)} rules')
```

---

## Соглашение по source-тегам

Формат: `shackle_L{lesson}_p{book_page}`  
Примеры:
- `shackle_L17_p108` — урок 17, книжная страница 108
- `shackle_L17_p109_p110` — правило охватывает две страницы
- `shackle_L18_p115` — урок 18, страница 115

Находить книжный номер страницы по колонтитулу (он напечатан вверху/внизу страницы).

---

## Что индексировать

**Включать:**
- Все пронумерованные параграфы (§165, §166, …) — грамматические правила
- Парадигмы склонений и спряжений с исключениями
- Принципы использования форм (синтаксис, эргатив, пассив и т.д.)
- Примечания о значениях форм и их отличиях

**НЕ включать:**
- Словарные списки (Vocabulary — Masculine nouns / Feminine nouns / Verbs / Adjectives)
- Упражнения (Exercise A, Exercise B) — только текст правил, не сами задания

---

## Соглашение по pattern (короткий идентификатор)

Примеры из уже сделанных уроков:
- `locative_case_masculine_declensions`
- `personal_pronouns_full_declension`
- `demonstrative_pronoun_locative_full_paradigm`
- `verbs_lai_pai_irregular_conjugation`
- `ergative_construction_transitive_past`

Правило: `snake_case`, описывает тему, без номера параграфа. Уникальность не требуется (pattern может совпадать у разных уроков если тема та же, их различает source).

---

## Прогресс и координация

После выполнения каждого урока:

1. Добавить строку в `/home/royal/Work/Spiritual/KSD_AI/grammar_index_progress.md` — в таблицу блоков:
   ```
   | L17 | 108–114 | ✅ DONE | §165–§170 ... | N |
   ```

2. Добавить строку в `/home/royal/Work/Spiritual/KSD_AI/CHANGELOG.md` — в секцию `## Скрипты`:
   ```
   - 2026-05-01 | Codex | grammar_rules (shackle_L17) | Уроки 17–N: §165–§M, N правил добавлено
   ```

3. Сохранить Python-скрипт как `add_grammar_shackle_L17_20.py` (или аналогично по блокам).

---

## Проверка после вставки

Claude проверит результат командой:

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('ksd_knowledge.db')
c = conn.cursor()
c.execute(\"SELECT source, COUNT(*) FROM grammar_rules WHERE source LIKE 'shackle_L1[789]%' OR source LIKE 'shackle_L2%' GROUP BY source ORDER BY source\")
for r in c.fetchall(): print(r)
print('Total:', c.execute('SELECT COUNT(*) FROM grammar_rules').fetchone()[0])
"
```

---

## Начало работы

```
PDF страница 118 = книжная страница 108 = начало урока 17.
```

Открыть PDF, перейти на страницу 118, начать с первого параграфа урока 17.
