import sqlite3
conn = sqlite3.connect('ksd_knowledge.db')
cur = conn.cursor()

# Source: C. Shackle, "An Introduction to the Sacred Language of the Sikhs"
# SOAS / Heritage Publishers, 1982 (repr. 1999)
# Confidence note: HIGH for morphology/paradigms/syntax (SGGS-specific, academic)
#                  MEDIUM for phonology (transliteration with macrons, not live pronunciation)
# Source tag: shackle_L[lesson]_p[book-page]

rules = [
    # ─── FOUNDATIONAL PRINCIPLE (Part I p.7 + Lesson 1 §010) ───────────────
    ('principle', 'sls_final_vowel_determines_declension',
     'All SLS words end in a vowel (unlike modern Punjabi where final vowels are dropped). '
     'The final vowel of the singular direct case (sd.) determines both the declension class '
     'and is a guide to gender. Must be noted when a noun is first introduced. '
     'Most grammatical endings are vowels — this is the foundation of Gurbani parsing.',
     'ਘਰੁ / ਘਰਾ / ਘਰਿ',
     'ਘਰੁ [gharu] house (sd., aungkar) | ਘਰਾ [ghara] houses (pd.) | ਘਰਿ [ghari] in the house (locative) — '
     'three different words in English, three vowel endings in SLS',
     'shackle_L01_p7_p18'),

    # ─── §010 GENDER ────────────────────────────────────────────────────────
    ('gender', 'sls_noun_gender_two_classes',
     'SLS nouns assigned to masculine (m.) or feminine (f.) gender. '
     'Gender of personal nouns follows natural gender; all others determined historically '
     'and must be learnt for each noun.',
     'ਸਾਹਿਬੁ (m.) / ਦਾਤਾ (m.) / ਨਾਮੁ (m.)',
     'Gender cannot be predicted from meaning alone for non-personal nouns; '
     'final vowel of sd. gives clue to declension class within gender',
     'shackle_L01_p18'),

    # ─── §011 MASCULINE NOUN DECLENSIONS (sd.) ──────────────────────────────
    ('number', 'masculine_noun_decl_I_sd_aungkar',
     'Masculine noun declension I: singular direct (sd.) ends in [-u] (aungkar). '
     'Most common declension in SLS. The [-u] may sometimes be lengthened to [-o] '
     'for slight emphasis.',
     'ਨਾਮੁ, ਥਾਉ, ਸੰਸਾਰੁ=ਸੰਸਾਰੋ',
     'ਨਾਮੁ [namu] name | ਥਾਉ [thau] place | ਸੰਸਾਰੁ=ਸੰਸਾਰੋ world ([-o] = emphatic lengthening)',
     'shackle_L01_p18'),

    ('number', 'masculine_noun_decl_II_sd_kanna',
     'Masculine noun declension II: singular direct (sd.) ends in [-ā] (kanna). '
     'Second most common masculine declension. Typical for agent nouns.',
     'ਦਾਤਾ, ਕਰਤਾ',
     'ਦਾਤਾ [data] giver | ਕਰਤਾ [karta] creator — these end in kanna (long a)',
     'shackle_L01_p18'),

    ('number', 'masculine_noun_decl_III_sd_bihari_or_sihari',
     'Masculine noun declension III: sd. most commonly in [-ī] (bihari); '
     'a few also in [-i] (sihari) or [-ū] (long u). Less common than decl I and II. '
     'Note: same form can be noun or adjective (distinction less marked in SLS than English).',
     'ਪਾਪੀ, ਗੁਰੂ',
     'ਪਾਪੀ [papi] sinner (m. decl III, sd. in bihari) | '
     'ਗੁਰੂ [guru] guru (m. decl III, sd. in long u)',
     'shackle_L01_p19'),

    # ─── §012 ADJECTIVES ────────────────────────────────────────────────────
    ('word_class', 'adjective_three_declensions_agree_with_noun',
     'Adjectives follow same 3 declensions as nouns. Form used depends on gender and case '
     'of noun with which adjective agrees. Masculine singular direct (msd.) ending '
     'determines declension class. Distinction between noun and adjective less marked in SLS.',
     'ਨਿਰਮਲੁ (I), ਸਚਾ=ਸਾਚਾ (II), ਪਾਪੀ (III)',
     'ਨਿਰਮਲੁ pure (msd. decl I, [-u]) | ਸਚਾ=ਸਾਚਾ true (msd. decl II, [-ā]) | '
     'ਪਾਪੀ sinful (msd. decl III, [-ī]) — adjective precedes noun it qualifies',
     'shackle_L01_p19'),

    # ─── §013 PRONOUNS ──────────────────────────────────────────────────────
    ('word_class', 'pronouns_sd_1p_2p_3p',
     '1st/2nd person pronouns in sd.: ਹਉ (I), ਤੂੰ=ਤੁ (you/Thou). '
     'No true 3rd person pronoun — demonstrative ਸੋ=ਸੁ (that; he/it) used instead. '
     'Emphatic extended forms: ਸੋਈ=ਸੋਇ (that very one; he/it). '
     'Indefinite: ਕੋ=ਕੋਈ=ਕੋਇ (some, any, someone).',
     'ਹਉ, ਤੂੰ=ਤੁ, ਸੋ=ਸੁ, ਸੋਈ=ਸੋਇ, ਕੋ=ਕੋਈ=ਕੋਇ',
     'ਹਉ ਪਾਪੀ I [am] a sinner | ਸੋ ਦਰੁ ਤੇਰਾ that door [is] yours | '
     'ਨਾਹੀ ਕੋਈ [there is] no one',
     'shackle_L01_p20'),

    ('word_class', 'pronouns_sd_demonstrative_other',
     'Other common sd. pronouns typically in [-u]: '
     'ਇਹੁ=ਏਹੁ (this), ਸਭੁ (all, every), ਇਕੁ=ਏਕੁ (one), ਅਵਰੁ=ਹੋਰੁ (other, else). '
     'Form in [-o] implies slightly greater emphasis: ਏਕੋ = just one (exclusive).',
     'ਇਹੁ=ਏਹੁ, ਸਭੁ, ਇਕੁ=ਏਕੁ, ਅਵਰੁ=ਹੋਰੁ, ਏਕੋ',
     'ਏਕੋ = just one (emphatic, [-o] lengthening) | ਇਕੁ=ਏਕੁ = one | '
     'ਸਭੁ = all/every | ਅਵਰੁ=ਹੋਰੁ = other/else',
     'shackle_L01_p20'),

    ('word_form', 'reflexive_aapi_all_persons_shackle',
     'Reflexive pronoun ਆਪਿ=ਆਪੇ has same form for all persons (1s/2s/3s); '
     'meaning (myself/yourself/himself) determined by the subject of the sentence.',
     'ਆਪਿ = ਆਪੇ',
     'ਦਾਤਾ ਕਰਤਾ ਆਪਿ ਤੂੰ = Giver, Creator, You Yourself | '
     'meaning shifts: I myself / you yourself / he himself — same form',
     'shackle_L01_p21'),

    # ─── §014 SYNTAX ────────────────────────────────────────────────────────
    ('principle', 'sls_syntax_no_copula_no_article_word_order',
     'Three key SLS syntax features: (1) No copula — no word for "am/is/are" in simple sentences; '
     '(2) No definite article — "the" must be supplied in translation; '
     '(3) Free word order in verse — subject normally first but poetic inversions very common. '
     'ਏਕੁ=ਇਕੁ sometimes overlaps with indefinite article "a/an" but must usually be supplied.',
     'ਤੇਰਾ ਨਾਮੁ ਸਚਾ / ਸਾਹਿਬੁ ਸਚਾ',
     'ਤੇਰਾ ਨਾਮੁ ਸਚਾ = your name [is] true | '
     'ਸਾਹਿਬੁ ਸਚਾ = [the] Lord [is] true | '
     'ਸਚਾ ਤੇਰਾ ਨਾਮੁ = true [is] your name (inverted, same meaning)',
     'shackle_L01_p21'),

    # ─── §015 NEGATION ──────────────────────────────────────────────────────
    ('word_form', 'negation_four_variant_forms',
     'Negative adverb "not" has four variant forms in SLS: ਨ = ਨਾ = ਨਹੀ = ਨਾਹੀ. '
     'Due to absent copula, these also cover "am/is/are not" and "there is/are not".',
     'ਨ = ਨਾ = ਨਹੀ = ਨਾਹੀ',
     'ਨਾ ਕੋ ਮੇਰਾ = [there is] not anyone of mine | '
     'ਨਾਹੀ ਕੋਈ = [there is] no one | '
     'ਅਵਰੁ ਨ ਦੂਜਾ = [there is] no other [n]or second',
     'shackle_L01_p22'),

    # ─── LESSON 2: §020 MASCULINE PLURAL DIRECT ─────────────────────────────
    ('number', 'masculine_noun_plural_direct_formation',
     'Masculine plural direct (pd.) formation by declension: '
     'Decl I [-u] → pd. [-a] (aungkar→kanna); '
     'Decl I special [-āmu/ura] → pd. [-āmva/aira] (ura→aira bearer change); '
     'Decl II [-ā] → pd. [-e] (kanna→lam); '
     'Decl III [-ī]: no change — context or adjective agreement shows plural.',
     'ਸਹੁ→ਸਹਾ, ਨਾਉ→ਨਾਵ, ਜੀਉ→ਜੀਅ, ਰਾਜਾ→ਰਾਜੇ, ਪਾਪੀ→ਪਾਪੀ',
     'ਸਹੁ lord → ਸਹਾ lords | ਗੁਣੁ virtue → ਗੁਣਾ virtues | '
     'ਨਾਉ name → ਨਾਵ names | ਥਾਉ place → ਥਾਵ places | '
     'ਜੀਉ soul → ਜੀਅ creatures | '
     'ਰਾਜਾ king → ਰਾਜੇ kings | ਦਾਤਾ → ਦਾਤੇ givers | '
     'ਪਾਪੀ sinner/sinners (same form sg/pl, decl III)',
     'shackle_L02_p25'),
]

cur.executemany('''
    INSERT INTO grammar_rules (category, pattern, meaning, example_word, example_meaning, source)
    VALUES (?, ?, ?, ?, ?, ?)
''', rules)

conn.commit()
print(f'Added {len(rules)} rules')
cur.execute('SELECT COUNT(*) FROM grammar_rules')
print(f'Total grammar_rules: {cur.fetchone()[0]}')
