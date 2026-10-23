#!/bin/sh
set -eu
: "${TV_SERIAL:?Indica TV_SERIAL con la dirección y puerto ADB actuales}"
adb -s "$TV_SERIAL" shell pm enable --user 0 com.google.android.apps.tv.launcherx
adb -s "$TV_SERIAL" shell pm enable --user 0 com.google.android.tungsten.setupwraith
adb -s "$TV_SERIAL" shell cmd package set-home-activity --user 0 com.google.android.apps.tv.launcherx/com.google.android.apps.tv.launcherx.home.HomeActivity
adb -s "$TV_SERIAL" shell input keyevent KEYCODE_HOME
