# SGGS App Content

Exporter for the `Sri Guru Granth Sahib RU` Android content pack.

Run from repository root:

```bash
python3 sggs_app/export_sggs_content.py
```

The exporter reads:

- `ksd_ang_json/ksd_ang_*.json`
- `sggs_meta/raags.json`
- `sggs_meta/authors.json`
- `sggs_meta/shabad_index.json`

It writes:

- `sggs_app/content/sggs_ru/`
- `sggs_mobile/app/src/main/assets/sggs_ru/`

