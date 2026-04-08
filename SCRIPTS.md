# Методичка по Python скриптам

Все скрипты запускаются из `/home/royal/Work/Spiritual/`.

---

## 1. KhojGurbani — перевод Джапу Джи Сахиб

**Скрипт:** `khojgurbani_translate.py`  
**Кэш:** `khojgurbani_cache.json` (ключи: `kg_N`, `ss_N`, `commentary_N`)  
**Выход:** `KhojGurbani_Russian.docx`

### Посмотреть исходник шабда

```bash
python3 khojgurbani_translate.py fetch --ang 8 --shabad 38
```

Выводит: гурмукхи, транслитерацию, перевод KG (англ.), перевод SS (панджаби), комментарий KG.  
Нумерация шабдов **глобальная** (не по ангу). Шабд 38 → `--ang 8 --shabad 38`.

### Собрать docx для одного анга

```bash
python3 khojgurbani_translate.py build --ang 7 --shabad 31 --end-shabad 37 --output /tmp/ang7.docx
```

### Собрать финальный docx (все анги)

```bash
# Сначала собрать каждый анг отдельно:
python3 khojgurbani_translate.py build --ang 1 --shabad 1  --end-shabad 4  --output /tmp/ang1.docx
python3 khojgurbani_translate.py build --ang 2 --shabad 5  --end-shabad 10 --output /tmp/ang2.docx
python3 khojgurbani_translate.py build --ang 3 --shabad 11 --end-shabad 18 --output /tmp/ang3.docx
python3 khojgurbani_translate.py build --ang 4 --shabad 19 --end-shabad 22 --output /tmp/ang4.docx
python3 khojgurbani_translate.py build --ang 5 --shabad 23 --end-shabad 27 --output /tmp/ang5.docx
python3 khojgurbani_translate.py build --ang 6 --shabad 28 --end-shabad 30 --output /tmp/ang6.docx
python3 khojgurbani_translate.py build --ang 7 --shabad 31 --end-shabad 37 --output /tmp/ang7.docx
python3 khojgurbani_translate.py build --ang 8 --shabad 38 --end-shabad 40 --output /tmp/ang8.docx

# Затем объединить:
python3 - <<'EOF'
from docx import Document
from docx.oxml import OxmlElement
import copy

files = [f"/tmp/ang{i}.docx" for i in range(1, 9)]
merged = Document(files[0])

def add_page_break(doc):
    para = doc.add_paragraph()
    run = para.add_run()
    br = OxmlElement('w:br')
    br.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}type', 'page')
    run._r.append(br)

for path in files[1:]:
    add_page_break(merged)
    src = Document(path)
    for elem in src.element.body:
        if elem.tag.endswith('}sectPr'):
            continue
        merged.element.body.append(copy.deepcopy(elem))

merged.save("KhojGurbani_Russian.docx")
print("✓ KhojGurbani_Russian.docx")
EOF
```

### Карта шабдов (Джапу Джи)

| Анг | Шабды | Паури |
|-----|-------|-------|
| 1 | 1–4 | Шалок, 1–4 |
| 2 | 5–10 | 5–9 |
| 3 | 11–18 | 10–17 |
| 4 | 19–22 | 18–21 |
| 5 | 23–27 | 22–26 |
| 6 | 28–30 | 27–29 |
| 7 | 31–37 | 30–36 |
| 8 | 38–40 | 37, 38, финальный Шалок |

---

## 2. СГГС Дарпан — пересборка docx

**Скрипт:** `darpan_rebuild.py`  
**Источник:** `reference_material/GuruGranth Darpan by Prof Sahib Singh (Uni).docx`  
**Переводы:** берутся из `create_sggs_docx.py` (словари `RU_TRANSLATIONS`, `TRANSLIT_KEYS`)  
**Выход:** любой docx по выбору

### Запуск

```bash
# Весь документ (от Мул-мантара до конца):
python3 darpan_rebuild.py

# Только Джапу Джи (паури 1–16, параграфы 448–746):
python3 darpan_rebuild.py --start 448 --end 746

# Начать заново (если в docx есть мусор или серые блоки):
python3 darpan_rebuild.py --reset
```

**Автовозобновление:** при повторном запуске скрипт продолжит с последнего места (прогресс в `Darpan_Rebuilt.progress`).  
Прогресс выводится в терминал каждые ~200 параграфов.  
Непереведённые блоки **пропускаются** — в docx не попадают.

### Карта параграфов (Джапу Джи)

| Раздел | Параграфы |
|--------|-----------|
| Введение (Джапу Джи да Бхав) | 363–448 |
| Мул-мантар + Шалок (Анг 1) | 448–496 |
| Паури 1 | 496–514 |
| Паури 2 | 514–524 |
| Паури 3 | 524–562 |
| Паури 4 (Анг 2) | 562–596 |
| Паури 5 | 596–618 |
| Паури 6 | 618–629 |
| Паури 7 | 629–640 |
| Паури 8 | 640–644 |
| Паури 9 | 644–661 |
| Паури 10 | 661–683 |
| Паури 11 | 683–691 |
| Паури 12 (Анг 3) | 691–697 |
| Паури 13 | 697–701 |
| Паури 14 | 701–716 |
| Паури 15 | 716–726 |
| Паури 16 | 726–746 |

---

## 3. СГГС Дарпан — ChatGPT бот (Playwright)

**Скрипт:** `chatgpt_darpan/bot.py`  
**Что делает:** открывает страницы gurugranthdarpan.net, вставляет текст в ChatGPT, ждёт перевода, сохраняет в docx.  
**Прогресс:** сохраняется в `.progress_<output>.txt` — при перезапуске продолжает с того же места.

### Запуск

```bash
cd chatgpt_darpan

# Указать URL чата можно аргументом:
python3 bot.py --start 31 --end 50 --output output.docx --chat-url "https://chatgpt.com/c/ВАШ-ЧАТ-ID"

# Или не указывать — скрипт спросит интерактивно:
python3 bot.py --start 31 --end 50 --output output.docx
# → Введи URL чата ChatGPT: <вставляешь ссылку>
```

### Первый запуск (новый профиль браузера)

При первом запуске откроется браузер — нужно войти в ChatGPT вручную, затем нажать Enter в терминале.  
Профиль сохраняется в `bot_profile/` — последующие запуски стартуют уже залогиненными.

### Параметры

| Параметр | По умолчанию | Описание |
|----------|-------------|----------|
| `--start` | 1 | Начальный анг |
| `--end` | 1430 | Конечный анг |
| `--output` | `darpan_chatgpt.docx` | Имя выходного файла |
| `--delay` | 3.0 | Пауза между ангами (сек) |
| `--chat-url` | *(спросит)* | URL конкретного чата ChatGPT |

---

## 4. СГГС — чистый текст (бани + транслитерация)

**Скрипт:** `create_sggs_clean.py`  
**Выход:** `SGGS_Clean_Russian.docx`

```bash
python3 create_sggs_clean.py
```

---

## 5. KSD — Nanak Canvas

**Скрипты:** `ksd_canvas_fetch.py`, `ksd_canvas_build_ru.py`

```bash
# Скачать исходник статьи
python3 ksd_canvas_fetch.py

# Собрать переведённый docx
python3 ksd_canvas_build_ru.py
```
