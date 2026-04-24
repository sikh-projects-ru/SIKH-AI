import sqlite3
conn = sqlite3.connect('ksd_knowledge.db')
cur = conn.cursor()

rules = [
    # Page 91 — satu as virtue/chastity noun; kali vs kal
    ('word_form', 'satu_virtue_noun',
     'ਸਤੁ (aungkar) = virtue/chastity/giving as concrete noun (act of purity, charity); distinct from ਸਤਿ (adjective "True")',
     'ਸਤੁ / ਸਤ',
     'ਸੁਣਿਐ ਸਤੁ ਸੰਤੋਖੁ ਗਿਆਣੁ (Jap Ji) = truth-virtue, contentment, wisdom | ਸਤੁ ਸੀਗਾਰ ਭਉ ਅੰਜਨੁ ਪਾਇਆ (Suhi M:5) = virtue-chastity as adornment | ਪਤਿ ਵਿਣੁ ਪੂਜਾ ਸਤ ਵਿਣੁ ਸੰਜਮ (Ramkali M:1) = without virtue, discipline is empty', 'grammar_pdf_p91'),

    ('word_form', 'kali_vs_kal',
     'ਕਲਿ (sihari) = Kalyug (dark age) OR anxiety/mental anguish; ਕਲ (no sihari) = art/skill/power/plan — no sihari when meaning is craft or creative power',
     'ਕਲਿ / ਕਲ',
     'ਕਲਿ ਕਲੇਸ ਮਿਟੰਤ ਸਿਮਰਣਿ (Gujari M:5) = anxieties of Kalyug removed | ਆਪੇ ਹੀ ਕਰਣਾ ਕੀਓ ਕਲ ਆਪੇ ਹੀ ਤੈ ਧਾਰੀਓ (Asa di Var) = You Yourself created the art/power — ਕਲ=skill, no sihari', 'grammar_pdf_p91'),

    # Page 93 — additional word-form distinctions
    ('word_form', 'sathi_number_vs_fool',
     'ਸਠਿ (sihari) = 68 (number, from Sanskrit ਸ਼ਾਸ਼ਟਿ); ਸਠੀ = older form of the same; ਸਠ (mukta) = fool/stubborn',
     'ਸਠਿ / ਸਠੀ / ਸਠ',
     'ਸੁਣਿਐ ਅਠਸਠਿ ਕਾ ਇਸਨਾਣੁ (Jap Ji) = hearing [equals bathing at] 68 pilgrimage sites | ਸਠ ਕਠੋਰੁ ਕੁਲਹੀਣੁ ਬਿਆਪਤ ਮੋਹੁ ਕੀਚੁ (Asa M:5) = stubborn fool', 'grammar_pdf_p93'),

    ('word_form', 'koti_million_vs_kot_fort',
     'ਕੋਟਿ (sihari on ਟ) = ten million/crore (number); ਕੋਟੁ/ਕੋਟ (aungkar/mukta) = fort/fortress',
     'ਕੋਟਿ / ਕੋਟੁ',
     'ਕੋਟਿ = ten million (cardinal number, original sihari) | ਕੋਟੁ = fort — no sihari when meaning is fort', 'grammar_pdf_p93'),

    ('word_form', 'hasti_elephant_vs_hast',
     'ਹਸਤਿ/ਹਸਤੀ (sihari/bihari) = elephant; ਹਸਤੁ/ਹਸਤ (aungkar/mukta) = happen, hand, or laughing — opposite meanings, same spelling root',
     'ਹਸਤਿ / ਹਸਤੁ',
     'ਹਸਤਿ (elephant) takes sihari/bihari | when meaning is "to happen" or "hand" or "laughter" then aungkar or mukta', 'grammar_pdf_p93'),

    ('word_form', 'sudhi_vs_sudhu',
     'ਸੁਧਿ (sihari) = realization/awareness/consciousness; ਸੁਧੁ (aungkar) = corrected/purified/set right',
     'ਸੁਧਿ / ਸੁਧੁ',
     'ਸੁਧਿ = spiritual awareness (abstract noun, original sihari) | ਸੁਧੁ = one who is corrected (adjective/noun)', 'grammar_pdf_p93'),

    ('word_form', 'murti_vs_murtu',
     'ਮੂਰਤਿ (sihari) = idol/image/form (original sihari, from Sanskrit ਮੂਰ੍ਤਿ); ਮੂਰਤੁ (aungkar) = auspicious time/muhurat (ਮੁਹੂਰਤ)',
     'ਮੂਰਤਿ / ਮੂਰਤੁ',
     'ਮੂਰਤਿ = idol/divine form (sihari permanent) | ਮੂਰਤੁ = muhurat/auspicious moment (aungkar, different word)', 'grammar_pdf_p93'),

    # Page 94 — Section 30.2 Feminine agent nouns -ਣਿ ending
    ('gender', 'feminine_agent_noun_ni_ending',
     'Section 30.2: feminine agent/role nouns end in -ਣਿ (ਣ + sihari); masculine counterpart has -ਣ/ਣੁ; these are professional/relational feminine nouns',
     'ਭੰਡਾਰਣਿ, ਸੋਹਾਗਣਿ, ਪਰਦੇਸਣਿ, ਕਲਾਲਣਿ, ਬੈਰਣਿ, ਮਾਲਣਿ, ਬਨਜਾਰਣਿ, ਸਾਹਣਿ, ਸਾਪਣਿ, ਸਰਪਣਿ, ਜਲਣਿ, ਦਾਮਣਿ, ਵਰਤਣਿ, ਪੜੋਸਣਿ, ਸਉਕਣਿ, ਗੀਹਣਿ, ਤਾਜਣਿ, ਘਾਣਿ, ਕਾਣਿ, ਆਣਿ, ਪਾਣਿ',
     'ਸੋਹਾਗਣਿ = fortunate/married woman | ਕਲਾਲਣਿ = wine-seller woman | ਦਾਮਣਿ = lightning | ਪੜੋਸਣਿ = neighbor woman', 'grammar_pdf_p94'),

    ('word_form', 'kaman_charm_vs_kamani_woman',
     'ਕਾਮਣ (mukta) = charm/spell/love-talisman; ਕਾਮਣਿ (sihari) = woman — same root, opposite roles in same verse',
     'ਕਾਮਣ / ਕਾਮਣਿ',
     'ਗੁਣਿ ਕਾਮਣ ਕਾਮਣਿ ਕਰੈ ਤਉ ਪਿਆਰੇ ਕਉ ਪਾਵੈ (Tilang M:1) = the woman (ਕਾਮਣਿ) makes a charm (ਕਾਮਣ) of virtues [and] obtains her beloved groom', 'grammar_pdf_p94'),

    # Page 95 — taruni vs taranu vs tarun; additional feminine list
    ('word_form', 'taruni_vs_taranu_vs_tarun',
     'ਤਰੁਣਿ (sihari) = young woman; ਤਰਣੁ (aungkar on ਣ) = swimming/crossing over (verbal noun); ਤਰੁਣ (mukta) = youth/adolescence — three distinct meanings from similar forms',
     'ਤਰੁਣਿ / ਤਰਣੁ / ਤਰੁਣ',
     'ਜੈਸੀ ਤਰੁਣਿ ਭਤਾਰ ਉਰਝੀ (Asa M:5) = woman attached to husband | ਤਰਣੁ ਦੁਹੇਲਾ ਭਇਆ ਖਿਨ ਮਹਿ ਖਸਮੁ ਚਿਤਿ ਨ ਆਇਓ (Asa M:5) = crossing [over] became difficult — ਤਰਣੁ is verb-noun NOT woman despite ਖਸਮੁ in same line', 'grammar_pdf_p95'),

    ('principle', 'context_determines_gender_not_neighboring_words',
     'do not assign gender based on neighboring words in verse; ਤਰਣੁ is wrongly read as "woman" because ਖਸਮੁ (husband) appears in same line — grammar (aungkar on ਣ) determines meaning, not context of surrounding nouns',
     'ਤਰਣੁ misread as woman',
     'ਤਰਣੁ ਦੁਹੇਲਾ ਭਇਆ ਖਿਨ ਮਹਿ ਖਸਮੁ ਚਿਤਿ ਨ ਆਇਓ (Asa M:5) — ਤਰਣੁ (aungkar)=crossing, not woman; ਤਰੁਣਿ (sihari) would mean woman', 'grammar_pdf_p95'),

    ('gender', 'feminine_sihari_additional_list',
     'additional feminine words with original/permanent sihari: ਬੇਲਿ/ਵੇਲਿ, ਦਾਲਿ, ਭਾਲਿ, ਭੀਤਿ, ਕਰਤੂਤਿ, ਦਾਤਿ, ਤਪਤਿ, ਮਸੀਤਿ, ਹਟਤਾਰਿ, ਲਬਧਿ, ਨਦਰਿ, ਖਬਰਿ, ਡੋਰਿ, ਵਾਰਿ/ਵਾੜਿ, ਅਰਦਾਸਿ, ਫੁਰਮਾਇਸਿ, ਸਾਬਾਸਿ, ਰਹਰਾਸਿ, ਰਾਸਿ',
     'ਭੀਤਿ=wall(f), ਕਰਤੂਤਿ=deed(f), ਦਾਤਿ=gift(f), ਨਦਰਿ=grace(f), ਖਬਰਿ=news(f), ਅਰਦਾਸਿ=prayer(f), ਰਹਰਾਸਿ=evening prayer(f)',
     'all these feminine nouns carry permanent sihari regardless of grammatical position', 'grammar_pdf_p95'),

    # Page 97 — Section 30.4 Arabic -ਤਿ extended list
    ('gender', 'arabic_feminine_ti_extended_list',
     'Section 30.4: extended list of Arabic-origin feminine nouns ending in -ਤਿ; all take permanent sihari on ਤ',
     'ਕੁਦਰਤਿ, ਸਿਫਤਿ, ਹਿਕਮਤਿ, ਹੁਜਤਿ, ਮਿਹਰਾਮਤਿ, ਸਰੀਅਤਿ, ਹੁਰਮਤਿ, ਗੈਰਤਿ, ਕਰਮਾਤਿ, ਸਲਾਮਤਿ, ਕੀਮਤਿ, ਮੁਸਕਤਿ, ਮੁਹਲਤਿ, ਨਉਬਤਿ, ਨੀਅਤਿ, ਹੈਰਤਿ, ਜਰੂਰਤਿ, ਖਿਜਮਤਿ, ਦਉਲਤਿ, ਮਿੰਨਤਿ, ਖਸਲਤਿ, ਨਿਆਮਤਿ, ਸੁਨਤਿ, ਮੁਹਬਤਿ, ਤਰੀਕਤਿ, ਮਸਲਤਿ, ਉਮਤਿ',
     'all Arabic feminine words ending in -ਤ take permanent sihari = -ਤਿ; this is a large category of loanwords', 'grammar_pdf_p97'),

    # Page 97 — Section 31.0/2.0 Count indefinite plural
    ('word_form', 'eki_plural_count',
     'ਏਕਿ (sihari) = indefinite plural "some/certain ones" (parallel to ਇਕਿ); ਏਕੁ (aungkar) = singular "one/the One"',
     'ਏਕਿ / ਏਕੁ',
     'ਏਕਿ ਨਚਾਵਹਿ ਏਕਿ ਭਵਾਵਹਿ ਇਕਿ ਆਇ ਜਾਇ ਹੋਇ ਧੂਰਾ (Ramkali M:5) = some He makes dance, some He makes wander', 'grammar_pdf_p97'),

    # Page 99 — hori/avari plural confirmation
    ('principle', 'count_words_sihari_plural_aungkar_singular',
     'systematic pattern for count/numeral words: aungkar or mukta = singular; sihari = indefinite plural — applies to ਇਕਿ/ਇਕੁ, ਹਿਕਿ/ਹਿਕੁ, ਏਕਿ/ਏਕੁ, ਹੋਰਿ/ਹੋਰੁ, ਅਵਰਿ/ਅਵਰੁ',
     'ਹੋਰਿ/ਹੋਰੁ, ਅਵਰਿ/ਅਵਰੁ pattern',
     'ਧਰਤੀ ਹੋਰੁ ਪਰੈ ਹੋਰੁ ਹੋਰੁ (Jap Ji) = singular | ਹੋਰਿ ਕੇਤੇ ਗਾਵਨਿ ਸੇ ਮੈ ਚਿਤਿ ਨ ਆਵਨਿ (Jap Ji) = plural | ਅਵਰਿ ਉਪਾਵ ਸਭਿ ਤਿਆਗਿਆ (Bilaval M:5) = all other means [plural]', 'grammar_pdf_p99'),

    # Page 98 — critical parsing: ika-apinai patlI
    ('principle', 'sihari_determines_ik_meaning',
     'if ਇਕ means "some" (indefinite plural pronoun) then ਕ must have sihari = ਇਕਿ; if sihari absent and word ਪਤਿ follows, ਪਤਿ means honor (with sihari) — absence of sihari on ਇਕ forces different reading of whole verse',
     'ਇਕਿ vs ਇਕ — determines meaning of entire verse',
     '"ਇਕ ਆਪੀਨੈ ਪਤਲੀ ਸਹ ਕੇਰੇ ਬੋਲਾ" — if ਇਕ = "some", ਕ needs sihari; ਪਤਲੀ is Urdu (not Farid\'s language); correct reading from old sakhi: one woman is weak, Master\'s commands are hard on her', 'grammar_pdf_p98'),
]

cur.executemany('''
    INSERT INTO grammar_rules (category, pattern, meaning, example_word, example_meaning, source)
    VALUES (?, ?, ?, ?, ?, ?)
''', rules)

conn.commit()
print(f'Added {len(rules)} rules')
cur.execute('SELECT COUNT(*) FROM grammar_rules')
print(f'Total grammar_rules: {cur.fetchone()[0]}')
