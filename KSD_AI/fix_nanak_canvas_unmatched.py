#!/usr/bin/env python3
"""Fix the 11 unmatched Nanak Canvas concept lines so export resolves verse_id.

KSD-only: touches canvas_concepts.gurbani_ref and ksd_examples for Nanak Canvas
concepts. Does NOT touch Sahib Singh or any sggs-reader translation data.

Root cause was almost always an ang typo in the source markup (and two snippets
that captured the Mehla author tag instead of the cited line). All targets are
verified against ksd_ang_json/ before and after. Idempotent: re-running is a
no-op once the values already hold the corrected form.
"""

import importlib.util
import json
import os
import sqlite3

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, "ksd_knowledge.db")

spec = importlib.util.spec_from_file_location("exp", os.path.join(ROOT, "export_ksd_concepts.py"))
exp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exp)
strip = exp.strip_gurmukhi
head = exp.gurmukhi_head

# ksd_examples row fixes: id -> (new_ang_or_None, new_gurmukhi_or_None, expected_verse_id)
EXAMPLE_FIXES = {
    722: (484, None, 21787),   # Применение: ang typo 474->484
    719: (969, None, 41461),   # Применение: ang typo 1370->969
    720: (917, "ਪੰਚ ਦੂਤ ਤੁਧੁ ਵਸਿ ਕੀਤੇ ਕਾਲੁ ਕੰਟਕੁ ਮਾਰਿਆ ॥", 39153),  # Применение
    435: (969, None, 41461),   # concepts_sikhi kavan-narak: ang typo 696->969
    692: (None, "ਜਿਸ ਕੈ ਘਰਿ ਦੀਬਾਨੁ ਹਰਿ ਹੋਵੈ ਤਿਸ ਕੀ ਮੁਠੀ ਵਿਚਿ ਜਗਤੁ ਸਭੁ ਆਇਆ ॥", 25784),  # Дарга: ਜਿਸੁ->ਜਿਸ
    691: (None, "ਖਰੇ ਪਰਖਿ ਖਜਾਨੈ ਪਾਈਅਨਿ ਖੋਟਿਆ ਨਾਹੀ ਥਾਉ ॥", 46700),  # Дарга: fragment -> real line
    673: (291, None, 13243),   # Рай и ад: ang typo 295->291 (couplet head)
    648: (None, "ਫਰੀਦਾ ਉਮਰ ਸੁਹਾਵੜੀ ਸੰਗਿ ਸੁਵੰਨੜੀ ਦੇਹ ॥ ਵਿਰਲੇ ਕੇਈ ਪਈਅਨਿੑ ਜਿਨੑਾ ਪਿਆਰੇ ਨੇਹ ॥", 41315),  # Смерть: drop Mehla tag, book line
    650: (None, "ਇਕ ਦਝਹਿ ਇਕ ਦਬੀਅਹਿ ਇਕਨਾ ਕੁਤੇ ਖਾਹਿ ॥ ਇਕਿ ਪਾਣੀ ਵਿਚਿ ਉਸਟੀਅਹਿ ਇਕਿ ਭੀ ਫਿਰਿ ਹਸਣਿ ਪਾਹਿ ॥ ਨਾਨਕ ਏਵ ਨ ਜਾਪਈ ਕਿਥੈ ਜਾਇ ਸਮਾਹਿ ॥੨॥", 28043),  # Жизнь после смерти
}

# canvas_concepts.gurbani_ref fixes: concept_id -> [(old_token, new_token), ...]
REF_FIXES = {
    67: [("СГГС 474:", "СГГС 484:"), ("СГГС 696:", "СГГС 969:")],
    68: [("СГГС 467:", "СГГС 437:")],
}


def load_corpus_index():
    index = {}
    corpus_dir = os.path.join(ROOT, "ksd_ang_json")
    for name in os.listdir(corpus_dir):
        if not name.startswith("ksd_ang_") or not name.endswith(".json"):
            continue
        d = json.load(open(os.path.join(corpus_dir, name)))
        for sh in d.get("shabads", []):
            for ln in sh.get("lines", []):
                index[ln.get("verse_id")] = (d["ang"], strip(ln.get("gurmukhi", "")))
    return index


def main():
    corpus = load_corpus_index()
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row

    print("=== ksd_examples ===")
    for rid, (new_ang, new_gur, vid) in EXAMPLE_FIXES.items():
        row = db.execute("SELECT ang, gurmukhi FROM ksd_examples WHERE id=?", (rid,)).fetchone()
        if row is None:
            print(f"  id={rid}: ROW MISSING — skipped")
            continue
        ang = new_ang if new_ang is not None else row["ang"]
        gur = new_gur if new_gur is not None else row["gurmukhi"]
        db.execute("UPDATE ksd_examples SET ang=?, gurmukhi=? WHERE id=?", (ang, gur, rid))
        # verify head resolves to expected verse_id on the target ang
        c_ang, c_key = corpus.get(vid, (None, None))
        ok = c_ang == ang and strip(head(gur)) and (strip(head(gur)) in c_key or c_key.startswith(strip(head(gur))[:8]))
        print(f"  id={rid:>4} ang->{ang} verse_id={vid} {'OK' if ok else 'CHECK!'}")

    print("=== canvas_concepts.gurbani_ref ===")
    for cid, repls in REF_FIXES.items():
        row = db.execute("SELECT gurbani_ref FROM canvas_concepts WHERE id=?", (cid,)).fetchone()
        ref = row["gurbani_ref"]
        for old, new in repls:
            if old in ref:
                ref = ref.replace(old, new)
                print(f"  concept {cid}: '{old}' -> '{new}'")
            elif new in ref:
                print(f"  concept {cid}: '{new}' already applied")
            else:
                print(f"  concept {cid}: token '{old}' NOT FOUND — CHECK!")
        db.execute("UPDATE canvas_concepts SET gurbani_ref=? WHERE id=?", (ref, cid))

    db.commit()
    db.close()
    print("done.")


if __name__ == "__main__":
    main()
