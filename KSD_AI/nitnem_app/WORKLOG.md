# Nitnem App Worklog

Date: 2026-04-25

## Current Product Direction

The user wants a Nitnem reader app:
- First release: Android.
- Future release: iPhone.
- Android should be quick and high-quality.
- Future iOS should not require rewriting the whole core.

Recommended direction:
- Kotlin Multiplatform core.
- Android UI first with Jetpack Compose.
- Future iOS via SwiftUI over shared KMP core, or Compose Multiplatform if it is stable enough at that time.
- Content delivered as versioned JSON packs.
- Future API updates through a manifest/content pack model.

## App Concept

Reader app for Nitnem understood as the first 13 angs of SGGS.

Expected features:
- Reader screen.
- Information blocks / menu.
- About Nitnem section.
- Toggleable display layers:
  - Gurmukhi.
  - Roman transliteration.
  - Roman display.
  - Main Russian translation.
  - Artistic Russian translation.
  - Context notes.
  - Future word analysis.
- Settings:
  - Font size.
  - Theme.
  - Visible layers.
- Later:
  - API updates.
  - Multiple translators.
  - Search.
  - Bookmarks.
  - Last reading position.
  - Google Play release.
  - iOS release.

## Created Files

- `nitnem_app/README.md`
- `nitnem_app/architecture.md`
- `nitnem_app/content_schema_v1.md`
- `nitnem_app/mvp_backlog.md`
- `nitnem_app/editorial_intro_ru.md`
- `nitnem_app/export_nitnem_content.py`
- `nitnem_app/content/nitnem_ru_ksd_v1.json`
- `nitnem_mobile/settings.gradle.kts`
- `nitnem_mobile/build.gradle.kts`
- `nitnem_mobile/gradle.properties`
- `nitnem_mobile/app/build.gradle.kts`
- `nitnem_mobile/app/src/main/AndroidManifest.xml`
- `nitnem_mobile/app/src/main/java/org/ksd/nitnem/MainActivity.kt`
- `nitnem_mobile/app/src/main/assets/nitnem_ru_ksd_v1.json`
- `nitnem_mobile/app/src/main/res/values/styles.xml`
- `nitnem_mobile/README.md`

## Content Pack

Exporter:

```bash
python3 nitnem_app/export_nitnem_content.py
```

Generated file:

```text
nitnem_app/content/nitnem_ru_ksd_v1.json
```

Last measured stats:
- 13 angs.
- 54 shabads.
- 587 lines.
- package id: `nitnem_ru_ksd_sggs_001_013`.

The content pack currently uses:
- `schema_version: 1`
- `content_version: 1`
- translator id: `ksd_ru`
- source: SGGS angs 1-13

## Editorial Frame

The app should include a careful editorial note:

This Russian translation was prepared with regard to the school of Dr. Karminder
Singh Dhillon and inspired by his translation methods and ways of doing vichar
on Gurbani. It is not an official translation by Dr. Karminder Singh Dhillon and
does not fully represent his translations. Serious study requires watching his
lectures, reading his books, translations, articles, and other materials.

Tone requirement:
- Keep it transparent.
- Do not present this as an official KSD translation.
- Avoid making the app intro feel like a polemical pamphlet.
- Present the conceptual position clearly and calmly.

## Nitnem / Ek Granth Editorial Rationale

The app is being framed around the position:

`Ek Granth Ek Panth`

Key SGGS references provided by the user:

```text
ਇਕਾ ਬਾਣੀ ਇਕੁ ਗੁਰੁ ਇਕੋ ਸਬਦੁ ਵੀਚਾਰਿ ॥
Eka Banee Ek Gur Eko Shabad Vichaar
SGGS p646
```

```text
ਪੋਥੀ ਪਰਮੇਸਰ ਕਾ ਥਾਨੁ ॥
Pothi Parmeshar Ka Thaan
SGGS p1226
```

```text
ਸਤਿਗੁਰੂ ਬਿਨਾ ਹੋਰ ਕਚੀ ਹੈ ਬਾਣੀ ॥
Satgur Bina Hor Kachee Hai Banee
SGGS p920
```

```text
ਬਾਣੀ ਗੁਰੂ ਗੁਰੂ ਹੈ ਬਾਣੀ ਵਿਚਿ ਬਾਣੀ ਅੰਮ੍ਰਿਤੁ ਸਾਰੇ ॥
Bani Guru, Guru Hai Bani, Vich Bani Amrit Sarey
SGGS p982
```

