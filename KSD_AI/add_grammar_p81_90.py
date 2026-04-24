import sqlite3
conn = sqlite3.connect('ksd_knowledge.db')
cur = conn.cursor()

rules = [
    # Page 81 — Section 26.0 Dulangkar (ਦੁਲੈਂਕੜ); 26.1 Noun + Preposition
    ('vowel_mark', 'dulangkar_noun_before_preposition',
     'Section 26.0-26.1: dulangkar (ੁ, aungkar) on noun when followed by a preposition word; marks noun as object/base for preposition',
     'ਵਸਤੁ, ਜਿੰਦੁ, ਖਾਕੁ, ਸਸੁ, ਪੀਯੁ',
     'ਵਸਤੁ ਅੰਦਰਿ ਵਸਤੁ ਸਮਾਵੈ (Asa di Var) | ਸਾਹੇ ਲਿਖੇ ਨ ਚਲਨੀ ਜਿੰਦੁ ਕੂੰ ਸਮਝਾਇ (Salok Farid) | ਸਸੁ ਤੇ ਪਿਰਿ ਕੀਨੀ ਵਾਖਿ (Asa M:5)', 'grammar_pdf_p81'),

    # Page 82 — 26.2 Dulangkar as preposition; 26.3 Dulangkar replacing Hora
    ('vowel_mark', 'dulangkar_as_preposition',
     'Section 26.2: dulangkar used as preposition meaning "in/within" — word with aungkar itself functions as locative (ਵਿਚ)',
     'ਖੇਹੁ=ਖੇਹ ਵਿਚ',
     'ਖੇਹੁ ਖੇਹ ਰਲਾਈਏ (Siri Ragu M:1) = merged into dust [ਖੇਹੁ = in dust]', 'grammar_pdf_p82'),

    ('vowel_mark', 'dulangkar_replacing_hora',
     'Section 26.3: dulangkar replaces hora (ੋ) for poetic meter — meaning identical to hora form; ਜਿਦੂ=ਜਿਦੋਂ (from which), ਤਿਦੂ=ਤਿਦੋਂ (from then), ਕੂ=ਕੋ',
     'ਜਿਦੂ=ਜਿਦੋਂ, ਤਿਦੂ=ਤਿਦੋਂ, ਕੂ=ਕੋ, ਅਸਲੂ=ਅਸਲੋਂ',
     'ਜਿਦੂ ਕਿਛੁ ਗੁਝਾ ਨ ਹੋਇ (Var Gauri M:4) = from which nothing is hidden | ਮਾਸ ਨ ਤਿਦੂ ਖਾਹਿ (Salok Farid) | ਦੁਖ ਮੁਝ ਕੂ (to me)', 'grammar_pdf_p82'),

    # Pages 82-83 — Section 27.0 Laa'n replacing Sihari
    ('vowel_mark', 'laan_replacing_sihari',
     'Section 27.0: laa\'n (ਾ, lavan) replaces sihari for poetic meter — same grammatical meaning; forms are interchangeable',
     'ਪੜੇ=ਪੜਿ, ਮੁਹੇ=ਮੁਹਿ, ਕੁੜੇ=ਕੁੜਿ, ਦਰੇ=ਦਰਿ, ਸੰਸਾਰੇ=ਸੰਸਾਰਿ, ਸੰਗੇ=ਸੰਗਿ, ਸਾਥੇ=ਸਾਥਿ, ਧੁਰੇ=ਧੁਰਿ, ਉਪਰੇ=ਉਪਰਿ, ਅੰਤੇ=ਅੰਤਿ',
     'ਕਬਿਤ ਪੜੇ ਪੜਿ ਕਬਿਤਾ ਮੁਏ (Sorath Kabir) — same line uses both forms | ਸੰਤੋਖੁ ਭਇਆ ਸੰਸਾਰੇ (=ਸੰਸਾਰਿ, Sorath M:5) | ਨਾਨਕ ਪ੍ਰਭੁ ਮੇਰੈ ਸਾਥੇ (=ਸਾਥਿ, Sorath M:5)', 'grammar_pdf_p82'),

    ('word_form', 'laan_sihari_same_line',
     'same verse can use both laa\'n and sihari forms of same word — confirms they are stylistic variants, not grammatically distinct',
     'ਦਰੇ=ਦਰਿ',
     'ਹਰਿ ਦਰੇ ਹਰਿ ਦਰਿ ਸੋਹਨਿ ਤੇਰੇ ਭਗਤ ਪਿਆਰੇ ਰਾਮ (Asa M:5) — ਦਰੇ and ਦਰਿ in same tuk', 'grammar_pdf_p83'),

    # Pages 83-86 — Section 28.0 Dulaava (ਦੁਲਾਈਆਂ)
    ('vowel_mark', 'dulaava_place_preposition',
     'Section 28.0-28.1: dulaava (ੈ) marks locative/place preposition "in/at/on/with" — used with place nouns, nouns of location, and relational nouns',
     'ਦੂਜੈ=ਦੂਜੇ ਨਾਲ, ਰਿਦੈ=ਰਿਦੇ ਵਿਚ, ਮੰਦੈ=ਮੰਦ ਵਿਚ, ਰੈਨਡੀਏ=ਰੈਨ ਵਿਚ, ਚਉਕੈ, ਮਥੈ, ਪੇੜੈ, ਅਗੈ, ਤਲੈ, ਪਿਛੈ',
     'ਸਭੋ ਸੁਤਕੁ ਭਰਮੁ ਹੈ ਦੂਜੈ ਲਗੈ ਜਾਇ (Asa di Var) | ਸਚੁ ਤਾ ਪਰੁ ਜਾਣੀਐ ਜਾ ਰਿਦੈ ਸਚਾ ਹੋਇ (Asa di Var)', 'grammar_pdf_p83'),

    ('vowel_mark', 'dulaava_noun_preposition',
     'Section 28.2: dulaava (ੈ) on noun = locative "in/to/of the [noun]" where a preposition word follows; parallels sihari but for different case contexts',
     'ਘਰੈ, ਨਾਵੈ',
     'ਘਰੈ ਅੰਦਰਿ ਸਭੁ ਵਥੁ ਹੈ (Asa M:3) = within the house everything exists | ਸਭ ਨਾਵੈ ਨੋ ਲੋਚਦੀ (Asa M:3) = all long for the Name', 'grammar_pdf_p84'),

    ('vowel_mark', 'dulaava_adjective_agreement',
     'Section 28.3: when noun carries sihari or dulaava, its adjective must also take dulaava (ੈ) — agreement in oblique case; dulaava replaces laa\'n on adjective',
     'ਅੰਧੈ, ਪੂਰੈ, ਭੀੜੈ, ਭੀਹਾਵਲੈ, ਮੇਰੈ, ਤੇਰੈ, ਪਰਾਇਓ, ਕਚੈ, ਪਹਿਲੈ',
     'ਗੁਰਿ ਪੂਰੈ ਮਿਹਰਵਾਨਿ (M:4) = by the Perfect Guru, merciful — ਗੁਰਿ (sihari) → ਪੂਰੈ (dulaava) | ਮੁਰਖਿ ਅੰਧੈ ਪਤਿ ਗਵਾਈ (Asa di Var)', 'grammar_pdf_p84'),

    ('principle', 'terai_mani_bhavde_correct_reading',
     'ਭਗਤ ਤੇਰੈ ਮਨਿ ਭਾਵਦੇ (Asa di Var) = "devotees are pleasing to Your mind" NOT "devotees are pleasing Your mind"; ਤੇਰੈ = locative "to Your [mind]", ਮਨਿ = dative; subject is ਭਗਤ',
     'ਤੇਰੈ ਮਨਿ',
     'ਭਗਤ ਤੇਰੈ ਮਨਿ ਭਾਵਦੇ — devotees are beloved in Your heart (not: devotees love Your mind)', 'grammar_pdf_p85'),

    ('vowel_mark', 'dulaava_verb_causal',
     'Section 28.4: dulaava on verb-noun = causal "by means of [verb action]"; ਸੁਣਿਓ = ਸੁਣਨ ਕਰਕੇ "by hearing" — same pattern as sihari on verb (rule 14 cross-reference)',
     'ਸੁਣਿਓ=ਸੁਣਨ ਕਰਕੇ',
     'dulaava on verb-noun marks the action as the cause/instrument of the main clause result', 'grammar_pdf_p86'),

    # Page 86 — Section 29.0 Kenora (ਕਨੌੜਾ)
    ('case', 'kenora_ablative_preposition',
     'Section 29.0: kenora (ੈਂ / ਹੈਂ) used as ablative preposition "from / away from / out of" on locative nouns; ਆਪੈਂ=ਆਪ ਥੋਂ (from oneself), ਮੁਹੈਂ=ਮੁੰਹ ਤੋਂ (from the mouth)',
     'ਆਪੈਂ=ਆਪ ਥੋਂ, ਮੁਹੈਂ=ਮੁੰਹ ਤੋਂ, ਜੀਭੌਂ=ਜੀਭ ਤੋਂ',
     'ਨਾਨਕ ਜੇ ਕੋ ਆਪੈਂ ਜਾਣੈ ਅਗੈ ਗਇਆ ਨ ਸੋਹੈ (Jap Ji) = one who thinks himself above [from oneself outward] will not look good ahead | ਮੁਹੈਂ ਕਿ ਬੋਲਣੁ ਬੋਲੀਐ (Jap Ji)', 'grammar_pdf_p86'),

    # Page 88 — Module 5, Section 30.1 Original Sihari — extended word list
    ('vowel_mark', 'original_sihari_extended_list',
     'Section 30.1: extended list of original/inherited sihari words — sihari is permanent, comes from source language (Sanskrit/Arabic); cannot be removed or replaced by aungkar',
     'ਹਰਿ, ਨਾਰਿ, ਰਾਸਿ, ਜੁਗਤਿ, ਧੁਨਿ, ਭੂਮਿ, ਧਰਤਿ, ਪ੍ਰੀਤਿ, ਦ੍ਰਿਸਟਿ, ਸਿਮ੍ਰਿਤਿ, ਨਾਭਿ, ਸ਼ਕਤਿ, ਰੈਣਿ, ਰਾਤਿ, ਰੁਤਿ, ਸ੍ਰਿਸਟਿ, ਕੀਰਤਿ, ਰਵਿ, ਅਗਨਿ, ਸਮਾਧਿ, ਮਰਤਿ, ਜਤਿ, ਜੋਤਿ, ਰੀਤਿ, ਅਤਿ, ਸਰਣਿ, ਨਿਧਿ, ਰਿਧਿ, ਬਿਧਿ, ਜੋਨਿ, ਸੁਰਤਿ, ਧੁਰਿ, ਮੁਨਿ, ਤ੍ਰਿਪਤਿ, ਉਪਾਧਿ, ਚਿੰਤਾਮਣਿ',
     'ਰਿਧਿ ਬੁਧਿ ਸਿਧਿ ਗਿਆਨੁ ਸਦਾ ਸੁਖੁ ਹੋਇ (M:1 Var Malar) — all three have original sihari', 'grammar_pdf_p88'),

    ('word_form', 'bhagti_vs_bhagtu',
     'ਭਗਤਿ (original sihari) = devotion/bhakti (abstract noun); ਭਗਤੁ (aungkar) = devotee singular (person); ਭਗਤ (mukta) = devotees plural',
     'ਭਗਤਿ / ਭਗਤੁ / ਭਗਤ',
     'ਤੇਰੀ ਭਗਤਿ ਤੇਰੀ ਭਗਤਿ ਭੰਡਾਰ ਜੀ (Asa M:4) = Your devotion [abstract] | ਤੇਰੇ ਭਗਤ ਸਲਾਹਨਿ ਤੁਧੁ ਜੀ (plural devotees)', 'grammar_pdf_p88'),

    ('word_form', 'mukti_vs_muktu',
     'ਮੁਕਤਿ (original sihari) = liberation/mukti (abstract noun); ਮੁਕਤੁ (aungkar) = liberated one (person); ਮੁਕਤ (mukta) = liberated plural',
     'ਮੁਕਤਿ / ਮੁਕਤੁ / ਮੁਕਤ',
     'ਮੁਕਤਿ ਭੁਗਤਿ ਜੁਗਤਿ ਤੇਰੀ ਸੇਵਾ (Suhi M:5) = liberation, sustenance, unity — through Your service | ਇਹ ਜੀਉ ਸਦਾ ਮੁਕਤੁ ਹੈ (M:3 Var Gujari) = this soul is always liberated (person)', 'grammar_pdf_p88'),

    # Page 89 — original sihari distinctions continued
    ('word_form', 'gati_vs_gatu',
     'ਗਤਿ (original sihari) = spiritual state/condition (abstract); ਗਤੁ (aungkar) = went/departed/passed (verb form meaning "became gone")',
     'ਗਤਿ / ਗਤੁ',
     'ਨਾਮੋ ਗਤਿ ਨਾਮੋ ਪਤਿ ਜਨ ਕੀ (Dhanasari M:5) = Name is the state, Name is the honor | ਅਪਿਓ ਪੀਓ ਗਤੁ ਭੀਓ ਭਰਮਾ (Jetsari M:5) = drank nectar, delusion departed', 'grammar_pdf_p89'),

    ('word_form', 'budhi_vs_budhu',
     'ਬੁਧਿ (original sihari) = intellect/wisdom (abstract noun); ਬੁਧੁ (aungkar) = Buddha/wise person (masculine singular); ਬੁਧ ਸਿਧ (mukta) = plural wise ones',
     'ਬੁਧਿ / ਬੁਧੁ / ਬੁਧ',
     'ਰਿਧਿ ਬੁਧਿ ਸਿਧਿ ਗਿਆਨੁ ਸਦਾ ਸੁਖੁ ਹੋਇ (M:1) = spiritual powers, wisdom, siddhis | ਤੈ ਵਿਚਿ ਸਿਧ ਬੁਧ ਸੁਰ ਨਾਥ (Asa di Var) = plural persons', 'grammar_pdf_p89'),

    ('word_form', 'mati_vs_matu',
     'ਮਤਿ (original sihari) = intellect/understanding (abstract); ਮਤੁ (aungkar) = drunk/intoxicated (adjective/verb form = ਮੱਤਾ ਹੋਇਆ)',
     'ਮਤਿ / ਮਤੁ',
     'ਮਤਿ ਥੋੜੀ ਸੇਵ ਗਵਾਈਐ (Asa di Var) = through little intellect, service is wasted | ਮਨੁ ਮੈ ਮਤੁ ਮੈਗਲ ਮਿਕਦਾਰਾ (Dhanasari M:3) = mind drunk like intoxicated elephant', 'grammar_pdf_p89'),

    # Page 90 — more original sihari distinctions
    ('word_form', 'pati_vs_patu',
     'ਪਤਿ (original sihari) = husband OR honor/dignity (abstract); ਪਤੁ (aungkar/mukta) = leaf/petal (noun) OR Jogi\'s ਪੱਟਾ (begging cloth)',
     'ਪਤਿ / ਪਤੁ / ਪਤ',
     'ਜਹ ਨਿਰਮਲ ਪੁਰਖੁ ਪੁਰਖ-ਪਤਿ ਹੋਤਾ (Sukhmani) = husband/lord | ਮੁਰਖਿ ਅੰਧੈ ਪਤਿ ਗਵਾਈ = honor lost | ਫਲ ਫਿਕੇ ਫੁਲ ਬਕਬਕੇ ਕੰਮਿ ਨ ਆਵਹਿ ਪਤ (Asa di Var) = leaves [no sihari, noun]', 'grammar_pdf_p90'),

    ('word_form', 'miti_vs_mitu',
     'ਮਿਤਿ (original sihari) = measure/extent/limit (abstract); ਮਿਤੁ (aungkar) = friend (masculine noun)',
     'ਮਿਤਿ / ਮਿਤੁ',
     'ਕਰਤੇ ਕੀ ਮਿਤਿ ਕਰਤਾ ਜਾਣੈ (Dakhni Omkar) = Creator alone knows His own extent | ਮਿਟੀ ਪਈ ਅਟੋਲਵੀ ਕੋਇ ਨ ਹੋਸੀ ਮਿਤੁ (Salok Farid) = no one will be a friend', 'grammar_pdf_p90'),

    ('word_form', 'sati_vs_satu',
     'ਸਤਿ (original sihari) = True/Truth as adjective (eternal attribute of Creator); ਸਤੁ (aungkar/mukta) = truth/virtue/reality as noun',
     'ਸਤਿ / ਸਤੁ',
     'ਚਰਨ ਸਤਿ, ਸਤਿ ਪਰਸਨਹਾਰ | ਆਪਿ ਸਤਿ, ਸਤਿ ਸਭ ਧਾਰੀ (Sukhmani) = True the feet, True the worship | ਸਤੁ ਸੰਤੋਖੁ ਪਤੁ ਕਰਿ ਝੋਲੀ (Ramkali M:3) = make truth and contentment your begging-bag [noun]', 'grammar_pdf_p90'),
]

cur.executemany('''
    INSERT INTO grammar_rules (category, pattern, meaning, example_word, example_meaning, source)
    VALUES (?, ?, ?, ?, ?, ?)
''', rules)

conn.commit()
print(f'Added {len(rules)} rules')
cur.execute('SELECT COUNT(*) FROM grammar_rules')
print(f'Total grammar_rules: {cur.fetchone()[0]}')
