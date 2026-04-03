# TODO

## KSD — Nanak Canvas (Karmindar Singh Dhillon)

- [ ] Перевести части 3–12 (URLs в `ksd_nanak_canvas_urls.json`)
- [ ] Финальная сборка книги:
  - Объединить все 12 частей в один docx, сохранив картинки и цитаты (Гурмукхи + транслитерация)
  - Книжное оформление: титульный лист, оглавление, единые стили (заголовки, тело, блоки цитат)
  - Редактура формулировок — сгладить там, где звучит буквально, до естественного русского
- [ ] Создать `ksd_canvas_combine.py` — скрипт объединения 12 docx в один

## KSD — Большие файлы в git

- [ ] Упаковать `reference_material/` и `ksd_reference_material/` в zip-архивы и коммитить их
  ```bash
  zip -r reference_material.zip reference_material/
  zip -r ksd_reference_material.zip ksd_reference_material/ --exclude "*_RU.docx"
  ```

## KhojGurbani — перевод Джапу Джи Сахиб

- [ ] Перевести АНГ 5–24 (пауди 22–38 + шалок) — данные в `kg_raw_all.json`
- [ ] Автоматизация через Claude API (когда будет ключ)

## СГГС Дарпан (проф. Сахиб Сингх)

- [ ] Перевести пауди 17–38

## Общее

- [ ] Письмо автору KhojGurbani через SikhPhilosophyNetwork