```text
ਜੈਸੀ ਮੈ ਆਵੈ ਖਸਮ ਕੀ ਬਾਣੀ ਤੈਸੜਾ ਕਰੀ ਗਿਆਨੁ ਵੇ ਲਾਲੋ ॥
Jaisee Mein Avey Khasam Kee Banee
SGGS p722
```

User rationale:
- Modern common Nitnem cuts existing banis and adds compositions from outside SGGS.
- This app should present Nitnem as the first 13 angs of SGGS.
- The editorial frame should root this in SGGS and the KSD-style `Ek Granth` approach.

Current implementation:
- `editorial_intro_ru.md` contains a more complete Russian editorial explanation.
- `export_nitnem_content.py` includes condensed app `info_blocks`.

## Translation / Terminology Rules Recently Added

These rules were added to `ksd_ai_translator.py` for future prompt generation.

Important current rules:
- Do not use flat cosmology for Jap Ji / SGGS spiritual reading.
- Sahib Singh is low-priority lexical/grammar help only.
- `Sat/Sach` should not default to abstract "truth"; prefer Divine / Creator-related / abiding.
- `Satsangat/Sadhsangat` may be inner connection with Divine / Guru-Shabad / Naam, not necessarily a social group.
- `ghar/dar/duar/mahal` often means inner space of conscience / realization, not external location.
- `māī/mayi` may be Maya, ignorance, mind/reason, or mother only with clear context.
- `moh/moha` means mayaic attachment / enchantment / clouding of discernment, not just ordinary affection.
- `bhavjal` must not be written as "бхаваджал"; translate as ocean/flow of mayaic entanglement.
- `sohila/sohilai` should be unfolded as "песнь Мира", flow of Hukam, inner song of connection, not left as a bare term except in a title.
- `satigur` should be displayed in Russian as `Сатгуру`, not `Сатигур/Сатигуру`.
- Names of God may remain as names: `Сахиб`, `Хар`, `Раам`, `Гобинд`, etc.
- If source has `Har`, prefer `Хар` / `Вездесущий Хар` / `Хар-Наам` rather than always replacing with `Творец`.
- `sukh` should not be written as `сух`; translate as spiritual happiness, inner happiness, steady peace, happiness of sahaj.
- `liv` should not be left as `лив`; translate as steady inner focus, loving attention, focused consciousness toward Har/Naam/Shabad.
- `sanjog` should not be left as `санжог/санджог`; translate as connection, condition, inner conjunction, or spiritual seed that matures in Hukam.
- `sakat` should not be left as `сакат`; translate as manmukh-state, consciousness turned away from Har/Naam/Guru-Shabad.
- `haumai / Хоумэ` is not merely pride/ego. It is susceptibility to influence by "I/we", egoic self-centering, the mechanism through which Maya narrows perception. It can be read through modern terms like motivated reasoning, selective perception, search for resonance instead of reality, and ignoring feedback from Reality, body, conscience, logic, world, fruits of actions, and Hukam.

## Current Known Cleanup Already Done

Before generating the latest app content pack, obvious known old terms were checked and cleaned from current JSON files:

Checked pattern:

```bash
rg -n "\\bсух\\b|суху|сухом|внутренний сух|санжог|санджог|бхаваджал|Сатигур|Сатигуру" ksd_ang_json/ksd_ang_*.json
```

After cleanup, this search returned no app-relevant hits in current `ksd_ang_json/ksd_ang_*.json`.

Affected current JSON files during cleanup:
- `ksd_ang_json/ksd_ang_0004.json`
- `ksd_ang_json/ksd_ang_0010.json`
- `ksd_ang_json/ksd_ang_0011.json`
- `ksd_ang_json/ksd_ang_0013.json`

## Next Practical Steps

1. Re-run exporter after any content changes:

```bash
python3 nitnem_app/export_nitnem_content.py
```

2. Validate generated content:

```bash
python3 -m json.tool nitnem_app/content/nitnem_ru_ksd_v1.json
```

3. Check pack stats:

```bash
python3 -c "import json; p=json.load(open('nitnem_app/content/nitnem_ru_ksd_v1.json', encoding='utf-8')); print('angs', len(p['angs'])); print('shabads', sum(len(a['shabads']) for a in p['angs'])); print('lines', sum(len(s['lines']) for a in p['angs'] for s in a['shabads'])); print('package', p['package_id'])"
```

