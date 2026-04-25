#!/usr/bin/env python3
"""Apply manual translation patches to the app JSON without re-running GPT.

patches.json format:
  [{ "verse_id": 518, "field": "main", "old": "...", "new": "..." }, ...]

Fields: main | artistic | context_note
Run: python3 nitnem_app/apply_patches.py
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
APP_JSON = ROOT / "nitnem_mobile/app/src/main/assets/nitnem_ru_ksd_v1.json"
PATCHES  = Path(__file__).parent / "patches.json"

patches = json.loads(PATCHES.read_text())
data    = json.loads(APP_JSON.read_text(encoding="utf-8"))

index = {}  # verse_id -> translation dict
for ang in data["angs"]:
    for sh in ang["shabads"]:
        for ln in sh["lines"]:
            t = ln.setdefault("translations", {}).setdefault("ksd_ru", {})
            index[ln["verse_id"]] = t

applied = 0
for p in patches:
    vid   = p["verse_id"]
    field = p["field"]
    t = index.get(vid)
    if t is None:
        print(f"SKIP  v={vid}: verse not found")
        continue
    val = t.get(field, "") or ""
    if p["old"] not in val:
        print(f"SKIP  v={vid} [{field}]: old text not found")
        continue
    t[field] = val.replace(p["old"], p["new"], 1)
    print(f"PATCH v={vid} [{field}]: ok")
    applied += 1

APP_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nApplied {applied}/{len(patches)} patches -> {APP_JSON}")
