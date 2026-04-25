# KSD Nitnem Mobile

Android-first reader prototype for the first 13 angs of SGGS-based Nitnem.

## Current State

- Jetpack Compose Android app scaffold.
- Local content pack: `app/src/main/assets/nitnem_ru_ksd_v1.json`.
- Reader screen with ang navigation, info blocks, and display toggles.
- Text colors follow the DOCX translation palette.

## Open In Android Studio

Open the `nitnem_mobile` directory as a Gradle project.

The project currently expects:

- JDK 17
- Android SDK API 36
- Android Gradle Plugin 9.1.0
- Gradle 9.3.1 or the Gradle version Android Studio installs for AGP 9.1

AGP 9 has built-in Kotlin support, so this project does not apply
`org.jetbrains.kotlin.android` separately.

## Test On A Phone

Recommended first test:

1. Open `nitnem_mobile` in Android Studio.
2. Let Android Studio sync Gradle and install the missing Android SDK packages.
3. Connect an Android phone by USB.
4. Enable Developer options and USB debugging on the phone.
5. Select the phone in Android Studio and press Run.

APK file test:

1. In Android Studio, use Build > Build App Bundle(s) / APK(s) > Build APK(s).
2. Send `app/build/outputs/apk/debug/app-debug.apk` to the phone.
3. Open the APK on the phone and allow install from this source if Android asks.

Command-line test after a Gradle wrapper exists:

```bash
./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

This repository now has a local `local.properties` pointing to:

```text
/home/royal/Work/Spiritual/KSD_AI/.android-sdk
```

The first debug APK was built successfully at:

```text
app/build/outputs/apk/debug/app-debug.apk
```

ADB is available locally at:

```text
/home/royal/Work/Spiritual/KSD_AI/.android-sdk/platform-tools/adb
```

## Updates Tab

The Updates screen reads:

```text
app/src/main/assets/updates.md
```

For now this is a small markdown-like local file. Later it can be replaced by an
API-fed update feed while keeping the same screen.

## Next Steps

- Add a Gradle wrapper from Android Studio or an installed Gradle.
- Run the app on an Android emulator/device.
- Move parser and content models into a shared module when starting iOS/KMP work.
- Add remote content update metadata and signature/version checks.
