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

