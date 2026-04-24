import sqlite3
conn = sqlite3.connect('ksd_knowledge.db')
cur = conn.cursor()

rules = [
    # Page 31 — sihari on verb-adjective lists and reduplicated words
    ('vowel_mark', 'sihari_verb_adjective_list',
     'sihari appears on adverbs/verb-adjectives of manner or repetition',
     'ਫੇਰਿ, ਬਾਹੁਰਿ, ਬਹੁਰਿ, ਫੁਨਿ, ਕਿਟਿ, ਬੀਚਿ, ਮੰਝਾਰਿ, ਨਿਰੰਤਰਿ, ਭਿਨਿ, ਓੜਿ, ਉਪਰਿ, ਹੇਠਿ, ਹਜੂਰਿ, ਤਤਕਾਲਿ, ਆਸਿ ਪਾਸਿ',
     'sihari marks these as verb-adjectives, not nouns', 'grammar_pdf_p31'),

    ('vowel_mark', 'sihari_reduplicated_words',
     'reduplicated verb-adjectives take sihari on both instances',
     'ਝਿਮਿ ਝਿਮਿ, ਠਿਮਿ ਠਿਮਿ, ਮੁਸਿ ਮੁਸਿ, ਮਪਿ ਮਪਿ, ਵਲਿ ਵਲਿ, ਰਸਕਿ ਰਸਕਿ',
     'reduplicated adverbs of manner', 'grammar_pdf_p31'),

    # Section 8.0 (pages 33-36) — Sihari-Preposition: specific word pairs
    ('word_form', 'ਬਾਹਰ_noun_vs_preposition',
     'ਬਾਹਰ as noun: no sihari, uses ਕਾ as possessive marker; ਬਾਹਰਿ with sihari = preposition "outside of"',
     'ਬਾਹਰ / ਬਾਹਰਿ',
     'ਬਾਹਰ ਕਾ ਮਾਸੁ ਮੰਦਾ (noun) vs ਬਾਹਰੁ ਉਦਕਿ ਪਖਾਰੀਐ (noun direction)', 'grammar_pdf_p33'),

    ('word_form', 'ਅੰਤਰਿ_vs_ਅੰਤਰੁ',
     'ਅੰਤਰਿ with sihari = locative preposition "inside/within"; ਅੰਤਰੁ with aungkar = noun "different/separation"',
     'ਅੰਤਰਿ / ਅੰਤਰੁ',
     'ਤਨੁ ਮਨੁ ਦੇਇ ਨ ਅੰਤਰੁ ਰਾਖੈ (Suhi, Ravidas) — ਅੰਤਰੁ = separation', 'grammar_pdf_p34'),

    ('word_form', 'ਓੜਕਿ_vs_ਓੜਕ',
     'ਓੜਕਿ with sihari = adverb "forever/eternally"; ਓੜਕ without syllable = noun "end"',
     'ਓੜਕਿ / ਓੜਕ',
     'ਸੇਵਕ ਕੀ ਓੜਕਿ ਨਿਬਹੀ ਪ੍ਰੀਤਿ (Maru M:5, forever) vs ਓੜਕ ਓੜਕ ਭਾਲਿ ਥਕੇ (Jap Ji, end)', 'grammar_pdf_p35'),

    ('word_form', 'ਅੰਤੁ_noun',
     'ਅੰਤੁ with aungkar = noun "end/limit"; no sihari because it is a noun',
     'ਅੰਤੁ',
     'ਅਗਮ ਅਗੋਚਰਾ ਤੇਰਾ ਅੰਤੁ ਨ ਪਾਇਆ (Anand)', 'grammar_pdf_p35'),

    ('word_form', 'ਸੰਗਿ_vs_ਸੰਗੁ',
     'same word in one verse: ਸੰਗਿ with sihari = preposition "with"; ਸੰਗੁ with aungkar = noun "company/association"',
     'ਸੰਗਿ / ਸੰਗੁ',
     'ਤਿਨ ਸੰਗਿ ਸੰਗੁ ਨ ਕੀਚਈ (M:5, Var Gujari)', 'grammar_pdf_p35'),

    ('word_form', 'ਵਿਚਿ_vs_ਵਿਚੁ',
     'ਵਿਚਿ with sihari = preposition "in/inside"; ਵਿਚੁ with aungkar = noun "middle/intermediary"',
     'ਵਿਚਿ / ਵਿਚੁ',
     'ਹਉਮੈ ਮਨੁ ਅਸਥੁਲੁ ਹੈ ਕਿਉਂ ਕਰਿ ਵਿਚੁ ਦੇ ਜਾਇ (M:3, Var Gujari)', 'grammar_pdf_p36'),

    ('word_form', 'ਫੇਰਿ_vs_ਫੇਰੁ',
     'ਫੇਰਿ with sihari = adverb "again/then"; ਫੇਰੁ with aungkar = noun (name Pheru, or cycle/circle)',
     'ਫੇਰਿ / ਫੇਰੁ',
     'ਫੇਰਿ ਵਸਾਇਆ ਫੇਰੁ-ਆਣਿ ਸਤਿਗੁਰਿ ਖਡੂਰੁ (Var Sata Balvand)', 'grammar_pdf_p36'),

    ('case', 'possessive_drops_aungkar',
     'in possessive case (sambandh karak), aungkar is removed from last consonant whether preposition ਦਾ/ਕਾ appears or not',
     '', '', 'grammar_pdf_p33'),

    # Section 9.0 (pages 37-38) — Conjunctions
    ('word_class', 'conjunction_no_sihari',
     'conjunctions (ਯੋਜਕ) connect two clauses and do NOT take sihari at end — they look like adverbs but are not',
     'ਮਤੁ, ਜਬ, ਤਬ, ਅਬ, ਨਾਤੁਰ, ਸਣੁ, ਵਿਣੁ',
     'conjunctions: no sihari expected', 'grammar_pdf_p37'),

    ('word_form', 'ਮਤੁ_conjunction',
     'ਮਤੁ = conjunction "lest / so that not"; no sihari — not an adverb',
     'ਮਤੁ',
     'ਮਤੁ ਕਿ ਜਾਪੈ ਸਾਹੁ ਆਵੈ ਕਿ ਨ ਆਵੈ ਰਾਮ (Bihagrа M:4)', 'grammar_pdf_p38'),

    ('word_form', 'ਨਾਤੁਰ_conjunction',
     'ਨਾਤੁਰ = conjunction "otherwise/or else" (= ਨਹੀਂ ਤਾਂ, ਵਰਨਾ); no sihari',
     'ਨਾਤੁਰ',
     'ਗੁਰ ਪ੍ਰਸਾਦਿ ਅਕਲਿ ਭਈ ਅਵਰੈ ਨਾਤੁਰ ਭਾ ਬੇਗਾਨਾ (Gauri Bairagan, Kabir)', 'grammar_pdf_p38'),

    ('word_form', 'ਸਣੁ_conjunction',
     'ਸਣੁ = conjunction "along with / and with" (= ਅਤੇ ਨਾਲੋਂ); no sihari',
     'ਸਣੁ',
     'ਚੁੜਾ ਭੰਨੁ ਪਲੰਗ ਸਿਉ ਮੁੰਢੇ ਸਣੁ ਬਾਹੀ ਸਣੁ ਬਾਹਾ (Vadhans M:1)', 'grammar_pdf_p38'),

    ('word_form', 'ਵਿਣੁ_conjunction',
     'ਵਿਣੁ = conjunction "without" connecting two clauses; no sihari',
     'ਵਿਣੁ',
     'ਵਿਣੁ ਪਾਰਸੈ ਪੁਜ ਨ ਹੋਵਈ ਵਿਣੁ ਮਨ ਪਰਚੇ ਅਵਰਾ ਸਮਝਾਏ (Gujari M:3)', 'grammar_pdf_p38'),

    # Section 10.0 (pages 39-40) — Conjunctive Participle
    ('word_class', 'conjunctive_participle_sihari',
     'conjunctive participle (ਪੂਰਬ-ਪੂਰਨ-ਕਾਰਦੰਤਕ): sihari on base verb = "having done [action]"; action completed before the main verb',
     'ਛੋਡਿ, ਬੈਸਿ, ਧਰਿ, ਕਰਿ, ਭਣਿ, ਘੜਿ, ਬੀਜਿ, ਬੋਲਿ, ਭਖਿ',
     'ਮਾਸੁ ਛੋਡਿ ਬੈਸਿ ਨਕੁ ਪਕੜਹਿ (M:1) | ਧਰਿ ਤਰਾਜੁ ਤੋਲੀਐ (Asa di Var) | ਕਰਿ ਕਿਰਪਾ ਜਿਸੁ ਆਪਿ ਬੁਝਾਇਆ (Sukhmani)', 'grammar_pdf_p39'),

    # Page 40 — parsing principles: sihari determines word boundary and meaning
    ('principle', 'sihari_determines_parsing',
     'absence of sihari where conjunctive participle is expected means the word is a noun — this changes sentence meaning entirely; critical for correct Gurbani parsing',
     'ਸਾਜਨ / ਸਾਜਿ',
     'ਸਾਜਨ ਚਲੇ ਪਿਆਰਿਆ (friends departing) — reading ਸਾਜ ਨ ਚਲੇ is wrong because ਸਾਜਿ (having adorned) would need sihari on ਜ which is absent', 'grammar_pdf_p40'),

    ('principle', 'compound_noun_vs_conjunctive_participle',
     'when sihari is absent on what looks like a conjunctive participle, the word forms a compound noun; determines correct parsing',
     'ਬੋਲੁ-ਵਿਗਾੜੁ',
     'ਜੇ ਕੋ ਆਖੈ ਬੋਲੁ ਵਿਗਾੜੁ (Jap Ji) = compound noun "corruptor of speech", NOT ਬੋਲਿ ਵਿਗਾੜੁ; confirmed by ਅਸੀ ਬੋਲ-ਵਿਗਾੜ ਵਿਗਾੜਹ ਬੋਲ (Siri Rag M:1)', 'grammar_pdf_p40'),
]

cur.executemany('''
    INSERT INTO grammar_rules (category, pattern, meaning, example_word, example_meaning, source)
    VALUES (?, ?, ?, ?, ?, ?)
''', rules)

conn.commit()
print(f'Added {len(rules)} rules')
cur.execute('SELECT COUNT(*) FROM grammar_rules')
print(f'Total grammar_rules: {cur.fetchone()[0]}')
