import sqlite3
conn = sqlite3.connect('ksd_knowledge.db')
cur = conn.cursor()

rules = [
    # ─── LESSON 9: §090-§094 ─────────────────────────────────────────────────
    ('number', 'masculine_noun_oblique_by_declension',
     'Masculine noun oblique cases by declension. '
     'Decl I (sd.[-u]): so. in [-a] or [-ai]; pd. in [-a]; po. in [-āṃ]. '
     'Nouns with [urā] in sd.: ਜੀਉ → so. ਜੀਅ=ਜੀਐ; note ਭਉ (fear) → so. ਭੈ. '
     'Nouns with sd. [-āmu]: ਨਾਉ → so. ਨਾਵ=ਨਾਵੈ (two so. forms in free variation); po. ਨਾਵਾਂ. '
     'Decl II (sd.[-ā]): so. = pd. in [-e]; po. in [-iāṃ] — ਮੰਗਤਾ → so./pd. ਮੰਗਤੇ → po. ਮੰਗਤਿਆਂ. '
     'Decl III (sd.=so.=pd.): only po. is distinctive, in [-āṃ] — ਪਾਪੀ → po. ਪਾਪੀਆਂ.',
     'ਮਠੁ→ਮਠ=ਮਠੈ/ਮਠਾਂ | ਜੀਉ→ਜੀਅ=ਜੀਐ | ਭਉ→ਭੈ | ਨਾਉ→ਨਾਵ=ਨਾਵੈ | ਮੰਗਤਾ→ਮੰਗਤੇ/ਮੰਗਤਿਆਂ | ਪਾਪੀ→ਪਾਪੀਆਂ',
     'ਭਉ [fear] sd. → ਭੈ so. (irregular) | ਨਾਉ [name] so. ਨਾਵ/ਨਾਵੈ — two forms in free variation',
     'shackle_L09_p62'),

    ('number', 'feminine_noun_oblique_by_declension',
     'Feminine nouns: mostly no special oblique form — so.=sd., po.=pd. '
     'Decl IV: sd.=so.[-a], pd.=po.[-āṃ]. '
     'Decl V: sd.=so.[-i], pd.=po.[-īṃ]. '
     'Decl VI (sd.[-u]): so.[-u] — has a form for so. but same as sd.; pd.=po.[-ūṃ]. '
     'Decl VII: sd.=so.[-ī], pd.+po.[-iāṃ]. '
     'Decl VIII: sd.=so.',
     'ਵਸਤੁ (decl VI: sd.=so.[-u], pd.=po.[-ūṃ])',
     'Feminine oblique: generally so.=sd. and po.=pd. — learn exceptions per declension',
     'shackle_L09_p63'),

    ('word_class', 'adjective_oblique_AII_masculine',
     'Adjective AII (msd.[-ā]) oblique: mso. in [-e] = mpd. in [-e]; mpo. in [-iāṃ]. '
     'Note: mpo.[-iāṃ] vs fpo.[-iāṃ] differ in nasalisation and must be distinguished. '
     'Adj AI: all m. and f. d./o. forms in [-a] — no separate oblique form. '
     'Adj AIII: no change for any case.',
     'ਕੁੜਾ (msd.) → ਕੁੜੇ (mso./mpd.) → ਕੁੜਿਆਂ (mpo.) | ਕੁੜੀ (fsd./fso.) → ਕੁੜੀਆਂ (fpd./fpo.)',
     'ਕੁੜੇ = mso. or mpd. false | ਕੁੜਿਆਂ = mpo. | ਕੁੜੀ = fsd./fso. | ਕੁੜੀਆਂ = fpd./fpo.',
     'shackle_L09_p63'),

    ('principle', 'noun_oblique_compound_possessive',
     'Noun in oblique used as first member of a compound with another noun. '
     'Two types: (1) coordinate pair — ਆਵਣੁ ਜਾਣੁ "coming and going, transmigration"; '
     '(2) possessive — ਹਰਿ ਨਾਮੁ "God\'s name" (oblique as genitive). '
     'First element may be adjective-as-noun: ਨਿਰਮਲ ਨਾਮੁ "name of the Pure One" '
     '(vs ਨਿਰਮਲੁ ਨਾਮੁ "pure name" — adjective agreeing with noun). '
     'Only second element is declined; first remains in oblique.',
     'ਹਰਿ ਨਾਮੁ / ਨਿਰਮਲ ਨਾਮੁ / ਆਵਣੁ ਜਾਣੁ',
     'ਹਰਿ ਨਾਮੁ = God-name (possessive compound) | '
     'ਨਿਰਮਲ ਨਾਮੁ = name of the Pure One (adj-as-noun+noun) | '
     'ਨਿਰਮਲੁ ਨਾਮੁ = pure name (simple adjective+noun)',
     'shackle_L09_p64'),

    ('word_form', 'postposition_kau_no_object_marker',
     '[kau] and [no] "to, for" are also used to mark the direct object of transitive verbs. '
     'In that case they are not translated into English — equivalent to noun alone in oblique/direct. '
     '[binu]/[viṇu] "without" may precede the noun they govern (i.e. used as preposition). '
     'Word governed always in oblique, whatever the position: ਬਿਨੁ ਗੁਰ = ਗੁਰ ਬਿਨੁ.',
     'ਸੁਖ ਕਉ ਮੰਗੈ / ਬਿਨੁ ਗੁਰ = ਗੁਰ ਬਿਨੁ',
     'ਸੁਖ ਕਉ ਮੰਗੈ ਸਭੁ ਕੋ = everyone asks for happiness (ਕਉ marks direct object) | '
     'ਬਿਨੁ ਗੁਰ = ਗੁਰ ਬਿਨੁ = without the guru',
     'shackle_L09_p64_p65'),

    ('word_form', 'oblique_infinitive_purpose_and_allow',
     'Oblique of infinitive (in [-aṇa] or [-aṇai]): used before postpositions, in compounds. '
     'With [jāi] "go" → expresses purpose: ਨਾਵਣ ਜਾਉ = "I go to bathe". '
     'With [de] "give" → expresses "allow to": ਨਾਵਣ ਨ ਦੇਇ = "he does not allow [one] to bathe".',
     'ਨਾਵਣ ਜਾਉ / ਨਾਵਣ ਨ ਦੇਇ',
     'ਨਾਵਣ ਜਾਉ = I go to bathe (obl.inf.+jāi = purpose) | '
     'ਨਾਵਣ ਨ ਦੇਇ = he does not allow to bathe (obl.inf.+de = allow)',
     'shackle_L09_p65'),

    # ─── LESSON 10: §100-§104 ────────────────────────────────────────────────
    ('word_form', 'possessive_postposition_ka_declension',
     'Possessive postposition [kā] "\'s, of": declined like adjective AII — '
     'agrees in gender, number, case with the OBJECT POSSESSED (not the possessor). '
     'Possessor is in oblique (as with all postpositions). '
     'm.sg.d. ਕਾ / m.sg.o. ਕੇ / m.pl.d.&o. ਕੇ / m.pl.o. ਕਿਆਂ; '
     'f. forms: ਕੀ (sg.d.&o.) / ਕੀਆਂ (pl.d.&o.). '
     'Less common equivalents: [dā], [sandā], [kerā] — all declined the same way.',
     'ਹਰਿ ਕਾ ਨਾਮੁ / ਹਰਿ ਕੀ ਸਿਫਤਿ / ਗੁਰ ਕੇ ਗੁਣ',
     'ਹਰਿ ਕਾ ਨਾਮੁ = God\'s name (ਕਾ agrees with m. ਨਾਮੁ) | '
     'ਤਾ ਕਾ = ਤਿਸ ਕਾ = his/hers/its | ਜਾ ਕਾ = ਜਿਸ ਕਾ = whose',
     'shackle_L10_p68_p69'),

    ('word_form', 'adjectival_postpositions_jeta_vihuna',
     'Other adjectival postpositions (declined like adjectives, agree with object): '
     'Relative adjectives (§072) used as postpositions: '
     '...ਜੇਤਾ "as much as"; ...ਜੇਤੇ "as many as"; ...ਜੈਸਾ=ਜੇਹਾ "like"; ...ਜੇਵੜੁ "as great as". '
     'Words used only as postpositions: '
     '...ਵਿਹੁਣਾ "without, lacking"; ...ਬਾਹਰਾ "bereft of, without".',
     'ਗਿਆਨ ਵਿਹੁਣਾ / ਸਤਿਗੁਰ ਜੇਵੜੁ',
     'ਗਿਆਨ ਵਿਹੁਣਾ = lacking knowledge | ਸਤਿਗੁਰ ਜੇਵੜੁ ਦਾਤਾ ਕੇ ਨਹੀ = '
     'there is no giver as great as the true guru',
     'shackle_L10_p69'),

    ('word_form', 'verbal_agent_suffix_haru',
     'Verbal agent: expresses "the doer of the action". '
     'Formed by adding suffix [-hāru] to the oblique infinitive (§094). '
     'Declined like masculine noun decl I.',
     'ਕਰਣੁ → ਕਰਣਹਾਰੁ = ਕਰਨੇਹਾਰੁ',
     'ਕਰਣੁ "to do" → ਕਰਣਹਾਰੁ/ਕਰਨੇਹਾਰੁ "doer, maker, creator" | '
     'ਸਿਰਜਣਹਾਰੁ "the Creator" — common in Gurbani',
     'shackle_L10_p69'),

    ('word_form', 'absolutive_extensions_kai',
     'Absolutive [-i] may be lengthened to [-ī] — no difference in sense. '
     'Absolutive may be followed by particle [kai] → extended form [-i kai]: ਕਰਿ ਕੈ "having done". '
     'No clear difference in meaning from simple absolutive. '
     'Extended [-i kai] CANNOT be used in compounds (e.g., with [sakki] or [jāṇi]).',
     'ਕਰਿ ਕੈ',
     'ਕਰਿ ਕੈ = having done (= ਕਰਿ, but cannot precede ਸਕੈ or ਜਾਣੈ in this form)',
     'shackle_L10_p70'),

    # ─── LESSON 11: §110-§113 ────────────────────────────────────────────────
    ('word_form', 'vocative_case_noun_forms',
     'Vocative case (v.): used when addressing. Only nouns have distinctive forms; '
     'sv. (singular vocative) often = so.; pv. (plural vocative) rarely encountered. '
     'M. nouns: decl I — sv.[-a] (= so.) or [-ā]: ਨਾਨਕ/ਨਾਨਕਾ "O Nanak!". '
     'Decl II — sv.[-e] (= so.) or [-iā]; pv.[-iho]: ਸਚੇ=ਸਚਿਆ "O true one!". '
     'Decl III — sv. = sd. or [-ā]; pv.[-ho]: ਭਾਈ = ਭਾਈਆ "O brother!"; ਭਾਈਹੋ. '
     'F. nouns: only decl IV (sv.[-e]: ਮੁੰਧੇ "O woman!") and '
     'decl VII (sv.[-ī]=so. or [-īe]; pv.[-īho]: ਸਖੀ=ਸਖੀਏ; ਸਖੀਹੋ). '
     'Adjectives qualifying vocative nouns appear in the oblique. '
     'Pronouns have no vocative case.',
     'ਨਾਨਕ=ਨਾਨਕਾ | ਸਚੇ=ਸਚਿਆ | ਭਾਈ=ਭਾਈਆ/ਭਾਈਹੋ | ਮੁੰਧੇ | ਸਖੀ=ਸਖੀਏ/ਸਖੀਹੋ',
     'ਮੇਰੇ ਸਚਿਆ = O my true one! (adjective ਮੇਰੇ in oblique, noun in sv.) | '
     'ਰੇ ਮਨਾ = O heart! (interjection [re] + m. vocative)',
     'shackle_L11_p72'),

    ('word_form', 'interjections_re_ri',
     'Interjection [re] used with m. nouns in vocative; f. equivalent [rī]. '
     'May precede or follow the vocative noun. '
     'Other interjections used independently (often as rhyme-words at verse-end): '
     'ਜੀਉ "sir!" — used without a noun.',
     'ਮਨ ਰੇ = ਰੇ ਮਨਾ / ਰੀ ਮਾਈ / ਜੀਉ',
     'ਰੇ ਮਨਾ = O heart! (m.) | ਰੀ ਮਾਈ = O mother! (f.) | ਜੀਉ = sir! (independent)',
     'shackle_L11_p73'),

    ('word_form', 'imperative_formation',
     'Imperative restricted to 2nd person normally. '
     'Consonant-stems: 2s. +[-u] or +[-i] (= abs.); 2p. +[-ahu] (commonest) or +[-ihu] or +[-iahu]. '
     'Vowel-stems: 2s. +[-u] or +[-i]; 2p. +[-vahu]. '
     'Common vowel-stem verbs with 2s. in [-hu]/[-hi]: '
     'ਹੋਇ→ਹੋਹੁ "be!"; ਜਾਇ→ਜਾਹਿ "go!"; ਦੇ→ਦੇਹਿ "give!"; ਲੈ→ਲੈਹਿ "take!". '
     '3rd person imperative (rare): 3s.+[-au] ਜਲਉ "let it burn!"; 3p.+[-anu] ਜਲਨੁ.',
     'ਜਾਣੁ=ਛੋੜਿ (2s.) / ਜਾਣਹੁ=ਛੋੜਿਹੁ (2p.) | ਆਉ=ਪਾਇ (2s.) / ਆਵਹੁ (2p.) | ਹੋਹੁ / ਜਾਹਿ / ਦੇਹਿ',
     'ਦੇਹਿ = give! (2s. vowel-stem with [-hi]) | ਜਾਣਿਅਹੁ = know! (2p. with [-iahu]) | '
     'ਜਲਉ = let it burn! (3s. imperative)',
     'shackle_L11_p73_p74'),

    ('word_form', 'gerundive_uses_obligation',
     'Gerundive [-ṇā]: carries sense of obligation — "ought to be done", "must". '
     'Often equivalent to a general command ("one must..."). '
     'Logical subject expressed in oblique case. '
     'ਸਾਚੀ ਕਾਰ ਕਮਾਵਣੀ = "true work is to be performed". '
     'ਉਠਿ ਚਲਣਾ = "one will have to get up and go". '
     'ਖੋਟੇ ਖੋਟੁ ਕਮਾਵਣਾ = "the false must perform falseness" (subject ਖੋਟੇ in oblique).',
     'ਕਰਣਾ / ਸਾਚੀ ਕਾਰ ਕਮਾਵਣੀ / ਉਠਿ ਚਲਣਾ',
     'ਉਠਿ ਚਲਣਾ = one will have to get up and go (general obligation) | '
     'ਖੋਟੇ ਖੋਟੁ ਕਮਾਵਣਾ = the false must perform falseness (oblique subject)',
     'shackle_L11_p74'),
]

cur.executemany('''
    INSERT INTO grammar_rules (category, pattern, meaning, example_word, example_meaning, source)
    VALUES (?, ?, ?, ?, ?, ?)
''', rules)

conn.commit()
print(f'Added {len(rules)} rules')
cur.execute('SELECT COUNT(*) FROM grammar_rules')
print(f'Total grammar_rules: {cur.fetchone()[0]}')
