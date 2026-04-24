import sqlite3
conn = sqlite3.connect('ksd_knowledge.db')
cur = conn.cursor()

rules = [
    # Page 111 — Section 35.1 Bihari plural preposition: extended examples
    ('vowel_mark', 'bihari_plural_preposition_extended',
     'Section 35.1: extended examples of bihari (ੀ) on plural noun = preposition "to/by/with/from"; each noun+bihari encodes specific case relationship',
     'ਪੁੱਤ੍ਰੀ=ਪੁੱਤ੍ਰਾਂ ਨੇ, ਕੰਨੀ=ਕੰਨਾਂ ਨੂੰ, ਨੇਤ੍ਰੀ=ਨੇਤ੍ਰਾਂ ਨਾਲ, ਥਣੀ=ਥਣਾਂ ਕਰਕੇ, ਅਵਤਾਰੀ=ਅਵਤਾਰਾਂ ਵਿਚ',
     'ਪੁੱਤ੍ਰੀ ਕਉਲੁ ਨ ਪਾਲਿਓ (Var Sata) = sons did not keep word | ਕੰਨੀ ਸੁਤਕੁ ਕੰਨਿ ਪੈ ਲਾਇਤਬਾਰੀ ਖਾਹਿ (Asa di Var) = ears hear slander | ਕਿਸਨੁ ਸਦਾ ਅਵਤਾਰੀ ਰੂਪਾ (Vadahans M:3) = Krishna always among incarnations', 'grammar_pdf_p111'),

    # Page 111-112 — Section 35.2 Bihari 1st person verb: additional examples
    ('tense', 'bihari_first_person_verb_extended',
     'Section 35.2: bihari (ੀ) on verb = 1st person singular "I [do]" — additional examples beyond ਸੋਚੀ/ਕਰੀ',
     'ਠਗੀ=ਮੈਂ ਠੱਗਦਾ ਹਾਂ, ਤੋਲੀ=ਮੈਂ ਤੋਲਾਂ',
     'ਹਉ ਠਗਵਾੜਾ ਠਗੀ ਦੇਸੁ (Siri Ragu M:1) = I am a cheater who cheats the land | ਘਟ ਹੀ ਭੀਤਰਿ ਸੋ ਸਹੁ ਤੋਲੀ (Suhi M:1) = within this very vessel I weigh that Husband', 'grammar_pdf_p112'),

    # Page 112 — Section 35.3 Bihari replacing Sihari (3rd plural they + instrumental)
    ('vowel_mark', 'bihari_replacing_sihari_3pl_instrumental',
     'Section 35.3: bihari replaces sihari in two roles: (1) 3rd person plural verb "they do" (=ਨਿ ending); (2) instrumental preposition "by means of / with" — same form, context distinguishes',
     'ਲਹਨੀ=ਲਹਨਿ ਲੈਂਦੇ, ਜਾਣੀ=ਜਾਣਨਿ, ਚੇਤਨੀ=ਚੇਤਨਿ, ਚਲਨੀ=ਚਲਨਿ; ਨਦਰੀ=ਨਦਰ ਨਾਲ, ਵਿਜੋਗੀ=ਵਿਜੋਗ ਨਾਲ, ਬੇਬਾਣੀ=ਬੇਬਾਣ ਵਿਚ',
     'ਨਾਨਕ ਕਰਮਾਂ ਬਾਹਰੇ ਦਰਿ ਢੋਅ ਨ ਲਹਨੀ ਢਾਵਦੇ (Asa di Var) = graceless ones get no support at the door | ਨਦਰੀ ਮੋਖ ਦੁਆਰੁ (Jap Ji) = by the Glance of Grace, the door of liberation | ਰਹੈ ਬੇਬਾਣੀ ਮੜੀ ਮਸਾਣੀ (Asa di Var) = dwells in wilderness of cremation ground', 'grammar_pdf_p112'),

    # Page 113 — Section 6.0 Past Tense -ਨੁ ending with more examples
    ('tense', 'past_tense_nu_extended_examples',
     'Past tense -ਨੁ (singular agent, plural objects) extended examples: verb-stem + ਿਅਨੁ or ਿਓਨੁ = "he/Creator did [to many]"',
     'ਬਖਸਿਅਨੁ, ਉਤਾਰਿਅਨੁ, ਰਖਿਅਨੁ, ਰਿੜਕਿਓਨੁ, ਲਇਅਨੁ, ਨਿਕਾਲਿਅਨੁ',
     'ਕਉਣ ਕਉਣ ਅਪਰਾਧੀ ਬਖਸਿਅਨੁ (M:5) = which sinners did He forgive? | ਚਉਦਹ ਰਤਨ ਨਿਕਾਲਿਅਨੁ ਕੀਤੋਨੁ ਚਾਨਾਣੁ (Var Sata) = He brought out 14 gems and created light | ਮਾਧਾਣਾ ਪਰਬਤੁ ਕਰਿ ਸਬਦਿ ਰਿੜਕਿਓਨੁ (Var Sata) = He churned [the ocean] by the Word', 'grammar_pdf_p114'),

    ('tense', 'parkhiani_plural_vs_parkhianu_singular',
     'ਪਰਖੀਅਨਿ (sihari on ਨ) = plural past "they examined/were examined"; ਪਰਖਿਅਨੁ (aungkar on ਨ) = singular past "He examined" — sihari/aungkar on ਨ determines number of agent',
     'ਪਰਖੀਅਨਿ / ਪਰਖਿਅਨੁ',
     'ਖੋਟੇ ਖਰੇ ਸਭਿ ਪਰਖੀਅਨਿ ਤਿਤੁ ਸਚੈ ਕੈ ਦਰਬਾਰਾ ਰਾਮ (Vadahans M:3) = all the counterfeit and genuine were examined [plural passive] — sihari = plural', 'grammar_pdf_p114'),

    # Page 115 — Section 8.0 Original Aungkar: comprehensive list
    ('vowel_mark', 'original_aungkar_comprehensive',
     'Section 38.0: original/inherited aungkar words — permanent, not grammatical singular marker; includes both masculine and feminine nouns',
     'ਕਿਤੁ, ਸਭਤੁ, ਬਿਨੁ, ਬਹੁਤੁ, ਇਕਤੁ, ਬਿੰਦੁ (neuter/masculine); ਧਾਤੁ, ਭਿਖੁ, ਰਤੁ, ਮਲੁ, ਮਸੁ, ਵਥੁ, ਰੇਣੁ, ਢੇਣੁ, ਕਲਤੁ (feminine)',
     'ਧਾਤੁ ਮਿਲੈ ਫੁਨਿ ਧਾਤੁ ਕਉ (Siri Ragu M:1) = metal meets metal again | ਭਿਖੁ ਕੀ ਕਾਰ ਕਮਾਵਣੀ ਭਿਖੁ ਹੀ ਮਾਹਿ ਸਮਾਹਿ (Siri Ragu M:3) = the task of begging [feminine noun ਭਿਖੁ]', 'grammar_pdf_p115'),

    # Page 117 — Section 39.0 comprehensive ਹੁ vs ਹਹੁ
    ('case', 'hu_single_vs_hahu_double_comprehensive',
     'Section 39.0: single ਹੁ (one ਹ + aungkar, no nasal) = (1) on nouns: nominative/subject case singular; (2) on verbs: future tense 2nd person singular imperative; double ਹਹੁ (two ਹ + aungkar) = (1) on nouns: ablative case singular "from"; (2) on verbs: future tense 2nd person plural imperative',
     'Nouns: ਰਾਹੁ/ਰਾਹਹੁ, ਸਿਆਹੁ/ਸਿਆਹਹੁ, ਸਾਹੁ/ਸਾਹਹੁ; Verbs: ਕਹੁ/ਕਹਹੁ, ਬਹੁ/ਬਹਹੁ, ਰਹੁ/ਰਹਹੁ, ਸਹੁ/ਸਹਹੁ',
     'ਕਹੁ (you singular, say!) vs ਕਹਹੁ (you plural, say!) | ਰਾਹੁ (the path, nominative) vs ਰਾਹਹੁ (from the path, ablative) — single vs double ਹ is the grammatical distinction', 'grammar_pdf_p117'),

    # Page 112-113 — biopsy of ਮਸਾਣੀ/ਗੁਰ ਪਰਸਾਦੀ (brief notes on instrumental bihari)
    ('word_form', 'gur_parsadi_bihari_instrumental',
     'ਗੁਰ ਪਰਸਾਦੀ (bihari) = ਗੁਰੂ ਦੇ ਪਰਸਾਦਿ ਨਾਲ "by Guru\'s grace" — bihari as instrumental preposition on noun',
     'ਗੁਰ ਪਰਸਾਦੀ',
     'ਕਹੈ ਨਾਨਕੁ ਗੁਰ ਪਰਸਾਦੀ ਸਹਜੁ ਉਪਜੈ... (Anand) = by Guru\'s grace, equipoise arises', 'grammar_pdf_p113'),

    # Final summary principle — the master key for vowel mark parsing
    ('principle', 'vowel_mark_master_parsing_key',
     'master parsing key: same word changes meaning based on vowel mark — aungkar (ੁ)=singular noun/masculine OR imperative OR original; sihari (ਿ)=preposition/locative/agent/feminine/plural/conjunctive participle/imperative OR original; bihari (ੀ)=plural preposition/1st person verb/replaces sihari; dulangkar/dulaava (ੁ/ੈ)=case markers; context + vowel together determine meaning',
     'systematic guide to all vowel marks',
     'no single rule: each vowel mark has 3-7 possible functions; grammar + theological context together determine correct reading of Gurbani', 'grammar_pdf_p123'),
]

cur.executemany('''
    INSERT INTO grammar_rules (category, pattern, meaning, example_word, example_meaning, source)
    VALUES (?, ?, ?, ?, ?, ?)
''', rules)

conn.commit()
print(f'Added {len(rules)} rules')
cur.execute('SELECT COUNT(*) FROM grammar_rules')
print(f'Total grammar_rules: {cur.fetchone()[0]}')
