#!/usr/bin/env bash
set -e

export ANDROID_HOME=/home/royal/Work/Spiritual/KSD_AI/.android-sdk
export PATH="$ANDROID_HOME/platform-tools:$PATH"

cd "$(dirname "$0")"
./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
echo "Done."
