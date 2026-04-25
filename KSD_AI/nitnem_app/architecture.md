# Nitnem App Architecture

## Goal

Build a high-quality Android Nitnem reader first, while keeping the core ready
for a future iPhone app.

## Stack

Recommended direction:
- Shared core: Kotlin Multiplatform.
- Android UI: Jetpack Compose.
- iOS later: SwiftUI over shared KMP core, or Compose Multiplatform if stable
  enough for the target release.
- JSON: kotlinx.serialization.
- Networking later: Ktor Client.
- Local persistence: SQLDelight for multiplatform, or Android-only storage for
  MVP with a later migration.

## Module Shape

```text
nitnemApp/
  shared/
    models/
    content/
    reader/
    settings/
    sync/
    search/
  androidApp/
    ui/
    reader/
    settings/
    info/
    theme/
  iosApp/              # later
```

## MVP Screens

- Bani list / Nitnem contents.
- Reader screen.
- Display settings.
- Information blocks about Nitnem.
- Bookmarks / saved reading position.

## Reader Layers

Each line can show independently:
- Gurmukhi.
- Roman transliteration.
- Readable roman display.
- Main Russian translation.
- Artistic Russian translation.
- Context note.
- Word analysis later.

## Update Model

MVP:
- Content pack is bundled with the app.

Later:
- App checks a remote manifest.
- If a newer `content_version` exists, downloads the new content pack.
- Content is saved locally and works offline.
- Multiple translators can be added without changing the reader UI.

## Product Rule

The app should feel like a reading and contemplation tool, not a social feed.
Information blocks should support the reading, not interrupt it.

