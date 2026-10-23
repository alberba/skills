#!/usr/bin/env bash
# Compila el launcher sin Gradle: aapt2 + javac + d8 + apksigner.
# Variables: ANDROID_SDK_ROOT, JAVA_HOME, WORK_DIR (descargas y compilación), OUT (APK), KEYSTORE.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SDK="${ANDROID_SDK_ROOT:-$HOME/Library/Android/sdk}"
BT="$(ls -d "$SDK"/build-tools/* | sort -V | tail -1)"
PLATFORM="$(ls -d "$SDK"/platforms/android-* | sort -V | tail -1)"
JAVAC="${JAVA_HOME:+$JAVA_HOME/bin/}javac"
WORK="${WORK_DIR:-${TMPDIR:-/tmp}/tv-launcher-build}"
DEPS="$WORK/deps"
BUILD="$WORK/build"
OUT="${OUT:-$WORK/clean-tv-launcher.apk}"
# La misma clave firma todas las versiones: así `adb install -r` actualiza sin desinstalar.
KEY="${KEYSTORE:-$HOME/.android/tv-launcher.keystore}"
if [[ ! -f "$KEY" ]]; then
  mkdir -p "$(dirname "$KEY")"
  keytool -genkeypair -keystore "$KEY" -storepass android -keypass android -alias tvlauncher \
    -dname "CN=TV Launcher" -keyalg RSA -keysize 2048 -validity 10000
fi
mkdir -p "$DEPS" "$BUILD/classes" "$BUILD/dex" "$BUILD/aar"
fetch_aar() {
  local group="$1" artifact="$2" version="$3"
  local path="${group//.//}/$artifact/$version/$artifact-$version.aar"
  local file="$DEPS/$artifact-$version.aar"
  if [[ ! -f "$file" ]]; then curl -fL --retry 3 "https://dl.google.com/dl/android/maven2/$path" -o "$file"; fi
  mkdir -p "$BUILD/aar/$artifact"
  unzip -oq "$file" -d "$BUILD/aar/$artifact"
}
fetch_jar() {
  local group="$1" artifact="$2" version="$3"
  local path="${group//.//}/$artifact/$version/$artifact-$version.jar"
  local file="$DEPS/$artifact-$version.jar"
  if [[ ! -f "$file" ]]; then curl -fL --retry 3 "https://dl.google.com/dl/android/maven2/$path" -o "$file"; fi
}
fetch_maven_jar() {
  local group="$1" artifact="$2" version="$3"
  local path="${group//.//}/$artifact/$version/$artifact-$version.jar"
  local file="$DEPS/$artifact-$version.jar"
  if [[ ! -f "$file" ]]; then curl -fL --retry 3 "https://repo.maven.apache.org/maven2/$path" -o "$file"; fi
}

fetch_aar androidx.recyclerview recyclerview 1.3.2
fetch_aar androidx.core core 1.7.0
fetch_aar androidx.customview customview 1.0.0
fetch_aar androidx.customview customview-poolingcontainer 1.0.0
fetch_aar androidx.core core-ktx 1.5.0
fetch_jar androidx.annotation annotation 1.1.0
fetch_jar androidx.collection collection 1.0.0
fetch_maven_jar org.jetbrains.kotlin kotlin-stdlib 1.6.21
fetch_maven_jar org.jetbrains.kotlin kotlin-stdlib-common 1.6.21
fetch_maven_jar org.jetbrains annotations 13.0

CP="$BUILD/aar/recyclerview/classes.jar:$BUILD/aar/core/classes.jar:$BUILD/aar/customview/classes.jar:$BUILD/aar/customview-poolingcontainer/classes.jar:$BUILD/aar/core-ktx/classes.jar:$DEPS/annotation-1.1.0.jar:$DEPS/collection-1.0.0.jar:$DEPS/kotlin-stdlib-1.6.21.jar:$DEPS/kotlin-stdlib-common-1.6.21.jar:$DEPS/annotations-13.0.jar"
find "$BUILD/classes" -type f -delete
find "$BUILD/dex" -type f -delete
rm -rf "$BUILD/gen" "$BUILD/res"
mkdir -p "$BUILD/gen" "$BUILD/res"
for artifact in recyclerview core customview customview-poolingcontainer core-ktx; do
  if [[ -d "$BUILD/aar/$artifact/res" ]] && find "$BUILD/aar/$artifact/res" -type f -print -quit | grep -q .; then
    "$BT/aapt2" compile --dir "$BUILD/aar/$artifact/res" -o "$BUILD/res/$artifact.zip"
  fi
done
RESOURCE_ARGS=()
for artifact in recyclerview core customview customview-poolingcontainer core-ktx; do
  [[ ! -f "$BUILD/res/$artifact.zip" ]] || RESOURCE_ARGS+=( -R "$BUILD/res/$artifact.zip" )
done
ASSET_ARGS=()
if [[ -d "$HERE/app/src/main/assets" ]]; then ASSET_ARGS+=( -A "$HERE/app/src/main/assets" ); fi
"$BT/aapt2" link -o "$BUILD/launcher-unsigned.apk" -I "$PLATFORM/android.jar" \
  --manifest "$HERE/app/src/main/AndroidManifest.xml" --min-sdk-version 26 --target-sdk-version 34 \
  --auto-add-overlay \
  --java "$BUILD/gen" --extra-packages "androidx.recyclerview:androidx.core:androidx.customview:androidx.customview.poolingcontainer" \
  "${RESOURCE_ARGS[@]}" "${ASSET_ARGS[@]}"
"$JAVAC" -encoding UTF-8 -source 8 -target 8 -bootclasspath "$PLATFORM/android.jar" -classpath "$CP" -d "$BUILD/classes" \
  $(find "$HERE/app/src/main/java" "$BUILD/gen" -name '*.java' -print)
jar cf "$BUILD/app-classes.jar" -C "$BUILD/classes" .
"$BT/d8" --min-api 26 --lib "$PLATFORM/android.jar" --lib "$BT/core-lambda-stubs.jar" --output "$BUILD/dex" \
  "$BUILD/app-classes.jar" "$BUILD/aar/recyclerview/classes.jar" "$BUILD/aar/core/classes.jar" \
  "$BUILD/aar/customview/classes.jar" "$BUILD/aar/customview-poolingcontainer/classes.jar" "$BUILD/aar/core-ktx/classes.jar" \
  "$DEPS/annotation-1.1.0.jar" "$DEPS/collection-1.0.0.jar" \
  "$DEPS/kotlin-stdlib-1.6.21.jar" "$DEPS/kotlin-stdlib-common-1.6.21.jar" "$DEPS/annotations-13.0.jar"
python3 - "$BUILD/launcher-unsigned.apk" "$BUILD/dex/classes.dex" <<'PY'
import sys, zipfile
with zipfile.ZipFile(sys.argv[1], 'a', compression=zipfile.ZIP_DEFLATED) as apk:
    apk.write(sys.argv[2], 'classes.dex')
PY
"$BT/zipalign" -f 4 "$BUILD/launcher-unsigned.apk" "$BUILD/launcher-aligned.apk"
"$BT/apksigner" sign --v4-signing-enabled false --ks "$KEY" --ks-pass pass:android --key-pass pass:android \
  --out "$OUT" "$BUILD/launcher-aligned.apk"
"$BT/apksigner" verify --verbose "$OUT"
printf 'Built %s\n' "$OUT"
