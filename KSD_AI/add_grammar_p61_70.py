import sqlite3
conn = sqlite3.connect('ksd_knowledge.db')
cur = conn.cursor()

rules = [
    # Page 61 — 15.3 Feminine Noun Sihari (adjectives as feminine nouns)
    ('gender', 'feminine_adjective_as_noun_sihari',
     'adjectives used as feminine nouns take sihari; same adjective without sihari is masculine',
     'ਸੁੰਦਰਿ, ਸੁਜਾਣਿ, ਚਤੁਰਿ, ਚੰਚਲਿ, ਸੁਘਰਿ, ਨਿਰਗੁਣਿ, ਪਰਧਾਨਿ, ਕਰੂਪਿ, ਸਰੂਪਿ, ਬੇਪੀਰਿ, ਕੁੜਿਆਰਿ, ਸੇਵਕਿ',
     'ਸੁੰਦਰਿ ਸੁਜਾਣਿ ਚਤੁਰਿ ਬੇਟੀ (Ramkali M:5) = beautiful wise clever daughter | vs ਸੁੰਦਰ ਸੁਘਰ ਸਰੂਪ ਸਿਆਣੇ (Asa M:5, masculine)', 'grammar_pdf_p61'),

    ('word_form', 'ਸੇਵਕਿ_feminine',
     'ਸੇਵਕਿ (sihari) = female servant (feminine form); ਸੇਵਕੁ (aungkar) = male servant',
     'ਸੇਵਕਿ / ਸੇਵਕੁ',
     'ਹਿਰਦੈ ਹਰਿ ਹਰਿ ਨਾਮ ਰਸੁ ਕਵਲਾ ਸੇਵਕਿ ਤਿਸੁ (M:3, Var Bilaval) = Lakshmi is servant of that one', 'grammar_pdf_p61'),

    # Page 62 — 15.4 Arabic Feminine Nouns: -ਤਿ ending
    ('gender', 'arabic_feminine_ti_ending',
     'Arabic-origin feminine nouns ending in ਤ take sihari = -ਤਿ ending; large category of Arabic loanwords in Gurbani',
     'ਕੁਦਰਤਿ, ਸਿਫਤਿ, ਹਿਕਮਤਿ, ਹੁਰਮਤਿ, ਕੀਮਤਿ, ਸਲਾਮਤਿ, ਦਉਲਤਿ, ਮਿੰਨਤਿ, ਨਿਆਮਤਿ, ਸੁਨਤਿ, ਮੁਹਬਤਿ, ਤਰੀਕਤਿ, ਨੀਅਤਿ, ਹੈਰਤਿ, ਜਰੂਰਤਿ, ਉਮਤਿ',
     'all Arabic feminine words in Gurbani end in -ਤਿ (sihari on ਤ)', 'grammar_pdf_p62'),

    # Section 16.0 (pages 63-65) — Count/Numeral (ਸੰਖਿਆਵਾਚਕ)
    ('word_form', 'ਇਕਿ_indefinite_plural',
     'ਇਕ (no sihari) = singular "one"; ਇਕਿ (sihari) = indefinite plural pronoun/adjective "some/certain ones"',
     'ਇਕ / ਇਕਿ',
     'ਇਕਿ ਘਰਿ ਆਵਹਿ ਆਪਣੈ ਇਕਿ ਮਿਲਿ ਮਿਲਿ ਪੁਛਹਿ ਸੁਖੁ (Asa M:1) = some come home, some ask about wellbeing', 'grammar_pdf_p63'),

    ('word_form', 'ਹਿਕਿ_vs_ਹਿਕੁ',
     'ਹਿਕੁ (aungkar) = singular "one"; ਹਿਕਿ (sihari) = plural "some/ones" (Punjabi dialect form of ਇਕ)',
     'ਹਿਕੁ / ਹਿਕਿ',
     'ਬਨਿ ਭੀਆਵਲੇ ਹਿਕੁ ਸਾਥੀ ਲਧਮੁ (M:5 Var Gujari) = singular | ਹਿਕ ਦੂੰ ਹਿਕਿ ਚਾੜੇ ਅਨਿਕ ਪਿਆਰੇ (Jetsari M:5) = plural', 'grammar_pdf_p64'),

    ('word_form', 'ਹੋਰਿ_vs_ਹੋਰੁ',
     'ਹੋਰੁ/ਹੋਰ (aungkar/no syllable) = singular "another/other"; ਹੋਰਿ (sihari on ਰ) = plural "others"',
     'ਹੋਰੁ / ਹੋਰਿ',
     'ਧਰਤੀ ਹੋਰੁ ਪਰੈ ਹੋਰੁ ਹੋਰੁ (Jap Ji) = singular | ਹੋਰਿ ਕੇਤੇ ਗਾਵਨਿ ਸੇ ਮੈ ਚਿਤਿ ਨ ਆਵਨਿ (Jap Ji) = plural others', 'grammar_pdf_p65'),

    ('word_form', 'ਅਵਰਿ_vs_ਅਵਰੁ',
     'ਅਵਰੁ (aungkar) = singular "another/other one"; ਅਵਰਿ (sihari) = plural "others/all other means"',
     'ਅਵਰੁ / ਅਵਰਿ',
     'ਕਹੈ ਪ੍ਰਭੁ ਅਵਰੁ ਅਵਰੁ ਕਿਛੁ ਕੀਜੈ (Bilaval M:4) = singular | ਅਵਰਿ ਉਪਾਵ ਸਭਿ ਤਿਆਗਿਆ (Bilaval M:5) = all other means', 'grammar_pdf_p65'),

    # Section 17.0 (pages 65-66) — Demonstrative Pronouns
    ('word_class', 'demonstrative_gender_marking',
     'demonstrative pronouns/adjectives (ਇਹੁ, ਏਹੁ, ਓਹੁ): masculine singular = aungkar on ਹ; feminine singular = sihari on ਹ; plural = sihari on ਹ',
     'ਇਹੁ/ਇਹਿ, ਏਹੁ/ਏਹਿ, ਓਹੁ/ਓਹਿ',
     'ਜਿਨਿ ਏਹਿ ਲਿਖੇ ਤਿਸੁ ਸਿਰਿ ਨਾਹਿ (Jap Ji) = ਏਹਿ plural (these) | ਨਾ ਓਹਿ ਮਰਹਿ ਨ ਠਾਗੇ ਜਾਹਿ (Jap Ji) = ਓਹਿ plural (they)', 'grammar_pdf_p66'),

    # Section 18.0 (pages 67-70) — Past Tense Agent Sihari
    ('tense', 'past_tense_agent_sihari',
     'past tense: sihari on the agent/subject marks who performed the past action; sihari also lengthens pronunciation (ਕਿ sounds like ਕੇ, ਤਿ like ਤੇ)',
     'ਗੁਰਿ, ਪ੍ਰਭਿ, ਪੁਰਖਿ, ਪਰਮੇਸੁਰਿ, ਸਤਿਗੁਰਿ, ਬਾਪਿ, ਪਿਰਿ, ਮੁਰਖਿ, ਜਿਨਿ, ਤਿਨਿ, ਆਪਿ',
     'ਗੁਰਿ ਹਾਥੁ ਧਰਿਓ ਮੇਰੈ ਮਾਥਾ (Jetsari M:4) = Guru placed hand | ਸਰਬ ਕਲਿਆਣ ਪ੍ਰਭਿ ਕੀਨੇ (Sorath M:5) = Prabh did', 'grammar_pdf_p67'),

    ('word_form', 'past_agent_contraction',
     'past agent marker can contract: ਸੁਲਤਾਣੇ = ਸੁਲਤਾਣਿ ਦੇ ("by the Sultan"); ਕਰਤਾਰੇ = ਕਰਤਾਰਿ ਦੇ ("by the Creator") — oblique agentive contraction',
     'ਸੁਲਤਾਣੇ / ਕਰਤਾਰੇ',
     'ਨਾਮਾ ਸੁਲਤਾਣੇ ਬਾਧਿਲਾ (Bhairo Namdev) | ਠਾਵਿ ਪਾਈ ਕਰਤਾਰੇ (Sorath M:5)', 'grammar_pdf_p67'),

    ('word_form', 'ਜਿਨਿ_creator_vs_ਜਿਨ_pronoun',
     'ਜਿਨਿ (sihari) = past agent "Creator/Almighty who did [action]"; ਜਿਨ (no sihari) = relative pronoun "those who / whoever"',
     'ਜਿਨਿ / ਜਿਨ',
     'ਜਿਨਿ ਹਰਿ ਪਾਇਓ ਤਿਨਹਿ ਛਪਾਇਓ (Todi Namdev) = Creator found/hid | ਜਿਨ ਮਨਿ ਪ੍ਰੀਤਿ ਲਗੀ ਹਰਿ ਕੇਰੀ (Jetsari M:4) = those whose minds are attached', 'grammar_pdf_p68'),

    ('word_form', 'ਤਿਨਿ_creator_vs_ਤਿਨ_pronoun',
     'ਤਿਨਿ (sihari) = past agent "Creator" OR number three (3); ਤਿਨ (no sihari) = pronoun "those/they"',
     'ਤਿਨਿ / ਤਿਨ',
     'ਜਿਸਕਾ ਸਾ ਤਿਨਿ ਲੀਆ ਮਿਲਾਇ (Sukhmani) = Creator united | ਤਿਣਿ ਚੇਲੇ ਪਰਵਾਣੁ (Jap Ji) = three disciples (number 3) | ਤਿਨ ਹੋਵਤ ਆਤਮ ਪਰਗਾਸ (Sukhmani) = those who (pronoun)', 'grammar_pdf_p69'),

    ('word_form', 'ਆਪਿ_creator_and_being',
     'ਆਪਿ (sihari) = Creator/Almighty as past agent OR "the being/self" (sihari used because being and Creator are one — theological point)',
     'ਆਪਿ',
     'ਜਿਨ ਕਉ ਆਪਿ ਦੇਇ ਵਡਿਆਈ (M:4 Var Gauri) = Creator gives | ਆਪਿ ਜਪਹੁ ਅਵਰਾ ਨਾਮੁ ਜਪਾਵਹੁ (Sukhmani) = the being (sihari: being = Creator)', 'grammar_pdf_p70'),
]

cur.executemany('''
    INSERT INTO grammar_rules (category, pattern, meaning, example_word, example_meaning, source)
    VALUES (?, ?, ?, ?, ?, ?)
''', rules)

conn.commit()
print(f'Added {len(rules)} rules')
cur.execute('SELECT COUNT(*) FROM grammar_rules')
print(f'Total grammar_rules: {cur.fetchone()[0]}')
