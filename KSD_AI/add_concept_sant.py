import sqlite3
conn = sqlite3.connect('ksd_knowledge.db')
cur = conn.cursor()

# Sant has three distinct grammatical-semantic levels in Gurbani, plus a historical note
# This is theology/terminology, not grammar — belongs in canvas_concepts

concept = 'Sant (ਸੰਤ/ਸੰਤੁ) — Sant, святой, сант'

traditional = (
    'В сикхском обществе с 1903 года — почётный титул духовного лидера (Баба/Сант). '
    'В стандартных переводах "ਸੰਤ ਧੂਰਿ" (Sant Dhuur) переводится как "пыль со стоп святых" — '
    'подразумевая конкретных людей-сантов, которым нужно поклоняться или следовать. '
    'Исторически: с 1469 по 1708 (весь период Гуру) ни один сикх не носил и не получал '
    'титул "сант". Титул появился в среде сикхов лишь в 1903 году.'
)

ksd_meaning = (
    '1. ਸੰਤੁ (aungkar, единственное число) = Создатель или Гуру — не человек с титулом.\n'
    '   Пример: ਭਾਗੁ ਹੋਆ ਗੁਰਿ ਸੰਤੁ ਮਿਲਾਇਆ (СГГС 97) = "Удача улыбнулась, и я объединился '
    'со Святым Гуру (внутри)".\n\n'
    '2. ਸੰਤ (mukta, множественное число) = обычные сикхи, искатели Оангкара (Создателя). '
    '"Достичь пыли стоп сантов" = осознать Хукам через бхагатов.\n\n'
    '3. "Санты Бенареса" (ਬਾਨਾਰਸਿ ਕੇ ਠਗ, bukv. "аферисты Бенареса") — отдельная группа, '
    'которая сама называет себя сантами; прямо критикуется в Гурбани как мошенники. '
    'Кабир (СГГС 476): ਓਇ ਹਰਿ ਕੇ ਸੰਤ ਨ ਆਖੀਅਹਿ ਬਾਨਾਰਸਿ ਕੇ ਠਗ = '
    '"Они не могут зваться святыми Хара — они мошенники Бенареса".\n\n'
    '4. ਸੰਤ ਧੂਰਿ (Sant Dhuur) = не "пыль со стоп", а "сообщения, приводящие к реализации '
    'Создателя" (Creator Connecting Messages). '
    'Dhuur = послания, содержащиеся в шабде; Sant происходит от Sat = '
    'стремление установить связь с Оангкаром. '
    'Sant Dhuur — это внутреннее содержание шабда, ведущее к реализации, '
    'а не указание следовать за каким-то бабой-сантом.'
)

gurbani_ref = (
    'СГГС 97: ਭਾਗੁ ਹੋਆ ਗੁਰਿ ਸੰਤੁ ਮਿਲਾਇਆ — ਸੰਤੁ (aungkar) = Гуру/Создатель\n'
    'СГГС 476 (Кабир): ਓਇ ਹਰਿ ਕੇ ਸੰਤ ਨ ਆਖੀਅਹਿ ਬਾਨਾਰਸਿ ਕੇ ਠਗ — '
    'ਬਾਨਾਰਸਿ ਕੇ ਠਗ = мошенники, присвоившие имя "сант"'
)

source = 'word_sant_in_gurbani.txt; Karminder Singh Dhillon — Hijacking Of Sikhi (sikhivicharforum.org)'

cur.execute(
    'INSERT INTO canvas_concepts (concept, traditional, ksd_meaning, gurbani_ref, source) VALUES (?,?,?,?,?)',
    (concept, traditional, ksd_meaning, gurbani_ref, source)
)

conn.commit()
cur.execute('SELECT id FROM canvas_concepts ORDER BY id DESC LIMIT 1')
new_id = cur.fetchone()[0]
print(f'Added concept id={new_id}: Sant')
cur.execute('SELECT COUNT(*) FROM canvas_concepts')
print(f'Total canvas_concepts: {cur.fetchone()[0]}')
