import sqlite3
conn = sqlite3.connect('ksd_knowledge.db')
cur = conn.cursor()

# Source: C. Shackle, "An Introduction to the Sacred Language of the Sikhs"
# SOAS / Heritage Publishers, 1982 (repr. 1999)
# Confidence: HIGH for morphology/paradigms/syntax
# Source tag: shackle_L[lesson]_p[book-page]

rules = [
    # ─── LESSON 3: §030 FEMININE NOUN DECLENSIONS ────────────────────────────
    ('number', 'feminine_noun_decl_IV_sd_kanna',
     'Feminine noun declension IV: sd. in [-a] (kanna). Quite common f. declension. '
     'pd. in [-āṃ] (nasalised lengthening of final vowel — pattern shared by decl IV, V, VI).',
     'ਗਲ',
     'ਗਲ [gal] thing (sd.) → ਗਲਾਂ [galāṃ] things (pd.)',
     'shackle_L03_p30'),

    ('number', 'feminine_noun_decl_V_sd_sihari',
     'Feminine noun declension V: sd. in [-i] (sihari). One of the two commonest f. declensions. '
     'pd. in [-īṃ] (nasalised long i).',
     'ਸੋਹਣਿ',
     'ਸੋਹਣਿ [sohaṇ] married woman (sd.) → ਸੋਹਣੀਂ [sohaṇīṃ] married women (pd.)',
     'shackle_L03_p30'),

    ('number', 'feminine_noun_decl_VI_sd_aungkar',
     'Feminine noun declension VI: sd. in [-u] (aungkar). '
     'Only a few f. nouns have this form — since [-u] is the characteristic m. decl I ending, '
     'assignment to this f. declension must be learnt per word. pd. in [-ūṃ].',
     'ਵਸਤੁ',
     'ਵਸਤੁ [vastu] thing (sd.) → ਵਸਤੂੰ [vastūṃ] things (pd.)',
     'shackle_L03_p30'),

    ('number', 'feminine_noun_decl_VII_sd_bihari',
     'Feminine noun declension VII: sd. in [-ī] (bihari). Together with V, one of the two '
     'commonest f. declensions. pd. in [-īāṃ] (bihari + kanna + nasalisation).',
     'ਵਡਿਆਈ',
     'ਵਡਿਆਈ [vaḍiāī] glory (sd.) → ਵਡਿਆਈਆਂ [vaḍiāīāṃ] glories (pd.)',
     'shackle_L03_p30'),

    ('number', 'feminine_noun_decl_VIII_other',
     'Feminine noun declension VIII: other f. nouns, nearly all with sd. in [-ā] (long). '
     'Many are abstract nouns; pd. forms are not normally encountered. '
     'Must be learnt individually — [-ā] here is f., unlike m. decl II.',
     'ਦੁਨੀਆ, ਮਾਇਆ',
     'ਦੁਨੀਆ [dunīā] the world (f., decl VIII) | ਮਾਇਆ [māiā] maya (f., decl VIII)',
     'shackle_L03_p30'),

    # ─── §031 ADJECTIVE AGREEMENT (FEMININE) ─────────────────────────────────
    ('word_class', 'adjective_decl_AI_fsd_fpd',
     'Adjective declension AI (msd. in [-u]): mpd. = fsd. = fpd. all in [-a] (kanna). '
     'No lengthening of final vowel in fpd. — unlike f. noun decl IV. '
     'Single form serves masculine plural, feminine singular, and feminine plural.',
     'ਨਿਰਮਲੁ',
     'ਨਿਰਮਲੁ (msd.) = ਨਿਰਮਲ (mpd./fsd./fpd.) pure — four cases, one non-masculine form',
     'shackle_L03_p31'),

    ('word_class', 'adjective_decl_AII_fsd_fpd',
     'Adjective declension AII (msd. in [-ā]): mpd. in [-e]; fsd. in [-ī]; fpd. in [-īāṃ]. '
     'The commonest adjectival declension; fsd./fpd. correspond exactly to f. noun decl VII.',
     'ਸਚਾ=ਸਾਚਾ',
     'ਸਚਾ (msd.) → ਸਚੇ (mpd.) → ਸਚੀ (fsd.) → ਸਚੀਆਂ (fpd.) true',
     'shackle_L03_p31'),

    ('word_class', 'adjective_decl_III_no_gender_change',
     'Adjective declension III (msd. in [-ī]): no change for fsd. or fpd. — single form for all. '
     'Includes decl III nouns used adjectivally. Pattern: no gender agreement marking.',
     'ਪਾਪੀ',
     'ਪਾਪੀ sinful — same form for msd., fsd., mpd., fpd.',
     'shackle_L03_p31'),

    # ─── §032 PRONOUNS (FEMININE SINGULAR / PLURAL) ───────────────────────────
    ('word_class', 'pronoun_decl_I_gender_forms',
     'Pronoun declension I: msd. in [-o]; fsd. in [-ā]; pd. in [-e] (common gender). '
     'ਸੋ=ਸੁ (that/he) → ਸਾ (that/she) → ਸੇ=ਸਿ=ਤੇ (those/they). '
     'ਏਕੋ (just one m.) → ਏਕਾ (just one f.). '
     'Extended forms: ਸੋਈ (that very/he) → ਸਾਈ (that very/she) → ਸੇਈ (those very/they). '
     'ਕੋਈ (someone m.) → ਕਾਈ (someone f.).',
     'ਸੋ=ਸੁ / ਸਾ / ਸੇ=ਸਿ=ਤੇ',
     'ਸੋ (he/that) → ਸਾ (she/that) → ਸੇ (they/those) | ਏਕੋ → ਏਕਾ | ਸੋਈ → ਸਾਈ → ਸੇਈ | ਕੋਈ → ਕਾਈ',
     'shackle_L03_p32'),

    ('word_class', 'pronoun_decl_II_gender_forms',
     'Pronoun declension II: msd. in [-u]; fsd. in [-a]; pd. in [-a] or [-i]. '
     'Similar to adjective decl AI but with special plural forms. '
     'ਏਹੁ/ਇਹੁ (this m.) → ਏਹ (this f.) → ਏਹ=ਏਹਿ (these). '
     'ਸਭੁ (all m.) → ਸਭ (all f.) → ਸਭ=ਸਭਿ (all). '
     'ਹੋਰੁ (other m.) → ਹੋਰ → ਹੋਰ=ਹੋਰਿ (others). '
     'ਕਉਣੁ (which?) → ਕਉਣ → ਕਉਣ=ਕਉਣਿ. '
     'ਇਕੁ=ਏਕੁ (one m.) → ਇਕ (one f.) → ਇਕਿ (some).',
     'ਏਹੁ / ਏਹ / ਏਹ=ਏਹਿ',
     'ਏਹੁ (this m.) → ਏਹ (this f.) → ਏਹਿ (these) | ਸਭੁ → ਸਭ → ਸਭਿ | ਇਕੁ → ਇਕ → ਇਕਿ',
     'shackle_L03_p32'),

    # ─── LESSON 4: §040-§045 VERBS ────────────────────────────────────────────
    ('word_class', 'verb_consonant_vs_vowel_stem',
     'SLS verbs classified by stem type. Consonant-stems end in consonant; '
     'vowel-stems end in a long vowel. The stem itself rarely occurs alone — it is a '
     'grammatical abstraction. All inflected forms are built on the stem.',
     'ਜਾਣਿ [jāṇ-], ਆਖਿ [ākh-] / ਆਇ [ā-], ਜਾਇ [jā-]',
     'Consonant-stems: [jāṇ-] know, [ākh-] say | Vowel-stems: [ā-] come, [jā-] go, [ho-] be',
     'shackle_L04_p35'),

    ('word_form', 'absolutive_formation',
     'Absolutive (abs.): the simplest common form of the verb, used as reference form. '
     'Consonant-stems: abs. = stem + [-i]. '
     'Vowel-stems with [-ā], [-o]: add [-i] → abs. ends in [-āi] or [-oi]. '
     'Vowel-stems ending in [-ī], [-e], [-ai]: absolutive is identical to the stem (no [-i] added).',
     'ਕਰਿ, ਆਇ, ਜਾਇ, ਹੋਇ, ਪੀ, ਦੇ, ਲੈ',
     'ਕਰਿ [kari] do (consonant-stem [kar-]+[-i]) | ਆਇ come | ਜਾਇ go | ਹੋਇ be | '
     'ਪੀ drink (vowel-stem [-ī], abs.=stem) | ਦੇ give ([-e]) | ਲੈ take ([-ai])',
     'shackle_L04_p35_p36'),

    ('word_form', 'present_tense_consonant_stem_endings',
     'Present tense of consonant-stems: personal endings added to stem. '
     '1s.: +[-āṃ]/(ਹਉ)ਕਰਾਂ, or +[-īṃ]ਕਰੀਂ, or +[-auṃ]ਕਰਉ. '
     '2s.: +[-amhi](ਤੂੰ)ਕਰਹਿ. '
     '3s.: +[-ai](ਸੋ)ਕਰੈ, or +[-e]ਕਰੇ ([-e] more frequent for [-r]-stems like [kar-]). '
     '1p.: +[-amha](ਹਮ)ਕਰਹੁ. 2p.: +[-ahu](ਤੁਮ)ਕਰਹੁ. '
     '3p.: +[-anhi](ਸੋ)ਕਰਨਿ, or +[-amhi]ਕਰਹਿ. No gender distinction in this tense.',
     'ਕਰਾਂ=ਕਰੀਂ=ਕਰਉ / ਕਰਹਿ / ਕਰੈ=ਕਰੇ / ਕਰਹੁ / ਕਰਨਿ=ਕਰਹਿ',
     'ਕਰਾਂ (1s.) | ਕਰਹਿ (2s.) | ਕਰੈ/ਕਰੇ (3s.) | ਕਰਹੁ (1p./2p.) | ਕਰਨਿ/ਕਰਹਿ (3p.) — stem [kar-] do/make',
     'shackle_L04_p36_p37'),

    ('principle', 'present_tense_wide_senses',
     'SLS present tense covers a wide range of English senses: simple present ("I do"), '
     'subjunctive ("let me do", "I should do"), conditional ("I would do"), future ("I will do"), '
     'interrogative ("do I?", "may I?", "shall I?"). '
     'No special marks distinguish these — context determines sense. '
     'Subject pronoun often omitted; person inferred from verb ending.',
     'ਕਿਆ ਮਾਗਉ',
     'ਕਿਆ ਮਾਗਉ = what shall [I] ask for? / what should [I] ask? (subject ਹਉ implied by -auṃ ending)',
     'shackle_L04_p37_p38'),

    ('principle', 'transitive_object_direct_case',
     'Direct object of transitive verbs placed in the direct case (same form as subject). '
     'Normal order subject→object→verb, but SLS poetic word order is very free; '
     'sense determined by context, not word position.',
     'ਸਚੁ ਕਹੈ ਨਾਨਕੁ',
     'ਸਚੁ ਕਹੈ ਨਾਨਕੁ = truth/tells/Nanak → sense must be "Nanak tells the truth" from context',
     'shackle_L04_p38'),

    ('word_form', 'negative_present_na_before_verb',
     'Negative of present tense: [na] placed immediately before the verb. '
     'Alternative forms (ਨ=ਨਾ=ਨਹੀ=ਨਾਹੀ) not usually used with present tense — mainly [na]. '
     'Extended present endings (052) most frequent after [na].',
     'ਨਾਮੁ ਨ ਵੀਸਰੈ',
     'ਨਾਮੁ ਨ ਵੀਸਰੈ = the name is not forgotten ([na] + 3s.)',
     'shackle_L04_p38'),

    # ─── LESSON 5: §050-§054 ABSOLUTIVE & COMPOUND VERBS ─────────────────────
    ('word_form', 'absolutive_uses_linking_verbs',
     'Absolutive primary use: links two verbs in one sentence — "having done X, [subject] does Y". '
     'Absolutive may be repeated before second verb to give sense of continual action. '
     'Used with [sakki] "be able to" (can only follow an absolutive). '
     'Used with [jāṇi] "know" → "know how to do".',
     'ਕਰਿ ਦੇਖੈ / ਕਰਿ ਕਰਿ ਦੇਖੈ / ਬੁਝਿ ਨ ਸਕੈ / ਲਿਖਿ ਨ ਜਾਣਾ',
     'ਕਰਿ ਦੇਖੈ = having made, [He] looks | ਕਰਿ ਕਰਿ ਦੇਖੈ = continual making | '
     'ਬੁਝਿ ਨ ਸਕੈ = he cannot ask (abs.+sakki) | ਲਿਖਿ ਨ ਜਾਣਾ = I do not know how to write',
     'shackle_L05_p42'),

    ('word_form', 'present_tense_vowel_stem_v_insertion',
     'Present tense of vowel-stems (long forms): [-v-] inserted between stem and personal endings. '
     'Treats vowel-stem as if it were a consonant-stem ending in [-āv], [-ev], [-īv], or [-ov]. '
     'Paradigm for [hoi] be/become (stem [ho-]): '
     '1s. ਹੋਵਾਂ/ਹੋਵੀਂ/ਹੋਵਉ, 2s. ਹੋਵਹਿ, 3s. ਹੋਵੈ (only one 3s. form for vowel-stems), '
     '1p. ਹੋਵਹੁ, 2p. ਹੋਵਹੁ, 3p. ਹੋਵਨਿ/ਹੋਵਹਿ.',
     'ਹੋਵਾਂ / ਹੋਵਹਿ / ਹੋਵੈ / ਹੋਵਹੁ / ਹੋਵਨਿ',
     'ਹੋਵੈ = he/she is (3s., only one form) | ਹੋਵਨਿ/ਹੋਵਹਿ = they are (3p.) — stem [ho-]+[-v-]+ending',
     'shackle_L05_p43'),

    ('word_form', 'present_tense_extended_forms_3s_3p',
     'Extended forms of present tense: personal endings extended to give final long vowel. '
     'Most frequent in 3s. and 3p.; most common after negative [na]. No difference in meaning. '
     '3s.: +[-āī] → ਕਰਈ (he does). 3p.: +[-anhī] → ਕਰਨੀ, or +[-amhī] → ਕਰਹੀ. '
     'Vowel-stems: 3s. ਹੋਵਈ, 3p. ਹੋਵਨੀ/ਹੋਵਹੀ. Often used for metrical convenience.',
     'ਕਰਈ / ਕਰਨੀ = ਕਰਹੀ / ਹੋਵਈ',
     'ਕਰਈ (3s. extended) | ਕਰਨੀ/ਕਰਹੀ (3p. extended) | ਹੋਵਈ (3s. vowel-stem extended)',
     'shackle_L05_p44'),

    ('word_form', 'compound_verb_kari',
     '[kari] "do, make" used with nouns and adjectives to form compound transitive verbs. '
     'Compound functions as a single verb phrase and needs composite translation into English.',
     'ਵੀਚਾਰੁ ਕਰਿ / ਕਿਰਪਾ ਕਰਿ / ਸਮ ਕਰਿ',
     'ਵੀਚਾਰੁ ਕਰਿ = make thought → think, reflect | '
     'ਕਿਰਪਾ ਕਰਿ = do mercy → be merciful | '
     'ਸਮ ਕਰਿ = make equal → consider as equal',
     'shackle_L05_p44'),

    ('principle', 'indirect_speech_no_that_conjunction',
     'SLS has no conjunction for "that" introducing indirect speech. '
     'Direct speech immediately follows verb [akhi]/[kahi] "say". '
     'Same sentence covers both direct and indirect speech readings.',
     'ਨਾਨਕੁ ਕਹੈ ਅਵਰੁ ਨਹੀ ਕੋਇ',
     'ਨਾਨਕੁ ਕਹੈ ਅਵਰੁ ਨਹੀ ਕੋਇ = Nanak says "there is no other" '
     '= Nanak says that there is no other (same words, both readings valid)',
     'shackle_L05_p45'),
]

cur.executemany('''
    INSERT INTO grammar_rules (category, pattern, meaning, example_word, example_meaning, source)
    VALUES (?, ?, ?, ?, ?, ?)
''', rules)

conn.commit()
print(f'Added {len(rules)} rules')
cur.execute('SELECT COUNT(*) FROM grammar_rules')
print(f'Total grammar_rules: {cur.fetchone()[0]}')