4. Open `nitnem_mobile` in Android Studio.

5. Add or let Android Studio generate a Gradle wrapper.

6. Install Android SDK API 36 / Build Tools 36.0.0 if Android Studio asks.

7. Run the app on an emulator/device.

8. If the app builds cleanly, split content models/parser into a shared module before starting iOS/KMP work.

## Mobile Prototype State

The Android prototype is intentionally small and local-first:

- It reads `nitnem_ru_ksd_v1.json` from Android assets.
- It shows menu/info blocks.
- It lets the reader switch angs.
- It lets the reader toggle transliteration, main translation, artistic layer, context notes, and comments.
- It includes an `Обновления` drawer item rendered from `nitnem_mobile/app/src/main/assets/updates.md`.
- It preserves the DOCX color logic:
  - Gurmukhi: `#550000`
  - Roman: `#555555`
  - Translation: `#005500`
  - Context: `#0055AA`
  - Comment: `#888888`
  - Artistic: `#333366`
  - Rahao: `#880044`
  - Heading/ink: `#222222`

Local environment limitation:
- A local Android SDK was installed under `.android-sdk`.
- A local Gradle 9.3.1 was installed under `.cache/gradle/gradle-9.3.1`.
- `nitnem_mobile/local.properties` points to the local SDK.
- `nitnem_mobile/gradlew` was generated.
- `assembleDebug` completed successfully.
- Built APK: `nitnem_mobile/app/build/outputs/apk/debug/app-debug.apk`.
- Latest APK SHA-256: `e7674188ca9c544ea66d77403d431ea6e66ebd4fb99d3b8070232e1170c608dc`.
- `adb devices` currently showed no connected/authorized phone.
- Android Emulator is not recommended in this environment because `/dev/kvm` is absent and CPU virtualization flags were not visible.

2026-04-25 follow-up fixes:
- Drawer menu was converted to a `LazyColumn`; the content pack had all 13 angs, but the phone UI only showed the first visible part of the drawer.
- Inline `[[context]]` fragments inside the main green translation are now rendered in blue and without the square brackets.
- New debug APK was built successfully after these fixes.
- Content pack now includes `works` and `authors`.
- Lines and shabads now include `work_id`, `work_unit_*`, `author_id`, `author_name_ru`, and `mahalla`.
- Android drawer now includes work navigation: Джап, Со Дар, Со Пуркх, Сохила.
- Line headers now show work/unit/ang/line and the expanded card shows the author.
- Author display is now controlled by a reader setting and defaults to hidden.
- Collapse/expand text buttons were replaced by compact arrow icon buttons.
- Info blocks were expanded for `Ek Granth Ek Panth Ek Maryada` and the first-13-angs rationale.

Gradle note:
- Android Gradle Plugin 9 has built-in Kotlin support, so `org.jetbrains.kotlin.android` should not be applied separately in `nitnem_mobile`.
- The app module applies `com.android.application` and `org.jetbrains.kotlin.plugin.compose`.

Testing note:
- To rebuild and install on the connected phone in one step, use the deploy script:
  `cd nitnem_mobile && ./deploy.sh`
- `deploy.sh` runs `./gradlew assembleDebug` then `adb install -r`. It works as a seamless update (no uninstall needed) as long as the same debug keystore is used. If the keystore changes (new machine/agent), uninstall the old version from the phone once, then `./deploy.sh` will work from that point on.
- The phone must be connected via USB with USB debugging enabled.

Future comments/audio note:
- Do not store audio bytes inside translation JSON.
- Store comments as metadata linked to a shabad/pauri/line id.
- Store audio as separate local assets for bundled audio, or as remote files with URL, checksum, duration, title, language, speaker, and content version.
- A future schema can add something like `commentary_items` with fields: `id`, `target_type`, `target_id`, `kind`, `title`, `body`, `audio_url`, `audio_asset`, `duration_ms`, `checksum`, `language`, `created_at`.

## Caution For Future Agents

- Do not regenerate translations through GPT unless the user explicitly asks.
- The user is currently happy with the translation direction and wants deterministic cleanup where possible.
- Preserve current JSON structure unless changing exporter/content schema intentionally.
- Avoid overwriting unrelated user changes.
- Keep app intro calm and transparent. The theological/editorial stance is important, but the reader experience should remain focused on reading and vichar.
