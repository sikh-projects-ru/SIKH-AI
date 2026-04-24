import sqlite3
conn = sqlite3.connect('ksd_knowledge.db')
cur = conn.cursor()

rules = [
    # Page 41 — conjunctive participle: ਜਰਿ vs ਜਰ (critical parsing example)
    ('word_form', 'ਜਰਿ_vs_ਜਰ',
     'ਜਰਿ (sihari) = conjunctive participle "having endured/burned away"; ਜਰ (no sihari) = noun "sword/gold" — opposite meanings',
     'ਜਰਿ / ਜਰ',
     'ਅਸ ਜਰਿ ਪਰ ਜਰਿ ਜਰਿ ਜਬ ਰਹੈ ਤਬ ਜਾਇ ਜੋਤਿ ਉਜਾਰਉ ਲਹੈ — burn away own and others desires (not "sword")', 'grammar_pdf_p41'),

    # Section 11.0 (pages 43-44) — Participle (ਕਾਰਦੰਤਕ) with auxiliary verbs
    ('word_class', 'participle_with_auxiliary_verb',
     'participle (ਕਾਰਦੰਤਕ) combined with auxiliary verbs (ਆਣਾ, ਜਾਣਾ, ਬਹਿਣਾ, ਰਹਿਣਾ, ਸਕਣਾ) forming compound verbs: sihari on participle last consonant',
     'ਬਨਿ, ਦੀਸਿ, ਜਿਣਿ, ਹਾਰਿ, ਛਡਿ, ਆਣਿ, ਭੇਜਿ, ਧੋਇ, ਲਿਖਿ, ਪੀੜਿ',
     'ਸੇਵਕ ਕਉ ਸੇਵਾ ਬਨਿ ਆਈ (Sukhmani) | ਦੇ ਸਾਬੁਣੁ ਲਈਐ ਓਹੁ ਧੋਇ (Jap Ji)', 'grammar_pdf_p43'),

    ('word_class', 'compound_verb_subject_sihari',
     'in compound verbs: sihari on subject end means "this/for/the" (preposition role); differs from noun+sihari preposition case because here the subject IS the main verb',
     'ਆਖਣਿ, ਪੜਣਿ',
     'ਜੇ ਕੋ ਖਾਇਕੁ ਆਖਣਿ ਪਾਇ (Jap Ji) | ਲਗਾ ਪੜਣਿ ਸਲੋਕੁ (Asa di Var)', 'grammar_pdf_p44'),

    # Section 12.0 (pages 45-47) — Imperative Mood (ਅਨੁਮਤਯਾਰਥ ਲਕਾਰ)
    ('word_class', 'imperative_mood_sihari',
     'imperative mood (ਅਨੁਮਤਯਾਰਥ ਲਕਾਰ): command "you do this" — sihari sometimes appears on verb last consonant',
     'ਜਪਿ, ਸਾਲਾਹਿ, ਸਿਮਰਿ, ਆਹਿ, ਲੇਹਿ, ਦੇਹਿ, ਸੁਣਿ, ਕਰਿ, ਧਰਿ',
     'ਏਕੋ ਜਪਿ ਏਕੋ ਸਾਲਾਹਿ ਏਕੁ ਸਿਮਰਿ ਏਕੋ ਮਨ ਆਹਿ (Sukhmani)', 'grammar_pdf_p45'),

    ('word_form', 'ਜਪਿ_vs_ਜਪੁ_vs_ਜਪ',
     'ਜਪਿ (sihari) = imperative "You recite!" (command); ਜਪੁ (aungkar) = noun+verb-noun "recitation" (title of Jap Ji + command to activate); ਜਪ (no syllable) = plural',
     'ਜਪਿ / ਜਪੁ / ਜਪ',
     'ਜਪਿ ਜਨ ਸਦਾ ਦਿਨ ਰੈਣੀ (Sukhmani, imperative) | ਜਪੁ after Gur Prasaad = title + imperative | ਅਸੰਖ ਜਪ ਅਸੰਖ ਭਾਉ (Jap Ji, plural)', 'grammar_pdf_p45'),

    ('word_form', 'imperative_examples_list',
     'imperative mood examples: ਸਾਲਾਹਿ=praise (you), ਸਿਮਰਿ=remember (you), ਆਹਿ=desire (you), ਲੇਹਿ=take (you), ਦੇਹਿ=give (you), ਸੁਣਿ=listen (you), ਕਰਿ=do (you), ਧਰਿ=hold/place (you)',
     'ਸਾਲਾਹਿ / ਸਿਮਰਿ / ਆਹਿ / ਲੇਹਿ / ਦੇਹਿ / ਸੁਣਿ / ਕਰਿ / ਧਰਿ',
     'ਮਨ ਮੇਰੇ ਤਿਨ ਕੀ ਓਟ ਲੇਹਿ, ਮਨੁ ਤਨੁ ਅਪਨਾ ਤਿਨ ਜਨ ਦੇਹਿ (Sukhmani)', 'grammar_pdf_p47'),

    # Section 13.0 (pages 47-50) — Subordinate Clause (ਅਧੀਨ ਵਾਕੰਸ)
    ('word_class', 'subordinate_clause_structure',
     'subordinate clause (ਅਧੀਨ ਵਾਕੰਸ): two words — (1) noun with sihari on last consonant + (2) verb ending with dulava; means "by [noun-action], [main result]"',
     'ਨਾਮਿ ਸਲਾਹਿਐ, ਸਤਿਗੁਰਿ ਮਿਲਿਐ, ਧਾਨਿ ਖਾਧੈ, ਪਾਰਸਿ ਪਰਸਿਐ',
     'ਨਾਨਕ ਨਾਮਿ ਸਲਾਹਿਐ ਮਨੁ ਤਨੁ ਸੀਤਲੁ ਹੋਇ (M:5) | ਸਤਿਗੁਰਿ ਮਿਲਿਐ ਸਚੁ ਪਾਇਆ (Asa di Var)', 'grammar_pdf_p48'),

    ('principle', 'subordinate_clause_noun_only',
     'sihari in subordinate clause appears on NOUN only, not on pronoun; when subject is a pronoun, sihari is absent',
     '',
     'ਸਤਿਗੁਰ ਵਿਟਹੁ ਵਾਰਿਆ ਜਿਤੁ ਮਿਲਿਐ ਖਸਮੁ ਸਮਾਲਿਆ (Asa di Var) — ਜਿਤੁ is pronoun, no sihari', 'grammar_pdf_p49'),

    ('word_form', 'ਜੋਬਨਿ_subordinate_clause',
     'ਜੋਬਨਿ (sihari) = subordinate clause noun "by/through [act of] youth [squandered]"; NOT "old age comes, youth is lost" — sihari marks it as cause, not sequence',
     'ਜੋਬਨਿ',
     'ਜਰੁ ਆਈ ਜੋਬਨਿ ਹਾਰਿਆ (Asa di Var) = old age arrived by [the body] losing youth through evil desires — subordinate clause, not temporal sequence', 'grammar_pdf_p49'),

    ('word_form', 'subordinate_clause_examples',
     'subordinate clause examples: ਨਾਮਿ ਸਲਾਹਿਐ=by praising the Naam, ਧਾਨਿ ਖਾਧੈ=by eating this grain, ਸਤਿਗੁਰਿ ਮਿਲਿਐ=by meeting the Satguru, ਪਿੰਡਿ ਮੁਐ=by dying of body, ਮੁਖਿ ਜੋਰਿਐ=by joining mouths',
     'ਨਾਮਿ / ਧਾਨਿ / ਸਤਿਗੁਰਿ / ਪਾਰਸਿ / ਲੋਕਿ / ਜੋਬਨਿ / ਪਿੰਡਿ / ਮੁਖਿ',
     'ਪਿੰਡਿ ਮੁਐ ਜੀਉ ਕਿਹ ਘਰਿ ਜਾਤਾ (Gauri Kabir) = by the body dying, where does the soul go?', 'grammar_pdf_p49'),

    # Section 14.0 / 14.1 (page 50) — Present Imperfect, Third Person Plural
    ('tense', 'present_imperfect_3rd_plural_ni',
     'present imperfect verb (ਸਮਾਨ ਵਰਤਮਾਨ) in 3rd person plural (ਬਹੁਵਚਨ ਅਨਯ ਪੁਰਖ): verb ends with ਨਿ (ਨ + sihari) = "they are [doing/singing/etc.]"',
     'ਗਾਵਨਿ, ਜਾਣਨਿ, ਵਾਇਨਿ, ਨਚਨਿ, ਹਲਾਇਨਿ, ਫੇਰਨਿ, ਚੁਗਨਿ, ਵਸਨਿ, ਛੋਡਨਿ',
     'ਗਾਵਨਿ ਤੁਧਨੋ ਚਿਤ੍ਰ ਗੁਪਤੁ ਲਿਖਿ ਜਾਣਨਿ (Sodar Asa M:1) = they sing to You, Chitr Gupt who writes knows', 'grammar_pdf_p50'),
]

cur.executemany('''
    INSERT INTO grammar_rules (category, pattern, meaning, example_word, example_meaning, source)
    VALUES (?, ?, ?, ?, ?, ?)
''', rules)

conn.commit()
print(f'Added {len(rules)} rules')
cur.execute('SELECT COUNT(*) FROM grammar_rules')
print(f'Total grammar_rules: {cur.fetchone()[0]}')
