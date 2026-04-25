import sqlite3
conn = sqlite3.connect('ksd_knowledge.db')
cur = conn.cursor()

rules = [
    # ─── LESSON 14: §140-§143 ───────────────────────────────────────────────────
    ('word_form', 'locative_case_masculine_declensions',
     'Locative (l.) — 5th and final case in SLS. '
     'Typical endings: [-i], [-ī], [-īṃ], [-e], [-ai]. '
     'Masculine declension I (sd. [-u]): sl. in [-i] or [-e] or [-ī]; pl. in [-īṃ]: '
     'ਮਨੁ → sl. ਮਨਿ = ਮਨੇ = ਮਨੀ; pl. ਮਨੀਂ. '
     'Sub-type ਨਾਉ (sd. [-āmu]): sl. ਨਾਇ = ਨਾਏ = ਨਾਈ; pl. ਨਾਈਂ. '
     'Declension II (sd. [-ā]): sl. in [-ai] (= so.); pl. in [-īṃ]: ਮੰਗਤਾ → sl. ਮੰਗਤੇ; pl. ਮੰਗਤੀਂ. '
     'Declension III: sl. = sd.; pl. in [-īṃ]: ਪਾਪੀ → sl. ਪਾਪੀ; pl. ਪਾਪੀਂ. '
     'Note: Dec. I sl. in [-e] vs Dec. II sl. in [-ai] are REVERSE of their oblique forms.',
     'ਮਨਿ=ਮਨੇ / ਮਨੀਂ | ਨਾਇ=ਨਾਏ=ਨਾਈ / ਨਾਈਂ | ਮੰਗਤੇ / ਮੰਗਤੀਂ | ਪਾਪੀ / ਪਾਪੀਂ',
     'ਮਨਿ = in the mind (sl.) | ਨਾਇ = in/of the Name (sl.) | '
     'ਘਰਿ = in the home (sl. Dec. I) | ਹਰਿ = in/of God (sl. Dec. I)',
     'shackle_L14_p88_p89'),

    ('word_form', 'locative_case_feminine_declensions',
     'Feminine locative: only declension IV commonly has special forms; others rare. '
     'Dec. IV (sd. [-a]): sl. in [-i] or [-ai]; pl. in [-īṃ]: ਦੇਹ → sl. ਦੇਹਿ = ਦੇਹੀ; pl. ਦੇਹੀਂ. '
     'Dec. V (sd. [-i] = sd.): sl. in [-i]; pl. in [-īṃ]: ਰਾਤਿ → sl. ਰਾਤਿ; pl. ਰਾਤੀਂ. '
     'Dec. VI: only d./o. occur (rare declension). '
     'Dec. VII (sd. [-ī]): sl. = sd.; pl. in [-īṃ]: ਸਖੀ → sl. ਸਖੀ; pl. ਸਖੀਂ. '
     'Dec. VIII (abstract nouns in [-ā]): mostly indeclinable — treated as uninflected.',
     'ਦੇਹਿ=ਦੇਹੀ / ਦੇਹੀਂ | ਰਾਤਿ / ਰਾਤੀਂ | ਸਖੀ / ਸਖੀਂ',
     'ਦੇਹਿ/ਦੇਹੀ = in the body (sl. Dec. IV) | ਰਾਤਿ = in/at night (sl. Dec. V) | '
     'ਸਖੀ = among/in girl-friends (sl. Dec. VII)',
     'shackle_L14_p90'),

    ('principle', 'locative_functions_place_instrumental',
     'Locative covers two main functions: '
     '(1) PLACE — "in, on, at": ਬਿਨੁ ਨਾਵੈ ਕਿਉ ਸਾਚਿ ਸਮਾਵੈ "without the Name how enter in the truth". '
     '(2) INSTRUMENTAL (rarer) — "by, through, with": absorbs old instrumental case. '
     'Many postpositions/adverbs ending in [-i] or [-ai] are simply fossilized locatives: '
     'ਅੰਦਰਿ "inside" (= locative of ਅੰਦਰ), ਅਗੇ = ਅਗਰੇ "before". '
     'Set instrumental phrases: ਸਹਜਿ = ਸਹਜੇ "through sahaj/naturally"; '
     'ਗੁਰ ਪਰਸਾਦੀ "through the Guru\'s grace"; ਗੁਰਮੁਖਿ "through the Guru\'s teaching".',
     'ਮਨਿ / ਸਬਦਿ / ਸਹਜਿ=ਸਹਜੇ / ਗੁਰਮੁਖਿ / ਅੰਦਰਿ',
     'ਸਬਦਿ ਨੀੰਧਾਵਣਹਾਰੁ = delivering across through the Word | '
     'ਸਹਜਿ = through sahaj, easily, naturally | ਗੁਰਮੁਖਿ = through/via the Guru\'s teaching',
     'shackle_L14_p91'),

    # ─── LESSON 15: §150-§153 ───────────────────────────────────────────────────
    ('word_form', 'adjective_locative_AI_AII_AIII',
     'Adjectival declensions for locative: '
     'AI (adj. in [-u]): only msl. has distinct form [-i] or [-u] (= mso.); '
     'all other forms (mp., fs., fp.) unchanged: ਨਿਰਮਲੁ → msl. ਨਿਰਮਲਿ = ਨਿਰਮਲ. '
     'AII (commonest): masculine follows noun Dec. II; feminine follows Dec. VII. '
     'Full AII paradigm: msd. ਕੂੜਾ; mso. ਕੂੜੇ; msl. ਕੂੜੇ = ਕੂੜੇ (same as mso.!); '
     'mp. ਕੂੜੇ; mpo. ਕੂੜਿਆਂ; mpl. ਕੂੜੀਂ | fsd./fso./fsl. ਕੂੜੀ; fp. ਕੂੜੀਆਂ; fpl. ਕੂੜੀਂ. '
     '[kā] locative: msl. ਕੇ = ਕੇ; mpl. ਕੀਂ; fsl. ਕੀ; fpl. ਕੀਂ. '
     'AIII (adj. in [-ī]): no inflection for gender, number, or case.',
     'ਨਿਰਮਲਿ / ਕੂੜੇ (msl.) / ਕੂੜੀ (fsl.) / ਕੂੜੀਂ (pl.)',
     'ਨਿਰਮਲਿ ਨਾਮਿ = in the pure Name (AI msl.) | ਕੂੜੇ ਮਨਿ = in the false mind (AII msl.) | '
     'ਕੂੜੀ ਭਗਤਿ = in false devotion (AII fsl.) | ਤੇਰੀ ਕੀ = of yours (f. possessive locative)',
     'shackle_L15_p94_p95'),

    ('word_form', 'verbs_lai_pai_irregular_conjugation',
     'Two irregular verb stems ending in [-ai]: '
     '[ਲੈ] = [ਲੇ] "take": abs. ਲੈ = ਲੇ; pres. 3s. ਲਏ = ਲੇਇ; 3p. ਲੈਨਿ = ਲਵਹਿ = ਲੇਹਿ. '
     '[ਪੈ] = [ਪਵਿ] "fall, lie" (intransitive): abs. ਪੈ = ਪਵਿ; pres. 3s. ਪਾਇ = ਪਵੈ; 3p. ਪਾਹਿ = ਪਵਨਿ. '
     '[ਪਾਇ] = [ਪਾਵਿ] "get, find; put, throw" (TRANSITIVE): abs. ਪਾਇ; pres. 3s. ਪਾਵੈ = ਪਾਏ. '
     'To distinguish: [ਪਾਇ] conjugated in long [v]-form when possible. '
     'Noun + [ਪੈ/ਪਵਿ] = intransitive compound; noun + [ਪਾਇ] = transitive: '
     'ਕੀਮਤਿ ਨ ਪੈ = "be priceless" vs ਕੀਮਤਿ ਨ ਪਾਇ = "be unable to estimate the price".',
     'ਲੈ=ਲੇ / ਲਏ / ਲੈਨਿ | ਪੈ=ਪਵਿ / ਪਾਇ=ਪਵੈ | ਪਾਇ / ਪਾਵੈ',
     'ਲੈ/ਲੇ = take (abs.) | ਲਏ/ਲੇਇ = he takes (3s.) | ਪੈ = fall, lie (abs.) | '
     'ਪਾਇ (intrans.) = fall, lie vs ਪਾਇ (trans.) = get/find/put — distinguish by context',
     'shackle_L15_p95_p96'),

    ('word_form', 'locative_compound_verbs',
     'Locative compound verbs: noun in LOCATIVE + intransitive verb. '
     'Common verbs: [āi] "come", [pai]/[pavi] "fall", [laggi]/[lāgi] "cling, be attached". '
     'Fixed idioms (meanings often non-literal, must be learnt): '
     'ਕੀਮਿ/ਕਾਮਿ ਨ ਆਇ "be of no use" (not come in work); '
     'ਚਿਤਿ ਆਇ "come to mind, be remembered"; '
     'ਥਾਇ ਨ ਪੈ/ਪਵਿ "find no place"; '
     'ਪਾਰਿ ਪੈ/ਪਵਿ "get across"; '
     'ਪਲੈ ਪੈ/ਪਵਿ "be acquired" (lit. fall in hem); '
     'ਲੇਖੇ ਨ ਪੈ/ਪਵਿ "not be credited with"; '
     'ਪਾਇ ਲਗਿ/ਲਾਗਿ "cling to feet"; '
     'ਗਲਿ ਮਿਲਿ "go and embrace". '
     'The noun in these compounds is locative; qualifying words must also be in locative.',
     'ਕਾਮਿ ਨ ਆਇ / ਚਿਤਿ ਆਇ / ਥਾਇ ਨ ਪੈ / ਪਾਰਿ ਪੈ / ਪਲੈ ਪੈ / ਪਾਇ ਲਗਿ',
     'ਕਾਮਿ ਨ ਆਇ = be of no use | ਚਿਤਿ ਆਇ = come to mind | ਪਾਰਿ ਪੈ = get across | '
     'ਪਾਇ ਲਗਿ = cling to feet | ਨਾਨਕੁ ਤਿਨ ਕੈ ਲਾਗੈ ਪਾਇ = Nanak clings to their feet',
     'shackle_L15_p96_p97'),

    ('word_form', 'locative_infinitive',
     'Infinitive has a locative case (besides oblique §094), following masculine declension I: '
     'd. ਆਖਣੁ; o. ਆਖਣ = ਆਖਣੇ; l. ਆਖਣਿ. '
     'Uses: '
     '(1) Simple locative/instrumental: ਦੇਣਿ ਨ ਜੋਰੁ = "there is no power in giving". '
     '(2) + [jai] "go" → purpose. '
     '(3) + [de] "give" → "allow to [do]" (same as oblique infinitive §094). '
     '(4) + [pai/pavi] or [laggi/lāgi] → "begin to": '
     'ਜੇ ਕੋ ਖਾਇਕੁ ਆਖਣਿ ਪਾਇ = "if some loudmouth begins to speak". '
     '(5) + [mili] (negative) → "not be allowed to, be unable to": '
     'ਹੁਣਿ ਕਹਣਿ ਨ ਮਿਲੈ ਖੁਦਾਇ = "now they are unable to say God".',
     'ਆਖਣਿ / ਦੇਣਿ ਨ ਜੋਰੁ / ਆਖਣਿ ਪਾਇ / ਕਹਣਿ ਨ ਮਿਲੈ',
     'ਦੇਣਿ ਨ ਜੋਰੁ = there is no power in giving (loc. inf.) | '
     'ਆਖਣਿ ਪਾਇ = begin to speak | ਕਹਣਿ ਨ ਮਿਲੈ = be unable to say',
     'shackle_L15_p97_p98'),

    # ─── LESSON 16: §160-§161 ────────────────────────────────────────────────────
    ('word_form', 'personal_pronouns_full_declension',
     'Full declension of personal pronouns (no special locative forms): '
     '1s.: d. ਹਉ "I"; o. ਮੈ = ਮੁਝੁ = ਮੁਝੈ "me"; poss. ਮੇਰਾ "my". '
     '2s.: d. ਤੂੰ = ਤੁ, emphatic ਤੁਹੀ = ਤੁਹੇ = ਤੁਹੋ "you"; '
     'o. ਤੁਝੁ = ਤੁਝੁ = ਤੁਝੈ = ਤੁਝੈ "you (oblique)"; poss. ਤੇਰਾ "your". '
     '1p.: d./o. ਹਮ "we/us"; poss. ਹਮਾਰਾ "our". '
     '2p.: d./o. ਤੁਮ "you/you"; poss. ਤੁਮਾਰਾ "your". '
     'So. forms in [-ai] are emphatic/stressed variants. '
     'Reflexive ਆਪੁ "self" (m. Dec. I): d./o. ਆਪੁ/ਆਪ; '
     'l. ਆਪਿ = ਆਪੇ "(by) oneself, of oneself"; a. ਆਪਹੁ "from oneself"; '
     'poss. ਆਪਣਾ = ਅਪਣਾ = ਆਪੁਣਾ "one\'s own" (translated relative to sentence subject).',
     'ਹਉ/ਮੈ/ਮੇਰਾ | ਤੂੰ/ਤੁਝੁ/ਤੇਰਾ | ਹਮ/ਹਮਾਰਾ | ਤੁਮ/ਤੁਮਾਰਾ | ਆਪਿ=ਆਪੇ / ਆਪਣਾ',
     'ਮੈ = me/to me | ਮੁਝੁ = me (oblique, stronger form) | ਆਪਿ/ਆਪੇ = by oneself | '
     'ਆਪਣਾ = one\'s own (my/your/his depending on subject)',
     'shackle_L16_p101'),

    ('word_form', 'demonstrative_pronoun_locative_full_paradigm',
     'Demonstrative/relative pronouns have locative case: '
     'sl. form 1: [-t-] infix → ਇਤੁ, ਏਤੁ = ਐਤੁ (this, loc.); ਉਤੁ, ਓਤੁ (that, loc.). '
     'sl. form 2 (agentive): [-n-] infix → ਇਨਿ, ਏਨਿ; ਉਨਿ, ਓਨਿ. '
     'pl. locative: always [-nhīṃ] → ਇਨੀਂ, ਏਨੀਂ; ਉਨੀਂ, ਓਨੀਂ. '
     'Full ਇਹੁ/ਏਹੁ "this" paradigm: '
     'sd. m. ਇਹੁ/ਏਹੁ; f. ਇਹ/ਏਹ; so. ਇਸੁ/ਏਸੁ; sl. ਇਤੁ/ਏਤੁ; sl.(ag.) ਇਨਿ/ਏਨਿ; '
     'sa. ਏਦੂੰ; pd. ਇਹਿ/ਏਹਿ; po. ਇਨ=ਇਨਾ/ਏਨਾ; pl. ਇਨੀਂ/ਏਨੀਂ. '
     'Full ਉਹੁ/ਓਹੁ "that/he/she" paradigm: '
     'sd. m. ਉਹੁ/ਓਹੁ; f. ਉਹ/ਓਹ; so. ਉਸੁ/ਓਸੁ; sl. ਉਤੁ/ਓਤੁ; sl.(ag.) ਉਨਿ/ਓਨਿ; sa. ਓਦੂੰ.',
     'ਇਤੁ=ਏਤੁ / ਇਨਿ=ਏਨਿ / ਇਨੀਂ | ਉਤੁ=ਓਤੁ / ਉਨਿ=ਓਨਿ',
     'ਇਤੁ = in this (locative of ਇਹੁ) | ਇਨਿ = by this one (agentive locative) | '
     'ਉਨਿ ਕੀਤਾ = he/she did (agentive, ergative sense) | ਇਨੀਂ = in/among these (pl. loc.)',
     'shackle_L16_p102'),
]

cur.executemany('''
    INSERT INTO grammar_rules (category, pattern, meaning, example_word, example_meaning, source)
    VALUES (?, ?, ?, ?, ?, ?)
''', rules)

conn.commit()
print(f'Added {len(rules)} rules')
cur.execute('SELECT COUNT(*) FROM grammar_rules')
print(f'Total grammar_rules: {cur.fetchone()[0]}')
