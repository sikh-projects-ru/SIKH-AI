import sqlite3
conn = sqlite3.connect('ksd_knowledge.db')
cur = conn.cursor()

rules = [
    # Page 102 — Section 32.0 Demonstratives: sihari = plural even for masculine
    ('word_class', 'demonstrative_sihari_plural_masculine',
     'Section 32.0: demonstrative pronouns ਇਹੁ/ਏਹੁ/ਓਹੁ — aungkar on ਹ = masculine singular; sihari on ਹ = feminine singular OR plural (including masculine plural); sihari overrides gender to mark plurality',
     'ਇਹੁ/ਇਹਿ, ਏਹੁ/ਏਹਿ, ਓਹੁ/ਓਹਿ/ਓਇ',
     'ਸਹਸਾ ਇਹੁ ਸੰਸਾਰੁ ਹੈ (masculine sg) | ਪ੍ਰਭੁ ਮਿਲਣੈ ਕੀ ਏਹ ਨੀਸਾਣੀ (feminine sg) | ਜਿਨਿ ਏਹਿ ਲਿਖੇ ਤਿਸੁ ਸਿਰਿ ਨਾਹਿ (Jap Ji) = ਏਹਿ plural, sihari on masculine word', 'grammar_pdf_p102'),

    ('word_form', 'ohi_oie_plural',
     'ਓਹੁ (aungkar) = singular "that one/He"; ਓਹਿ/ਓਇ (sihari) = plural "those/they"',
     'ਓਹੁ / ਓਹਿ / ਓਇ',
     'ਨਾਨਕ ਓਹੁ ਪੁਰਖੁ ਕਹੀਐ ਜੀਵਨ ਮੁਕਤਿ (Sukhmani) = singular | ਨਾ ਓਹਿ ਮਰਹਿ ਨ ਠਾਗੇ ਜਾਹਿ (Jap Ji) = plural | ਓਇ ਮਨੁਖ ਮੁੜ ਅਗਿਆਨੀ ਕਹੀਅਹਿ (Todi M:4) = plural variant ਓਇ', 'grammar_pdf_p102'),

    # Pages 103-105 — Section 33.0 Past Tense agents (extended examples)
    ('tense', 'past_agent_extended_examples',
     'Section 33.0: extended list of past tense agent markers with sihari — sihari prolongs the vowel (ਕਿ sounds like ਕੇ, ਤਿ like ਤੇ); covers Guru names, divine titles, and human agents',
     'ਗੁਰਿ, ਪਰਮੇਸੁਰਿ, ਪ੍ਰਭਿ, ਪੁਰਖਿ, ਸਤਿਗੁਰਿ, ਬਾਪਿ, ਪਿਰਿ, ਮੁਰਖਿ, ਜਿਨਿ, ਤਿਨਿ, ਆਪਿ',
     'ਹਾਥ ਦੇਇ ਰਾਖੇ ਪਰਮੇਸੁਰਿ ਸਗਲਾ ਦੁਰਤੁ ਮਿਟਾਇਆ (Gujari M:5) | ਕਰਤੈ ਪੁਰਖਿ ਤਾਲੁ ਦਿਵਾਇਆ (Sorath M:5) | ਬਾਪਿ ਦਿਲਾਸਾ ਮੇਰੋ ਕੀਨਾ (Asa Kabir) = Father gave comfort', 'grammar_pdf_p103'),

    ('word_form', 'bapi_past_agent_father',
     'ਬਾਪਿ (sihari) = father as past agent "Father did [action]"; ਬਾਪ (mukta) = father as noun object — both in same verse',
     'ਬਾਪਿ / ਬਾਪ',
     'ਬਾਪਿ ਦਿਲਾਸਾ ਮੇਰੋ ਕੀਨਾ। ਸੇਜ ਸੁਖਾਲੀ ਮੁਖਿ ਅੰਮ੍ਰਿਤੁ ਦੀਨਾ। ਤਿਸੁ ਬਾਪ ਕਉ ਕਿਉ ਮਨਹੁ ਵਿਸਾਰੀ (Asa Kabir) = ਬਾਪਿ (agent), ਬਾਪ (object of ਕਉ)', 'grammar_pdf_p104'),

    ('word_form', 'jini_agent_vs_jin_relative',
     'ਜਿਨਿ (sihari) = Creator as past agent "Creator who did"; ਜਿਨ (no sihari) = relative pronoun "those who/whoever" referring to humans',
     'ਜਿਨਿ / ਜਿਨ',
     'ਜਿਨਿ ਹਰਿ ਪਾਇਓ ਤਿਨਹਿ ਛਪਾਇਓ (Todi Namdev) = Creator who found [Hari] hid it | ਜਿਨ ਮਨਿ ਪ੍ਰੀਤਿ ਲਗੀ ਹਰਿ ਕੇਰੀ ਤਿਨ ਧੁਰਿ ਭਾਗ ਪੁਰਾਣਾ (Jetsari M:4) = those whose minds [human plural, no sihari]', 'grammar_pdf_p104'),

    ('word_form', 'tini_creator_vs_tin_pronoun_vs_number',
     'ਤਿਨਿ (sihari on ਨ) = Creator as past agent OR number three (3); ਤਿਨ (no sihari) = pronoun "those/they" (human, plural)',
     'ਤਿਨਿ / ਤਿਨ',
     'ਜਿਸਕਾ ਸਾ ਤਿਨਿ ਲੀਆ ਮਿਲਾਇ (Sukhmani) = Creator united | ਤਿਣਿ ਚੇਲੇ ਪਰਵਾਣੁ (Jap Ji) = three disciples [number] | ਤਿਨ ਹੋਵਤ ਆਤਮ ਪਰਗਾਸ (Sukhmani) = those who [pronoun, no sihari]', 'grammar_pdf_p105'),

    # Pages 105-107 — ਆਪਿ / ਆਪੁ / ਆਪ full disambiguation
    ('word_form', 'aapi_apu_aap_full_disambiguation',
     'three forms: ਆਪਿ (sihari) = Creator as past agent OR Being (whose self is one with Creator); ਆਪੁ (aungkar) = ego-self / His own self; ਆਪ (mukta) = reflexive "himself/itself"',
     'ਆਪਿ / ਆਪੁ / ਆਪ',
     'ਜਬ ਆਪਨ ਆਪੁ ਆਪਿ ਉਰਿ ਧਾਰੈ (Sukhmani) = ਆਪਿ=Creator, ਆਪੁ=Himself | ਸਤਿਗੁਰਿ ਮਿਲਿਐ ਸਚੁ ਪਾਇਆ ਜਿਨੀ ਵਿਚਹੁ ਆਪੁ ਗਵਾਇਆ = ਆਪੁ=ego | ਸਭ ਪਵੈ ਪੈਰੀ ਸਤਿਗੁਰੁ ਕੇਰੀ ਜਿਥੈ ਗੁਰੁ ਆਪ ਰਖਿਆ = ਆਪ=reflexive himself', 'grammar_pdf_p106'),

    ('principle', 'aapinai_aap_correct_reading',
     '"ਆਪੀਨੈ ਆਪੁ ਸਾਜਿਓ ਆਪੀਨੈ ਰਚਿਓ ਨਾਉ" (Asa di Var) is misread as "Creator created the world Himself and created names for beings" — wrong; ਆਪੁ = reflexive "He Himself" (not world-creation); correct: He Himself, appearing in both Nirgun and Sargun forms, no other created Him',
     'ਆਪੀਨੈ ਆਪੁ ਸਾਜਿਓ',
     'ਆਪਨਾ ਆਪੁ ਉਪਾਇਓਨੁ, ਤਦਹੁ ਹੋਰੁ ਨ ਕੋਈ (Gujari di Var M:3) — before creation He was alone; this confirms ਆਪੁ=His own self, no other created Him', 'grammar_pdf_p107'),

    # Page 108 — Section 34.0 Sihari for Greater Matr
    ('vowel_mark', 'sihari_for_greater_matr_bihari_substitution',
     'Section 34.0: sihari replaces bihari (and other long vowels) when poem requires shorter matra count; full list of bihari→sihari substitutions in Gurbani verse',
     'ਚਾਲਿਸ=ਚਾਲਸੀ, ਹੋਵਿਗ=ਹੋਵੇਗੀ, ਵਜਿਗ=ਵੱਜੇਗੀ, ਆਵਿਗ=ਆਵੇਗੀ, ਬਾਣਿ=ਬਾਣੀ, ਸਭਿ=ਸਭੀ, ਲੇਖਣਿ=ਲੇਖਣੀ, ਮੇਦਨਿ=ਮੇਦਨੀ, ਬਲਿ=ਬਲੀ, ਭਿ=ਭੀ, ਜਨਨਿ=ਜਨਨੀ, ਮਣਿ=ਮਣੀ, ਦੁਬਲਿ=ਦੁਬਲੀ',
     'sihari is the "short" form of bihari for metrical purposes; meaning is identical', 'grammar_pdf_p108'),

    ('word_form', 'suri_muni_sihari_for_bihari',
     'ਸੁਰਿ (sihari) = ਸੁਰੀ = deity/divine one; ਮੁਨਿ (sihari) = ਮੁਨੀ = sage/hermit — sihari replaces bihari for meter; both are adjectives for persons',
     'ਸੁਰਿ / ਮੁਨਿ',
     'ਆਖਿ ਸੁਰਿ ਨਰ ਮੁਨਿ ਜਨ ਸੇਵ (Jap Ji) = deities say, men and sages serve | ਸੁਣਿਐ ਸਿਧ ਪੀਰ ਸੁਰਿ ਨਾਥ (Jap Ji) = ਸੁਰਿ=deity', 'grammar_pdf_p109'),

    # Page 109 — Laan replaced by sihari; chari examples
    ('word_form', 'chari_four_vs_char',
     'ਚਾਰਿ (sihari or laa\'n) = ਚਾਰੇ "all four" (stressed numeral with emphasis); ਚਾਰ (no syllable) = "four" (unstressed, simple count)',
     'ਚਾਰਿ / ਚਾਰ',
     'ਪੰਡਿਤ ਮੈਲੁ ਨ ਚੁਕਈ ਜੇ ਵੇਦ ਪੜਹਿ ਜੁਗ ਚਾਰਿ (M:3) = all four ages | ਇਹ ਮਾਇਆ ਕੀ ਸੋਭਾ ਚਾਰਿ ਦਿਹਾੜੇ ਜਾਦੀ (Asa M:3) = lasts only four days [emphatic] | ਚਾਰ ਪਦਾਰਥ ਜੇ ਕੋ ਮਾਗੈ (Sukhmani) = four gifts [simple count, no stress]', 'grammar_pdf_p110'),

    ('word_form', 'kinni_how_many',
     'ਕਿੰਨਿ (sihari) = ਕਿੰਨੇ "how many/where" — sihari replaces laa\'n for meter',
     'ਕਿੰਨਿ / ਕਿੰਨੇ',
     'ਜਿਮੀ ਪੁਛੈ ਅਸਮਾਨ ਫਰੀਦਾ ਖੇਵਟ ਕਿੰਨਿ ਗਏ (Asa) = earth asks sky: the ferryman, how many have gone?', 'grammar_pdf_p110'),

    # Page 110 — Section 35.0/4.0 Bihari plural preposition (continuation)
    ('vowel_mark', 'bihari_plural_preposition_restatement',
     'Section 35.1/4.1: bihari (ੀ) on end of plural noun = preposition meaning "to/by/with/from the [plurals]" — bihari marks the plural noun as taking a case relationship',
     'ਸਿਖੀ, ਅਖੀ, ਉਪਾਵੀ, ਅਖਰੀ',
     'bihari gives preposition meaning to plural nouns: ਸਿਖੀ=ਸਿੱਖਾਂ ਨੇ, ਅਖੀ=ਅੱਖਾਂ ਨੂੰ, ਉਪਾਵੀ=ਉਪਾਵਾਂ ਨਾਲ — this is the core plural preposition function of bihari', 'grammar_pdf_p110'),
]

cur.executemany('''
    INSERT INTO grammar_rules (category, pattern, meaning, example_word, example_meaning, source)
    VALUES (?, ?, ?, ?, ?, ?)
''', rules)

conn.commit()
print(f'Added {len(rules)} rules')
cur.execute('SELECT COUNT(*) FROM grammar_rules')
print(f'Total grammar_rules: {cur.fetchone()[0]}')
