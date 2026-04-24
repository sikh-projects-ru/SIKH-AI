import sqlite3
conn = sqlite3.connect('ksd_knowledge.db')
cur = conn.cursor()

rules = [
    # Pages 71-72 — ਆਪਿ continuation + Nirgun/Sargun
    ('word_form', 'ਆਪਿ_vs_ਆਪੁ',
     'ਆਪਿ (sihari) = Creator as past agent / "the Being" whose self IS Creator; ਆਪੁ (aungkar) = the individual self/ego "himself/herself"',
     'ਆਪਿ / ਆਪੁ',
     'ਆਪਿ ਕਰੇ ਕਿਸੁ ਆਖੀਐ (Creator acts) | ਆਪੁ ਗਵਾਇ ਸੇਵਾ ਕਰੇ (efface your ego-self)', 'grammar_pdf_p71'),

    ('principle', 'nirgun_sargun_distinction',
     'Nirgun (ਨਿਰਗੁਣ) = Creator without attributes, beyond creation; Sargun (ਸਰਗੁਣ) = Creator manifest in creation with attributes — same One, two aspects; ਆਪਿ used for both because the Being is Creator',
     'ਨਿਰਗੁਣ / ਸਰਗੁਣ',
     'ਆਪੇ ਨਿਰਗੁਣੁ ਆਪੇ ਸਰਗੁਣੁ (M:5) — Creator is both; theological foundation for ਆਪਿ covering both states', 'grammar_pdf_p72'),

    ('word_form', 'ਖੁਦਿ_creator_agent',
     'ਖੁਦਿ (sihari) = Arabic/Persian "Khud" (self/God) as past agent marker — equivalent to ਆਪਿ; Creator performed the action',
     'ਖੁਦਿ',
     'ਖੁਦਿ ਕੁਦਰਤਿ ਕੀਮਤਿ ਕਰੇ (Creator himself sets the value of His creation)', 'grammar_pdf_p72'),

    # Page 73 — Section 19.0: Sihari replacing Bihari (poetic meter)
    ('vowel_mark', 'sihari_replacing_bihari_meter',
     'Section 19.0: sihari replaces bihari (ੀ) for poetic meter needs — meaning unchanged, both forms valid; Guru Granth uses shorter sihari to fit poetic rhythm (ਕਾਵਿ-ਰਚਨਾ)',
     'ਚੇਰਿ=ਚੇਰੀ, ਪੰਖਿ=ਪੰਖੀ, ਦਰਬਾਰਿ=ਦਰਬਾਰੀ, ਸੁਆਮਿ=ਸੁਆਮੀ, ਪ੍ਰੀਤਿ=ਪ੍ਰੀਤੀ, ਰਜਾਇ=ਰਜ਼ਾਈ',
     'ਚੇਰਿ ਕਹਾਵਉ ਸੁਆਮਿ ਤੁਮਾਰੀ (Suhi M:4) = I am called servant of my Master | ਪੰਖਿ ਨ ਚੁਕਾ (bird — meter form)', 'grammar_pdf_p73'),

    ('word_form', 'ਦਰਬਾਰਿ_bihari_meter',
     'ਦਰਬਾਰਿ (sihari) = ਦਰਬਾਰੀ "of the Court / courtly" — bihari replaced by sihari for meter; NOT the locative "in the Court" (which uses different grammar)',
     'ਦਰਬਾਰਿ / ਦਰਬਾਰੀ',
     'ਦਰਬਾਰਿ ਸੋਭਾ ਪਾਵਹਿ (obtain glory at/of the Court) — sihari=bihari meter form', 'grammar_pdf_p73'),

    # Page 74 — 19.0 continued: other vowel substitutions and short forms
    ('vowel_mark', 'sihari_replacing_lava_meter',
     'sihari also replaces ਲਾਵਾਂ (other vowel markers) for poetic meter: ਨੇਰਿ=ਨੇੜੇ (near), ਚਾਰਿ=ਚਾਰੇ (all four), ਤਲਿ=ਤਲੇ (below/under)',
     'ਨੇਰਿ / ਚਾਰਿ / ਤਲਿ',
     'ਸਦਾ ਨੇਰਿ ਦੂਰਿ ਨ ਜਾਹੁ (always near — ਨੇਰਿ=ਨੇੜੇ) | ਚਾਰਿ ਪਦਾਰਥ (the four gifts — ਚਾਰਿ=ਚਾਰੇ)', 'grammar_pdf_p74'),

    ('word_form', 'ਧੰਨਿ_short_form',
     'ਧੰਨਿ = short poetic form of ਧੰਨਾ/ਧੰਨੁ "blessed/praise be"; sihari is meter contraction — same meaning as full form',
     'ਧੰਨਿ',
     'ਧੰਨਿ ਸੁ ਦੇਸੁ ਜਹਾ ਤੂੰ ਵਸਿਆ (Tukhari M:5) = blessed is that land where You dwell', 'grammar_pdf_p74'),

    # Page 75 — Section 20.0: Bihari (ਬਿਹਾਰੀ); 20.1 Plural preposition
    ('vowel_mark', 'bihari_plural_preposition',
     'Section 20.1: bihari (ੀ) on noun = plural preposition form — "with the [plural noun]s / by the [plural noun]s / to the [plural noun]s"; equivalent to ਾਂ ਨੇ/ਨੂੰ/ਨਾਲ',
     'ਸਿਖੀ=ਸਿੱਖਾਂ ਨੇ, ਅਖੀ=ਅੱਖਾਂ ਨੂੰ, ਉਪਾਵੀ=ਉਪਾਵਾਂ ਨਾਲ, ਅਖਰੀ=ਅੱਖਰਾਂ ਨਾਲ',
     'ਸਿਖੀ ਸਿਖਿਆ ਗੁਰ ਵੀਚਾਰਿ (Jap Ji) = the Sikhs, through Guru\'s teaching, contemplate | ਅਖੀ ਬਾਝਹੁ ਵੇਖਣਾ (without eyes seeing)', 'grammar_pdf_p75'),

    ('word_form', 'ਅਖੀ_plural_preposition',
     'ਅਖੀ (bihari) = plural preposition "with/through the eyes" (ਅੱਖਾਂ ਨਾਲ/ਨੂੰ); ਅਖੁ (aungkar) = noun singular "eye"',
     'ਅਖੀ / ਅਖੁ',
     'ਅਖੀ ਬਾਝਹੁ ਵੇਖਣਾ ਵਿਣੁ ਕੰਨਾ ਸੁਣਣਾ (Anand Sahib) = to see without eyes, hear without ears', 'grammar_pdf_p75'),

    # Page 76 — 20.2 Bihari = 1st person verb; 20.3 Bihari replacing Sihari
    ('tense', 'bihari_first_person_verb',
     'Section 20.2: bihari (ੀ) on verb = 1st person singular "I [do/will do]" (ਮੈਂ ਕਰਾਂ); present/future tense self-reference',
     'ਸੋਚੀ=ਮੈਂ ਸੋਚਾਂ, ਕਰੀ=ਮੈਂ ਕਰਾਂ, ਦੇਖੀ=ਮੈਂ ਦੇਖਾਂ, ਵਣਜੀ=ਮੈਂ ਵਣਜ ਕਰਾਂ',
     'ਸੋਚੀ ਸੋਚਿ ਨ ਹੋਵਈ (Jap Ji) = even if I think and think [it cannot be known] | ਕਿਆ ਕਰੀ ਕਿਛੁ ਕਹਣੁ ਨ ਜਾਇ (what shall I do/say)', 'grammar_pdf_p76'),

    ('vowel_mark', 'bihari_replacing_sihari',
     'Section 20.3: bihari (ੀ) replaces sihari for poetic meter — same grammatical meaning; ਲਹਨੀ=ਲਹਨਿ (3rd plural "they receive"), ਜਾਣੀ=ਜਾਣਿ (conjunctive/preposition)',
     'ਲਹਨੀ=ਲਹਨਿ, ਜਾਣੀ=ਜਾਣਿ',
     'ਲਹਨੀ ਦਾਤਿ ਸੰਤੋਖੁ (they receive the gift of contentment) — bihari=sihari meter | ਜਾਣੀ ਜਾਣੁ ਨ ਦੇਵਉ (having known, I will not give up)', 'grammar_pdf_p76'),

    ('vowel_mark', 'bihari_as_preposition',
     'bihari (ੀ) on noun = instrumental preposition "by means of / through / with" (ਨਾਲ); ਨਦਰੀ=ਨਦਰ ਨਾਲ, ਵਿਜੋਗੀ=ਵਿਜੋਗ ਨਾਲ',
     'ਨਦਰੀ / ਵਿਜੋਗੀ',
     'ਨਦਰੀ ਨਦਰਿ ਨਿਹਾਲ (Jap Ji) = by the Glance of Grace, blissful | ਵਿਜੋਗੀ ਦੁਖੁ ਪਾਇਆ (by separation, pain is found)', 'grammar_pdf_p76'),

    # Page 77 — Section 21.0 Aungkar = singular; Section 22.0 Past tense -ਨੁ
    ('vowel_mark', 'aungkar_singular_marker',
     'Section 21.0: aungkar (ੁ) marks singular on BOTH noun and its adjective — both take aungkar together; this is the fundamental singular agreement rule',
     'ਸੱਚਾ ਸਾਹਿਬੁ, ਮਹਾਨੁ ਕਰਤਾਰੁ',
     'ਸੱਚਾ ਸਾਹਿਬੁ ਸਾਚੁ ਨਾਇ (Jap Ji) = True is the Master, True the Name — both noun+adjective take aungkar', 'grammar_pdf_p77'),

    ('tense', 'past_tense_nu_ending',
     'Section 22.0: past tense singular verb ending -ਨੁ (ਨ + aungkar) = "he/she/Creator did [action to plural objects]"; subject is singular, objects are plural',
     'ਬਖਸਿਅਨੁ, ਕੀਤਨੁ, ਦਿੱਤਨੁ',
     'ਬਖਸਿਅਨੁ ਨਾਮ ਨਿਧਾਨੁ (M:5) = He (singular) bestowed the treasure of Naam [plural blessings] | -ਨੁ marks singular agent doing plural action', 'grammar_pdf_p77'),

    # Page 78 — -ਨੁ vs -ਨਿ; Section 23.0 Imperative aungkar
    ('tense', 'past_tense_nu_vs_ni',
     'past tense contrast: -ਨੁ (aungkar) = singular agent "he examined/did"; -ਨਿ (sihari) = plural "they examined/did"',
     'ਪਰਖਿਅਨੁ / ਪਰਖੀਅਨਿ',
     'ਪਰਖਿਅਨੁ (he alone examined) vs ਪਰਖੀਅਨਿ (they examined) — aungkar=singular, sihari=plural agent', 'grammar_pdf_p78'),

    ('word_class', 'imperative_aungkar',
     'Section 23.0: aungkar (ੁ) on verb = imperative "You [singular, respectful] do this!" — formal command directed to one person; differs from sihari imperative (less formal)',
     'ਦੇਹੁ, ਚਲੁ, ਪਰੁ, ਸੁਣਹੁ, ਮਿਲਹੁ',
     'ਦੇਹੁ ਦਰਸਨੁ ਹੋਇ ਦਇਆਲੁ (M:5) = Give [Your] darshan, be merciful | ਸੁਣਹੁ ਬਿਨੰਤੀ ਮੇਰੀ ਹਰਿ ਜੀਉ (hear my prayer)', 'grammar_pdf_p78'),

    # Page 79 — Section 24.0 Original Aungkar words
    ('vowel_mark', 'original_aungkar_words',
     'Section 24.0: some words carry original/inherited aungkar from Sanskrit/Arabic — permanent, not grammatical number marker; must be recognized to avoid misreading as masculine singular',
     'ਕਿਤੁ, ਬਿਨੁ, ਬਹੁਤੁ, ਬਿੰਦੁ, ਸੁਤੁ, ਜੰਤੁ',
     'ਕਿਤੁ ਦਰਵਾਜੈ ਰਖਾ (Anand) = at which door shall I keep [watch]? — ਕਿਤੁ is original aungkar, not singular marker', 'grammar_pdf_p79'),

    ('gender', 'feminine_original_aungkar',
     'some feminine nouns carry original aungkar — they are feminine despite the aungkar which normally marks masculine; reader must know these by recognition',
     'ਧਾਤੁ=substance/metal (f), ਭਿਖੁ=begging (f), ਰਤੁ=blood (f), ਮਲੁ=filth (f), ਮਸੁ=ink (f)',
     'ਰਤੁ ਪੀਣੇ ਮਾਣਸ ਤੇ ਕੁੰਗੂ (Asa M:1) = those who drink blood [feminine noun ਰਤੁ] | ਮਸੁ ਕਰਿ ਮੇਘ ਵਰਸਾਵਉ (if I make ink of clouds)', 'grammar_pdf_p79'),

    ('word_form', 'ਬਿਨੁ_original_aungkar',
     'ਬਿਨੁ = "without" — conjunction/preposition with original aungkar; NOT singular marker; always written with aungkar on ਨ',
     'ਬਿਨੁ',
     'ਬਿਨੁ ਸਤਿਗੁਰ ਕਿਨੈ ਨ ਪਾਇਓ (without the Satguru none has found) — original aungkar, not grammatical', 'grammar_pdf_p79'),

    # Page 80 — Section 25.0: ਹੁ (single) vs ਹਹੁ (double)
    ('vowel_mark', 'hu_subject_case',
     'Section 25.0: single ਹੁ (ਹ + aungkar, no nasal) after word = nominative/subject case marker "the Creator/subject"; marks the main agent',
     'ਸਤਿਗੁਰਹੁ, ਪ੍ਰਭਹੁ',
     'ਮੇਰੇ ਸਤਿਗੁਰਹੁ ਕਿਰਪਾ ਕਰੀ (M:4) = My Satguru showed grace — ਹੁ marks subject/nominative', 'grammar_pdf_p80'),

    ('case', 'hahu_ablative_case',
     'double ਹਹੁ (two ਹ with aungkar) = ablative case "from / out of / away from"; distinguishes direction away from subject',
     'ਰਾਹੁ vs ਰਾਹਹੁ, ਕਹੁ vs ਕਹਹੁ',
     'ਰਾਹੁ (the path) vs ਰਾਹਹੁ (from the path) | ਕਹੁ (say — imperative) vs ਕਹਹੁ (from saying / because of saying) — single vs double ਹ distinguishes case', 'grammar_pdf_p80'),
]

cur.executemany('''
    INSERT INTO grammar_rules (category, pattern, meaning, example_word, example_meaning, source)
    VALUES (?, ?, ?, ?, ?, ?)
''', rules)

conn.commit()
print(f'Added {len(rules)} rules')
cur.execute('SELECT COUNT(*) FROM grammar_rules')
print(f'Total grammar_rules: {cur.fetchone()[0]}')
