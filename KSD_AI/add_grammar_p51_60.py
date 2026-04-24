import sqlite3
conn = sqlite3.connect('ksd_knowledge.db')
cur = conn.cursor()

rules = [
    # Page 51 — critical parsing example: ਸਾਲਾਹਨਿ vs ਸਾਲਾਹਣ
    ('word_form', 'ਸਾਲਾਹਨਿ_vs_ਸਾਲਾਹਣ',
     'ਸਾਲਾਹਨਿ (sihari on ਨ) = "they praise" (3rd person plural); ਸਾਲਾਹਣ (no sihari) = verb-noun "praise-worthy/deserving praise"',
     'ਸਾਲਾਹਨਿ / ਸਾਲਾਹਣ',
     'ਸੁਣਿਐ ਮੁਖ ਸਾਲਾਹਣ ਮੰਦੁ (Jap Ji) = "Whoever listened, even the wicked became praise-worthy" — NOT "wicked ones praise with their mouth"', 'grammar_pdf_p51'),

    ('word_form', 'ਮਰਨਿ_vs_ਮਰਨੁ',
     'ਮਰਨਿ (sihari on ਨ) = "they die" (3rd person plural present imperfect); ਮਰਨੁ (aungkar) = noun "death"',
     'ਮਰਨਿ / ਮਰਨੁ',
     'ਮਰਨਿ ਮੁਨਸਾ ਸੁਰਿਆ ਹਕੁ ਹੈ ਜੋ ਹੋਇ ਮਰਨਿ ਪਰਵਾਣੋ (Vadhans M:1) = those die who have been approved to die', 'grammar_pdf_p51'),

    # Section 14.2 (page 52) — Future Tense 3rd person plural: -ਸਨਿ ending
    ('tense', 'future_tense_3rd_plural_sni',
     'future tense (ਭਵਿਖੱਤ ਕਾਲ) 3rd person plural: verb ending in ਸ+ਨ takes sihari on final ਨ = "they will [do]"',
     'ਪਉਸਨਿ, ਜਾਸਨਿ, ਸਿੰਘਾਪਸਨਿ, ਬਹਸਨਿ',
     'ਤਲਬਾ ਪਉਸਨਿ ਆਕੀਆ ਬਾਕੀ ਜਿਨਾ ਰਹੀ (M:1, Var Ramkali) = rebels will be summoned who still owe a balance', 'grammar_pdf_p52'),

    # Section 14.3.1 (page 53) — Present Tense 3rd person plural: -ਹਿ ending
    ('tense', 'present_tense_3rd_plural_hi',
     'present tense (ਵਰਤਮਾਨ ਕਾਲ) 3rd person plural: verb ending in ਹ takes sihari = "they [do]"',
     'ਮਾਰਹਿ, ਲੁਟਹਿ',
     'ਮਾਰਹਿ ਲੁਟਹਿ ਨੀਤ ਨੀਤ (Gauri M:1) = they kill, they loot, again and again', 'grammar_pdf_p53'),

    # Section 14.3.2 (page 53) — Present Tense 2nd person singular: same -ਹਿ ending
    ('tense', 'present_tense_2nd_singular_hi',
     'present tense 2nd person singular (ਇਕ-ਵਚਨ ਮੱਧਮ ਪੁਰਖ): same -ਹਿ ending as 3rd plural; context determines person',
     'ਜੋਹਿ, ਰਹੀਏਹਿ, ਹੋਈਅਹਿ',
     'ਵੇਲਿ ਪਰਾਈ ਜੋਹਿ ਜੀਅੜੇ (Gauri M:1) = you spy on others opportunity | ਰਹੀਏਹਿ = you are left behind', 'grammar_pdf_p53'),

    # Section 15.1 (pages 53-59) — Original Sihari (ਮੂਲਿਕ ਸਿਹਾਰੀ)
    ('vowel_mark', 'original_sihari_inherited',
     'original/inherent sihari (ਮੂਲਿਕ ਸਿਹਾਰੀ): words borrowed from Sanskrit/Persian/Arabic that bring sihari from source language — it remains permanently regardless of grammatical function',
     'ਹਰਿ, ਨਾਰਿ, ਜੁਗਤਿ, ਧੁਨਿ, ਭੂਮਿ, ਧਰਤਿ, ਪ੍ਰੀਤਿ, ਆਦਿ, ਸਿਮ੍ਰਿਤਿ, ਸ਼ਕਤਿ, ਰੈਣਿ, ਰਾਤਿ, ਰੁਤਿ, ਸ੍ਰਿਸਟਿ, ਕੀਰਤਿ, ਜੋਤਿ, ਰੀਤਿ, ਅਤਿ, ਸਰਣਿ, ਨਿਧਿ, ਰਿਧਿ, ਸਿਧਿ, ਜੋਨਿ, ਸੁਰਤਿ, ਮੁਨਿ, ਤ੍ਰਿਪਤਿ, ਚਿੰਤਾਮਣਿ',
     'these always carry sihari — do not confuse with grammatical sihari endings', 'grammar_pdf_p54'),

    # Word pairs involving original sihari — pages 54-59
    ('word_form', 'ਭਗਤਿ_vs_ਭਗਤੁ',
     'ਭਗਤਿ (original sihari) = devotion/bhakti (abstract noun); ਭਗਤੁ (aungkar) = singular devotee (person); ਭਗਤ (no syllable) = plural devotees',
     'ਭਗਤਿ / ਭਗਤੁ / ਭਗਤ',
     'ਮੁਕਤਿ ਭੁਗਤਿ ਜੁਗਤਿ ਤੇਰੀ ਸੇਵਾ (Suhi M:5) | ਤੇਰੀ ਭਗਤਿ ਤੇਰੀ ਭਗਤਿ ਭੰਡਾਰ ਜੀ (Asa M:4)', 'grammar_pdf_p54'),

    ('word_form', 'ਮੁਕਤਿ_vs_ਮੁਕਤੁ',
     'ਮੁਕਤਿ (original sihari) = liberation (abstract noun); ਮੁਕਤੁ (aungkar) = liberated one (person)',
     'ਮੁਕਤਿ / ਮੁਕਤੁ',
     'ਇਹ ਜੀਉ ਸਦਾ ਮੁਕਤੁ ਹੈ (M:3 Var Gujari) — ਮੁਕਤੁ = liberated being (person)', 'grammar_pdf_p54'),

    ('word_form', 'ਗਤਿ_vs_ਗਤੁ',
     'ਗਤਿ (original sihari) = state/condition/spiritual state; ਗਤੁ/ਗਤ = "gone/past/happened" (different word entirely)',
     'ਗਤਿ / ਗਤੁ / ਗਤ',
     'ਨਾਮੋ ਗਤਿ ਨਾਮੋ ਪਤਿ ਜਨ ਕੀ (Dhanasari M:5) | ਅਪਿਓ ਪੀਓ ਗਤੁ ਭੀਓ ਭਰਮਾ (Jetsari M:5) = delusion is gone', 'grammar_pdf_p54'),

    ('word_form', 'ਬੁਧਿ_vs_ਬੁਧੁ',
     'ਬੁਧਿ (original sihari) = intellect/wisdom (abstract); ਬੁਧੁ = the wise one (person); ਸਿਧਿ = spiritual power (abstract); ਸਿਧੁ = siddha/adept (person)',
     'ਬੁਧਿ / ਬੁਧੁ / ਸਿਧਿ / ਸਿਧੁ',
     'ਰਿਧਿ ਬੁਧਿ ਸਿਧਿ ਗਿਆਨੁ ਸਦਾ ਸੁਖੁ ਹੋਇ (M:1 Var Malar) | ਭੈ ਵਿਚਿ ਸਿਧ ਬੁਧ ਸੁਰ ਨਾਥ (Asa di Var) = siddhas, wise ones, gods', 'grammar_pdf_p55'),

    ('word_form', 'ਮਤਿ_vs_ਮੱਤ',
     'ਮਤਿ (original sihari) = intellect/mind/reasoning (abstract noun); ਮੱਤ (no sihari, different root) = "drunk/intoxicated" or compound word element',
     'ਮਤਿ / ਮੱਤ',
     'ਮਤਿ ਥੋੜੀ ਸੇਵ ਗਵਾਈਐ (Asa di Var) = by little intellect, service is lost | ਮਨੁ ਮੈ ਮਤੁ ਮੈਗਲ ਮਿਕਦਾਰਾ (Dhanasari M:3) = mind drunk like an elephant', 'grammar_pdf_p55'),

    ('word_form', 'ਪਤਿ_vs_ਪਤੁ_vs_ਪਤ',
     'ਪਤਿ (original sihari) = husband OR honor/respect (two meanings, context dependent); ਪਤੁ (aungkar) = honor as abstract; ਪਤ (no syllable) = leaf/paper OR yogis begging bowl',
     'ਪਤਿ / ਪਤੁ / ਪਤ',
     'ਜਹ ਨਿਰਮਲ ਪੁਰਖੁ ਪੁਰਖ-ਪਤਿ ਹੋਤਾ (Sukhmani) = husband | ਮੁਰਖ ਅੰਧੈ ਪਤਿ ਗਵਾਈ (Asa di Var) = honor lost | ਫਲ ਫਿਕੇ ਫੁਲ ਬਕਬਕੇ ਕੰਮਿ ਨ ਆਵਹਿ ਪਤ (Asa di Var) = leaves (of no use)', 'grammar_pdf_p55'),

    ('word_form', 'ਮਿਤਿ_vs_ਮਿਤੁ',
     'ਮਿਤਿ (original sihari) = extent/measure/limit; ਮਿਤੁ (aungkar) = friend/companion',
     'ਮਿਤਿ / ਮਿਤੁ',
     'ਕਰਤੇ ਕੀ ਮਿਤਿ ਕਰਤਾ ਜਾਣੈ (Dakhni Oankar) = only Creator knows Creator extent | ਮਿਟੀ ਪਈ ਅਤੋਲਵੀ ਕੋਇ ਨ ਹੋਸੀ ਮਿਤੁ (Salok Farid) = no friend will come', 'grammar_pdf_p56'),

    ('word_form', 'ਸਤਿ_adjective_vs_ਸਤੁ_noun',
     'ਸਤਿ (adjective, original sihari) = True/Eternal (divine attribute, e.g. Sat Naam); ਸਤੁ (aungkar, noun) = charity/essence/purity/truth as quality',
     'ਸਤਿ / ਸਤੁ',
     'ਚਰਨ ਸਤਿ ਸਤਿ ਪਰਸਨਹਾਰ (Sukhmani) = True feet | ਸੁਣਿਐ ਸਤੁ ਸੰਤੋਖੁ ਗਿਆਨੁ (Jap Ji) = essence/charity heard | ਪਤਿ ਵਿਣੁ ਪੂਜਾ ਸਤ ਵਿਣੁ ਸੰਜਮ (Ramkali M:1) = without charity, restraint is futile', 'grammar_pdf_p56'),

    ('word_form', 'ਕਲਿ_vs_ਕਲ',
     'ਕਲਿ (sihari) = Kali Yuga (current age) OR mental distress/worry/anxiety; ਕਲ (no sihari) = skill/art/ability/power (no sihari when meaning skill)',
     'ਕਲਿ / ਕਲ',
     'ਕਲਿ ਕਲੇਸ ਮਿਟੰਤ ਸਿਮਰਣਿ ਕਾਟਿ ਜਮਦੂਤ ਵਾਸ (Gujari M:5) = distress of Kali Yuga | ਆਪੇ ਹੀ ਕਰਨਾ ਕੀਓ ਕਲ ਆਪੇ ਹੀ ਤੈ ਧਾਰੀਐ (Asa di Var) = ਕਲ = skill/power', 'grammar_pdf_p57'),

    ('word_form', 'ਕੋਟਿ_vs_ਕੋਟੁ',
     'ਕੋਟਿ (original sihari) = ten million/crore (number); ਕੋਟੁ (aungkar) = fort/castle',
     'ਕੋਟਿ / ਕੋਟੁ',
     'ਕੋਟਿ ਕੋਟਿ ਭਾਲਿ ਥਕੇ (Jap Ji) = millions searched | contrast with ਕੋਟੁ as fort', 'grammar_pdf_p59'),

    ('word_form', 'ਹਸਤਿ_vs_ਹਸਤੁ',
     'ਹਸਤਿ/ਹਸਤੀ (sihari/bihari) = elephant; ਹਸਤੁ/ਹਸਤ (aungkar/no syllable) = hand OR "happens/laughed"',
     'ਹਸਤਿ / ਹਸਤੁ',
     'sihari/bihari marks elephant meaning; aungkar/mukta marks hand or verb form', 'grammar_pdf_p59'),

    ('word_form', 'ਸੁਧਿ_vs_ਸੁਧੁ',
     'ਸੁਧਿ (sihari) = awareness/realization/consciousness; ਸੁਧੁ (aungkar) = corrected/purified',
     'ਸੁਧਿ / ਸੁਧੁ',
     'sihari = state of awareness; aungkar = adjective "corrected"', 'grammar_pdf_p59'),

    ('word_form', 'ਮੂਰਤਿ_vs_ਮੂਰਤੁ',
     'ਮੂਰਤਿ (original sihari) = idol/form/image (murti); ਮੂਰਤੁ (aungkar) = auspicious moment/muhurat',
     'ਮੂਰਤਿ / ਮੂਰਤੁ',
     'Akaal Murat = ਅਕਾਲ ਮੂਰਤਿ = Beyond-Time Form (sihari = original)', 'grammar_pdf_p59'),

    # Section 15.2 (pages 59-60) — Feminine Sihari (ਇਸਤਰੀ ਲਿੰਗ ਵਾਚਕ ਸਿਹਾਰੀ)
    ('gender', 'feminine_sihari_ni_ending',
     'sihari marks feminine gender on nouns ending in -ਣਿ or -ਨਿ; list of common feminine nouns with inherent sihari',
     'ਭੰਡਾਰਣਿ, ਸੋਹਾਗਣਿ, ਪਰਦੇਸਣਿ, ਕਲਾਲਣਿ, ਮਾਲਿਣਿ, ਭੈਰਾਗਣਿ, ਸਾਹਣਿ, ਸਾਪਣਿ, ਸਰਪਣਿ, ਜਲਣਿ, ਦਾਮਣਿ, ਵਰਤਣਿ, ਪੜੋਸਣਿ, ਸਉਕਣਿ, ਗੀਹਣਿ, ਘਾਣਿ, ਕਾਣਿ, ਪਾਣਿ',
     'sihari on -ਣਿ/-ਨਿ ending = feminine noun', 'grammar_pdf_p59'),

    ('word_form', 'ਕਾਮਣਿ_vs_ਕਾਮਣ',
     'ਕਾਮਣਿ (sihari) = woman/wife (feminine noun); ਕਾਮਣ (no sihari) = magic charm/spell (different meaning)',
     'ਕਾਮਣਿ / ਕਾਮਣ',
     'ਗੁਣਿ ਕਾਮਣ ਕਾਮਣਿ ਕਰੈ ਤਉ ਪਿਆਰੇ ਕਉ ਪਾਵੈ (Tilang M:1) — both in one line: charm and woman', 'grammar_pdf_p60'),

    ('word_form', 'ਤਰੁਣਿ_vs_ਤਰਣੁ',
     'ਤਰੁਣਿ (sihari, feminine) = young woman; ਤਰਣੁ (aungkar) = to swim/cross over — common misreading in Gurbani',
     'ਤਰੁਣਿ / ਤਰਣੁ',
     'ਜੋਸੀ ਤਰੁਣਿ ਭਤਾਰ ਉੜਜੀ (Asa M:5) = the young woman whose husband has left | ਤਰਣੁ ਦੁਹੇਲਾ ਭਇਆ ਖਿਨ ਮਹਿ (Asa M:5) = crossing over became difficult in a moment — NOT a woman', 'grammar_pdf_p60'),
]

cur.executemany('''
    INSERT INTO grammar_rules (category, pattern, meaning, example_word, example_meaning, source)
    VALUES (?, ?, ?, ?, ?, ?)
''', rules)

conn.commit()
print(f'Added {len(rules)} rules')
cur.execute('SELECT COUNT(*) FROM grammar_rules')
print(f'Total grammar_rules: {cur.fetchone()[0]}')
