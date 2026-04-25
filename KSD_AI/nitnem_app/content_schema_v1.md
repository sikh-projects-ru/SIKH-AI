# Content Pack Schema V1

Top-level content pack:

```json
{
  "schema_version": 1,
  "content_version": 1,
  "package_id": "nitnem_ru_ksd_sggs_001_013",
  "language": "ru",
  "source": {
    "name": "Sri Guru Granth Sahib",
    "ang_start": 1,
    "ang_end": 13
  },
  "translators": [],
  "banis": [],
  "angs": []
}
```

## Translator

```json
{
  "id": "ksd_ru",
  "name": "KSD Russian",
  "language": "ru",
  "style": "interpretive"
}
```

## Bani

```json
{
  "id": "nitnem_sggs_ang_001_013",
  "title": "Нитнем",
  "subtitle": "Первые 13 ангов СГГС",
  "ang_start": 1,
  "ang_end": 13,
  "section_refs": [
    { "type": "ang", "ang": 1 }
  ],
  "info_blocks": []
}
```

## Ang

```json
{
  "ang": 1,
  "shabads": []
}
```

## Shabad

```json
{
  "id": "1:1",
  "ang": 1,
  "shabad_id": 1,
  "rahao_verse_id": null,
  "rahao_theme": "",
  "summary": "",
  "lines": []
}
```

## Line

```json
{
  "id": "1:1:1",
  "ang": 1,
  "shabad_id": 1,
  "verse_id": 1,
  "is_rahao": false,
  "gurmukhi": "",
  "roman": "",
  "roman_display": "",
  "translations": {
    "ksd_ru": {
      "main": "",
      "artistic": "",
      "context_note": "",
      "confidence": 0.0,
      "confidence_reason": ""
    }
  },
  "word_analysis": []
}
```

## Notes

- `roman` is source transliteration.
- `roman_display` is a display-friendly variant.
- Future translators are added under `translations`.
- Future API updates should replace the whole content pack or apply a signed
  manifest-based patch.

