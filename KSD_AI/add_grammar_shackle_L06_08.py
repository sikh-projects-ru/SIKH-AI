import sqlite3
conn = sqlite3.connect('ksd_knowledge.db')
cur = conn.cursor()

rules = [
    # ─── LESSON 6: §060-§064 ─────────────────────────────────────────────────
    ('word_form', 'present_tense_vowel_stem_short_forms',
     'Vowel-stem present tense SHORT forms: abbreviated endings added directly to stem. '
     'In free variation with long forms (§051) — no difference in meaning; '
     'both sets needed for reading SLS verse (metrical freedom). '
     'Paradigm for [hoi]: 1s. +[-īṃ]ਹੋਈ or +[-uṃ]ਹੋਉ; 2s. +[-mhi]ਹੋਹਿ; '
     '3s. +[-e]ਹੋਏ or +[-i]ਹੋਇ (two short vs one long form; [-i] common at verse-end for metre); '
     '1p. +[-mhā]ਹੋਹ; 2p. +[-hu]ਹੋਹੁ; 3p. +[-nhi]ਹੋਨਿ or +[-mhi]ਹੋਹਿ. '
     'No short form for 1s. +[-vāṃ]. '
     'Extended short: 3s. +[-ī]ਹੋਈ; 3p. +[-mhī]ਹੋਹੀ.',
     'ਹੋਈ=ਹੋਵੀ / ਹੋਹਿ=ਹੋਵਹਿ / ਹੋਏ=ਹੋਵੈ / ਹੋਇ / ਹੋਨਿ=ਹੋਵਨਿ',
     'ਹੋਈ (1s. short) = ਹੋਵੀ (1s. long) | ਹੋਏ/ਹੋਇ (3s. short) = ਹੋਵੈ (3s. long) | '
     'ਹੋਇ at verse-end often = 3s. present, not absolutive',
     'shackle_L06_p47_p48'),

    ('word_form', 'intransitive_transitive_vowel_alternation',
     'SLS has many i./t. verb pairs where intransitive stem has short vowel, '
     'transitive has the corresponding long vowel. '
     'Commonest alternation: [a] (i.) ↔ [ā] (t.): ਤਰਿ "be saved" vs ਤਾਰਿ "save". '
     'Also [i] (i.) ↔ [e] (t.): ਮਿਲਿ "meet" vs ਮੇਲਿ "unite".',
     'ਤਰਿ (i.) / ਤਾਰਿ (t.) | ਮਿਲਿ (i.) / ਮੇਲਿ (t.)',
     'ਤਰਿ [tar-] be saved (i., short [a]) ↔ ਤਾਰਿ [tār-] save (t., long [ā]) | '
     'ਮਿਲਿ [mil-] meet (i., [i]) ↔ ਮੇਲਿ [mel-] unite (t., [e])',
     'shackle_L06_p48'),

    ('word_form', 'causative_verb_formation',
     'Causative: independent verb formed by adding [-ā-] to the simple stem. '
     'If simple verb is intransitive → causative = corresponding transitive: '
     'ਚਲਿ "go" → ਚਲਾਇ "make go, cause to depart". '
     'If simple verb is transitive → causative = "cause the action to be done by someone else": '
     'ਕਰਿ "do" → ਕਰਾਇ "cause to be done". '
     'Some causatives have lexicalised meanings: ਸੁਣਿ "hear" → ਸੁਣਾਇ "tell" (lit. cause to be heard). '
     'Causatives conjugated like vowel-stem verbs in [ā].',
     'ਚਲਿ → ਚਲਾਇ | ਕਰਿ → ਕਰਾਇ | ਸੁਣਿ → ਸੁਣਾਇ',
     'ਚਲਾਇ = cause to go | ਕਰਾਇ = cause to be done | ਸੁਣਾਇ = tell (lit. cause to be heard)',
     'shackle_L06_p48_p49'),

    ('word_class', 'demonstrative_ohu_alternative',
     'ਓਹੁ=ਓਹ is a less frequent alternative to ਸੋ/ਸੁ "that, he/she". '
     'Used in exactly the same way. '
     'Declension: ਓਹੁ (m.sd.) : ਓਹ (f.sd.) → ਓਹਿ/ਓਇ (pd. those/they). '
     'Similar to ਏਹੁ "this" declension (§032).',
     'ਓਹੁ / ਓਹ / ਓਹਿ=ਓਇ',
     'ਓਹੁ (that/he) : ਓਹ (that/she) → ਓਹਿ (those/they) — alternative to ਸੋ',
     'shackle_L06_p49'),

    ('word_form', 'repeated_negative_neither_nor',
     '[na]/[nā] "not" may be repeated before successive words or phrases '
     'to give the sense of the English "neither...nor...".',
     'ਨਾ ਓਹੁ ਆਵੈ ਨਾ ਓਹੁ ਜਾਇ',
     'ਨਾ ਓਹੁ ਆਵੈ ਨਾ ਓਹੁ ਜਾਇ = neither does he come, nor does he go',
     'shackle_L06_p49'),

    # ─── LESSON 7: §070-§073 ─────────────────────────────────────────────────
    ('word_form', 'infinitive_and_gerundive_formation',
     'Infinitive (noun of action): consonant-stems + [-aṇu]; vowel-stems + [-vaṇu] (long) or [-ṇu] (short). '
     'Declined like masculine nouns declension I (sd. in [-u]). '
     'Gerundive (adjective "ought to be done"): consonant-stems + [-aṇā]; vowel-stems + [-vaṇā] or [-ṇā]. '
     'Declined like adjectives AII. '
     'Infinitive/gerundive are partly interchangeable: ਪੀਣਾ=ਪੀਵਣੁ, ਖਾਣਾ=ਖਾਵਣੁ, ਮਰਣਾ=ਮਰਣੁ. '
     'Absolutive preferred in this book for referring to verbs.',
     'ਕਰਣੁ / ਕਰਣਾ | ਆਵਣੁ ਜਾਣੁ | ਖਾਵਣਾ | ਚਲਣਾ',
     'ਕਰਣੁ = to do/doing (infinitive) | ਕਰਣਾ = to be done (gerundive) | '
     'ਆਵਣੁ ਜਾਣੁ = coming and going; transmigration | ਚਲਣਾ = to be gone / ought to go',
     'shackle_L07_p52_p53'),

    ('word_class', 'relative_pronoun_jo_ji',
     'Relative pronoun ਜੋ=ਜਿ: single pair of forms for direct case (sd. and pd., both genders). '
     'Equivalent to English: who, what, which; whoever, whatever, whichever.',
     'ਜੋ = ਜਿ',
     'ਜੋ ਆਵਹਿ ਸੇ ਜਾਹਿ = who come, they go → those who come, go',
     'shackle_L07_p53'),

    ('principle', 'relative_clause_word_order',
     'SLS relative clause comes FIRST; main clause follows, introduced by a demonstrative '
     '(the "correlative"). Opposite of English order. '
     'Relative pronoun ਜੋ/ਜਿ may be omitted — order unchanged. '
     'Sentence must be translated beginning with the main clause in English.',
     'ਜੋ ਭਾਵੈ ਸੇ ਹੋਇ | ਕਰਤਾ ਕਰੇ ਸੁ ਹੋਇ',
     'ਜੋ ਭਾਵੈ ਸੇ ਹੋਇ = what pleases, that happens → that which pleases [Him] happens | '
     'ਕਰਤਾ ਕਰੇ ਸੁ ਹੋਇ = [what] Creator does, that happens → whatever Creator does comes to pass '
     '(ਜੋ omitted, ਸੁ is correlative)',
     'shackle_L07_p53'),

    ('word_class', 'correlative_pairs_j_t',
     'Many rhyming relative (j-) / correlative (t-) pairs. '
     'Adjective pairs: ਜੇਤਾ...ਤੇਤਾ "as much...so much"; ਜੇਤੇ...ਤੇਤੇ "as many...so many"; '
     'ਜੈਸਾ=ਜੇਹਾ...ਤੈਸਾ=ਤੇਹਾ "of which kind...of such a kind"; ਜੇਵੜੁ...ਤੇਵੜੁ "of which size...so great". '
     'Adverb pairs: ਜਾਂ...ਤਾਂ "when...then"; ਜਿਉ...ਤਿਉ "as...so"; ਜਹ...ਤਹ "where...there".',
     'ਜੇਤਾ...ਤੇਤਾ / ਜਿਉ...ਤਿਉ / ਜਹ...ਤਹ',
     'ਜਹ ਦੇਖਾ ਤਹ ਸੋਈ = where I look, there He [is] → He is wherever I look',
     'shackle_L07_p54'),

    # ─── LESSON 8: §080-§084 ─────────────────────────────────────────────────
    ('principle', 'oblique_case_introduction',
     'Oblique case (o.): most important non-direct case in SLS. '
     'Corresponds roughly to English "me, him, whom" (vs "I, he, who"). '
     'Used: (1) as direct/indirect object of transitive verbs; '
     '(2) before postpositions; (3) other functions (for, in, possessive) determined by context. '
     'No verb for "have" in SLS — oblique often carries possessive sense.',
     'ਹਉ ਤੁਧੁ ਆਖਾ | ਮੈ ਅਵਰੁ ਦੂਜਾ ਨ ਕੋਇ',
     'ਹਉ ਤੁਧੁ ਆਖਾ = I say to you (ਤੁਧੁ = oblique of ਤੂੰ) | '
     'ਮੈ ਅਵਰੁ ਦੂਜਾ ਨ ਕੋਇ = [for] me there is no other (possessive via oblique)',
     'shackle_L08_p57'),

    ('word_form', 'personal_pronouns_oblique',
     'Personal pronoun oblique forms. Singular pronouns change; plurals unchanged. '
     'ਹਉ (I) → ਮੈ (me/to me). '
     'ਤੂੰ=ਤੁ (you/Thou) → ਤੁਧੁ=ਤੁਝੁ (you/Thee, oblique). '
     'ਹਮ (we) → ਹਮ (us, unchanged). '
     'ਤੁਮ (you pl.) → ਤੁਮ (unchanged).',
     'ਹਉ→ਮੈ | ਤੂੰ→ਤੁਧੁ=ਤੁਝੁ | ਹਮ→ਹਮ | ਤੁਮ→ਤੁਮ',
     'ਮੈ = me / to me / in me (oblique of ਹਉ) | ਤੁਧੁ/ਤੁਝੁ = you Thee (oblique of ਤੂੰ)',
     'shackle_L08_p57'),

    ('word_form', 'other_pronouns_oblique',
     'Other pronouns have distinct so. (singular oblique) and po. (plural oblique) forms; '
     'no m./f. distinction in oblique. '
     'True 3p.: ਸੋ:ਸਾ → ਤਿਸੁ=ਤੈ (him/her); ਸੇ=ਤੇ → ਤਿਨ=ਤਿੰਨਾ (them). '
     'Relative: ਜੋ → so. ਜਿਸੁ=ਜੈ (whom); po. ਜਿਨ=ਜਿੰਨਾ. '
     'Interrogative: ਕਉਣੁ → so. ਕਿਸੁ=ਕੈ (whom?); po. ਕਿਨ=ਕਿੰਨਾ. '
     'Demonstratives: ਏਹੁ → so. ਏਸੁ; po. ਏੰਨਾ | ਓਹੁ → so. ਓਸੁ; po. ਓੰਨਾ. '
     'ਸਭਿ → po. ਸਭਨਾ; ਹੋਰਿ → po. ਹੋਰਨਾ; ਇਕਿ → po. ਇਕਨਾ.',
     'ਤਿਸੁ=ਤੈ / ਤਿਨ=ਤਿੰਨਾ | ਜਿਸੁ=ਜੈ / ਜਿਨ=ਜਿੰਨਾ | ਏਸੁ/ਏੰਨਾ | ਓਸੁ/ਓੰਨਾ',
     'ਤਿਸੁ = him/her (so.) | ਤਿਨ/ਤਿੰਨਾ = them (po.) | ਜਿਸੁ = whom (so.) | ਓਸੁ = that/him/her (so.)',
     'shackle_L08_p58'),

    ('principle', 'postpositions_follow_oblique',
     'SLS has postpositions (placed AFTER the word they govern) instead of English prepositions. '
     'Never placed after direct case — always follow oblique case. '
     'So. pronoun before postposition often ends in [-a] instead of [-u]. '
     'Common postpositions: ਕਉ=ਨੋ (to, for); ਨਾਲਿ=ਸਿਉ (with); ਸਰਿ (like); ਬਿਨੁ (without/except).',
     'ਤੁਧੁ ਨੋ / ਓਨਾ ਅੰਦਰਿ / ਬਿਨੁ',
     'ਗਾਵਨਿ ਤੁਧੁ ਨੋ ਪਉਣੁ ਪਾਣੀ = air and water sing to you (ਨੋ after oblique ਤੁਧੁ) | '
     'ਓਨਾ ਅੰਦਰਿ ਨਾਮੁ ਨਿਧਾਨੁ ਹੈ = inside them is the Name, the treasure',
     'shackle_L08_p59'),
]

cur.executemany('''
    INSERT INTO grammar_rules (category, pattern, meaning, example_word, example_meaning, source)
    VALUES (?, ?, ?, ?, ?, ?)
''', rules)

conn.commit()
print(f'Added {len(rules)} rules')
cur.execute('SELECT COUNT(*) FROM grammar_rules')
print(f'Total grammar_rules: {cur.fetchone()[0]}')
