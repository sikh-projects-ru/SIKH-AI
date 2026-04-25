import sqlite3
conn = sqlite3.connect('ksd_knowledge.db')
cur = conn.cursor()

rules = [
    # ─── LESSON 12: §120-§123 ───────────────────────────────────────────────────
    ('word_form', 'ablative_case_formation',
     'Ablative case (a.) = alternative to oblique + postposition [te] "from". '
     'Formed only from singular nouns by adding [-amhu] to the oblique stem. '
     'Not all declensions have sa. forms — adjectives have NO ablative. '
     'Declension I (sd. in [-u]): sa. in [-amhu]: ਭੈੜੁ → ਭੈੜਹੁ "from a vessel". '
     'Declension II (sd. in [-ā]): sa. in [-iamhu]: ਉਆ → ਉਇਅਹੁ "from water". '
     'Declension IV f. (sd. in [-a]): sa. in [-amhu] or [-aum]: ਜੀਭ → ਜੀਭਹੁ = ਜੀਭੈ "from the tongue". '
     'Pronominal sa.: special suffix [-dum]: ਏਹੁ → ਏਦੂੰ "from this"; ਇਕੁ → ਇਕਦੂੰ "from one".',
     'ਭੈੜਹੁ / ਉਇਅਹੁ / ਜੀਭਹੁ=ਜੀਭੈ / ਏਦੂੰ / ਇਕਦੂੰ',
     'ਭੈੜਹੁ = from a vessel | ਉਇਅਹੁ = from water | ਜੀਭਹੁ/ਜੀਭੈ = from the tongue | '
     'ਏਦੂੰ = from this (pronominal sa.) | ਇਕਦੂੰ = from one',
     'shackle_L12_p78'),

    ('principle', 'ablative_functions_from_than',
     'Ablative case (a.) or oblique + [te] expresses: '
     '(1) English "from" — source, separation, origin; '
     '(2) English "than" for comparison — SLS has NO comparative/superlative forms of adjectives. '
     'Comparison is expressed only with ablative or [te]: '
     '"X ਤੇ ਵੱਡਾ ਨਾਹੀ ਕੋਇ" = there is no one greater than X. '
     'Thus ablative + negation is the standard SLS comparatives pattern.',
     'ਤੁਝ ਤੇ ਵੱਡਾ ਨਾਹੀ ਕੋ',
     'ਤੁਝ ਤੇ ਵੱਡਾ ਨਾਹੀ ਕੋ = there is no one greater than you (ablative/[te] = than)',
     'shackle_L12_p79'),

    ('word_form', 'ablative_adverbs_amhu',
     'Ablative ending [-amhu] is commonly added to locative adverbs, creating distinct '
     '"from inside/outside" meanings: '
     'ਅੰਦਰਿ (inside) → ਅੰਦਰਹੁ "from inside"; '
     'ਬਾਹਰਿ (outside) → ਬਾਹਰਹੁ "from outside"; '
     'ਵਿਚਿ (in, inside) → ਵਿਚਹੁ "from within, from inside". '
     'Note: ਬਾਝੁ = ਬਾਝਹੁ "without" — [-amhu] here does NOT add ablative sense. '
     'Similarly ਵਿਟਹੁ "(sacrificed) to" — no ablative meaning despite ending.',
     'ਅੰਦਰਿ / ਅੰਦਰਹੁ | ਬਾਹਰਿ / ਬਾਹਰਹੁ | ਵਿਚਿ / ਵਿਚਹੁ | ਬਾਝੁ=ਬਾਝਹੁ | ਵਿਟਹੁ',
     'ਅੰਦਰਹੁ = from inside | ਬਾਹਰਹੁ = from outside | ਵਿਚਹੁ = from within | '
     'ਬਾਝੁ/ਬਾਝਹੁ = without (no ablative sense) | ਵਿਟਹੁ = sacrificed to (no ablative sense)',
     'shackle_L12_p79'),

    ('word_class', 'emphatics_hi_bhi_tam',
     'SLS has three enclitic emphatics — they cannot start a sentence, always follow '
     'the word they emphasize: '
     '[hī] "just, only" — the commonest; may represent any kind of emphasis; '
     '[bhī] = [bi] "also, even"; '
     '[tāṃ] = [tā] "but, on the other hand" — distinguished from CORRELATIVE [tāṃ] "then" (§072) '
     'which CAN stand first. '
     'Pronouns often followed by [hī]; 2s. direct + [hī] = ਤੁਹੀ "you (just you, only you)".',
     '...ਹੀ / ...ਭੀ=...ਬਿ / ...ਤੈ=...ਤ | ਤੁਹੀ',
     '...ਹੀ = just, only (enclitic) | ...ਭੀ = also, even | ...ਤੈ = but, on the other hand | '
     'ਤੁਹੀ = you (only you) | ਘਰ ਮਾਹਿ = in the house vs ਘਰ ਹੀ ਮਾਹਿ = in the very house',
     'shackle_L12_p80'),

    # ─── LESSON 13: §130-§133 ───────────────────────────────────────────────────
    ('word_form', 'future_tense_s_form',
     'S-future: stems + [-s-] prefix to present endings. Much less common than present. '
     'Consonant-stem paradigm (ਕਰਿ "do"): '
     '1s. + [-sāṃ] ਕਰਸਾ; 2s. + [-samhi] ਕਰਸਹਿ; 3s. + [-sī] ਕਰਸੀ; '
     '1p. + [-samhā] ਕਰਸਹਾ; 2p. + [-sahu] ਕਰਸਹੁ; '
     '3p. + [-sanhi] ਕਰਸਨਿ or + [-samhi] ਕਰਸਹਿ. '
     'Vowel-stems: endings added directly (no [-v-] insertion). '
     'Key: 3s. [-sī] contrasts with present 3s. [-ai]/[-e] — main way to spot S-future in verse. '
     'Gender-invariant (same forms for m. and f. throughout).',
     'ਕਰਸਾ / ਕਰਸਹਿ / ਕਰਸੀ / ਕਰਸਹਾ / ਕਰਸਹੁ / ਕਰਸਨਿ',
     'ਕਰਸੀ = he/she will do (3s. S-future; cf. present ਕਰੈ) | '
     'ਹੋਸੀ = he/she will be (3s. S-future of ਹੋਇ)',
     'shackle_L13_p83'),

    ('word_form', 'future_tense_g_form',
     'G-future: present personal form + inflected suffix [-gā] (m.) / [-gī] (f.). '
     'Unlike S-future, G-future inflects for GENDER. '
     'Key endings: 1s. m. [-aumgā] ਕਰੌਂਗਾ, f. [-aumgī] ਕਰੌਂਗੀ; '
     '2s. m. [-amhigā] ਕਰਹਿਗਾ; 3s. m. [-aigā] ਕਰੈਗਾ, f. [-aigī] ਕਰੈਗੀ; '
     '2p. m. [-ahuge] ਕਰਹੁਗੇ; 3p. m. [-amhige] ਕਰਹਿਗੇ. '
     '1p. and f. of 2p./3p. not normally used. '
     'Vowel-stems: may use long forms (with [-v-]) or short forms + suffix. '
     'Special short forms for ਹੋਇ "be": 3s. m. ਹੋਗੁ, f. ਹੋਗਿ. '
     'All future types are synonymous: ਹੋਸੀ = ਹੋਵੇਗਾ = ਹੋਇਗਾ = ਹੋਗੁ "he will be".',
     'ਕਰੈਗਾ / ਕਰੈਗੀ / ਕਰਹਿਗਾ / ਕਰੌਂਗਾ | ਹੋਗੁ / ਹੋਗਿ',
     'ਕਰੈਗਾ = he will do (3s. m. G-future) | ਕਰੈਗੀ = she will do (3s. f.) | '
     'ਹੋਗੁ = he will be (short G-future, 3s. m.) | ਹੋਗਿ = she will be (3s. f.)',
     'shackle_L13_p83_p84'),

    ('word_form', 'absolutive_compounds_de_lai_jai',
     'Absolutive compounds: absolutive + auxiliary verb where auxiliary loses basic meaning '
     'and modifies direction of action: '
     '[de] "give" → action directed OUTWARD from doer: ਦੇਖਾਇ ਦੇਇ "show (outward from oneself)". '
     '[lai]/[le] "take" → action directed INWARD toward doer: ਮੇਲਿ ਲੈਇ "unite (inward, to oneself)". '
     '[jai] "go" → slight emphasis only, no direction: most common compound ਲੈ ਜਾਇ "take away". '
     'Note: [lai] normally appears as [lae] in 3s. present (§151).',
     'ਦੇਖਾਇ ਦੇਇ / ਮੇਲਿ ਲੈਇ / ਲੈ ਜਾਇ',
     'ਦੇਖਾਇ ਦੇਇ = show (outward) | ਮੇਲਿ ਲੈਇ = unite (to oneself, inward) | '
     'ਲੈ ਜਾਇ = take away ([jai] adds emphasis)',
     'shackle_L13_p84_p85'),

    ('principle', 'conditional_clauses_je_tam',
     'Conditional clauses introduced by [je] "if"; main clause introduced by correlative '
     '[tāṃ] or [tā] "then". '
     'Same correlative structure as relative clauses (§072-073). '
     '[je] may be omitted — same as [jo] in relative clauses: '
     '"ਸਤਿਗੁਰੁ ਮਿਲੈ, ਤ ਸੋਝੀ ਹੋਇ" = [if] Satiguru meets (one), then there is awareness. '
     'Distinguish: enclitic [tāṃ/tā] "but, on the other hand" (§123) cannot start a clause; '
     'correlative [tāṃ] "then" CAN start a clause.',
     'ਜੇ...ਤਾਂ=ਤ | ਸਤਿਗੁਰੁ ਮਿਲੈ ਤ ਸੋਝੀ ਹੋਇ',
     'ਜੇ ਤੂੰ ਦੇਹਿ ਤ ਹਰਿ ਰਸੁ ਰਾਈ = if You give, then [I have] the essence of God | '
     'ਸਤਿਗੁਰੁ ਮਿਲੈ ਤ ਸੋਝੀ ਹੋਇ = [if] Satiguru meets, then awareness (je omitted)',
     'shackle_L13_p85'),
]

cur.executemany('''
    INSERT INTO grammar_rules (category, pattern, meaning, example_word, example_meaning, source)
    VALUES (?, ?, ?, ?, ?, ?)
''', rules)

conn.commit()
print(f'Added {len(rules)} rules')
cur.execute('SELECT COUNT(*) FROM grammar_rules')
print(f'Total grammar_rules: {cur.fetchone()[0]}')
