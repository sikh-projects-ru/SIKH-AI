# Nitnem App Planning

This folder contains the initial product and data architecture for a future
Nitnem reading app.

Decision:
- First public target: Android.
- Long-term target: Android + iOS.
- Architecture: Kotlin Multiplatform core, Android UI first.
- Content model: versioned JSON content packs, later updated through API.

Current generated content target:
- `content/nitnem_ru_ksd_v1.json`

Local exporter:
- `python3 nitnem_app/export_nitnem_content.py`

One-command local sync:
- `python3 nitnem_app/sync_content_pack.py`

This exports `nitnem_app/content/nitnem_ru_ksd_v1.json`, validates the package
ID `nitnem_ru_sikhizm_resolved`, and copies the exact same JSON into both
Android asset locations used by `nitnem_mobile` and `sggs_mobile`.
