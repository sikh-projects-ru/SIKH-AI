# Content Pack Schema V1

Top-level content pack:

```json
{
  "schema_version": 1,
  "content_version": 1,
  "package_id": "nitnem_ru_sikhizm_resolved",
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

## Remote Update Manifest

The mobile app checks the server on launch:

```text
GET /wp-json/ksd-nitnem/v1/manifest?package_id=nitnem_ru_sikhizm_resolved&content_version=1
```

Expected response:

```json
{
  "package_id": "nitnem_ru_sikhizm_resolved",
  "schema_version": 1,
  "content_version": 2,
  "updated_at": "2026-05-06T12:00:00+00:00",
  "has_update": true,
  "sha256": "hex-encoded-sha256-of-package-json",
  "package_url": "https://sikhizm.ru/wp-json/ksd-nitnem/v1/package/nitnem_ru_sikhizm_resolved",
  "public_update_log": [
    {
      "title": "Улучшен перевод Джап Джи",
      "body": "Некоторые строки стали звучать яснее.",
      "sections": ["Джап Джи"]
    }
  ]
}
```

Rules:

- `has_update` is `true` when server `content_version` is greater than the
  client's `content_version`.
- `package_url` returns the full content pack JSON using the same schema.
- `sha256` is calculated from the exact UTF-8 JSON response returned by
  `package_url`.
- If checksum validation fails, the client keeps the local bundled/cached
  package.
- The app currently replaces the whole local package; patch updates can be
  added later under a new manifest field.
