# Que Home abra el launcher propio

En Google TV, `cmd package set-home-activity` no basta: el home del sistema gana por prioridad. Hacen falta los tres pasos.

1. `pm disable-user --user 0 com.google.android.apps.tv.launcherx` (home de Google TV).
2. `pm disable-user --user 0 com.google.android.tungsten.setupwraith`. Con solo el paso 1, Home abre `setupwraith/.RecoveryActivity` (prioridad 1, la del launcher propio es 0), una pantalla de recuperación que no lleva al launcher.
3. `cmd package set-home-activity --user 0 dev.clean.tvlauncher/.MainActivity`.

## Comprobar

- `cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME` devuelve el launcher propio.
- Abre otra app, pulsa `KEYCODE_HOME` tres veces: `dumpsys activity activities | grep topResumedActivity` apunta al launcher cada vez.
- `am start -a android.settings.SETTINGS` abre Ajustes.
- El usuario reinicia la tele y sigue viendo el launcher. Hasta entonces, el arranque queda sin comprobar.

## Qué se pierde

El home de Google (Gemini, recomendaciones) y, posiblemente, el botón de asistente del mando. Avisa al usuario antes de empezar.

## Revertir

`TV_SERIAL=$TV ./scripts/restore-home.sh` reactiva ambos paquetes y vuelve a fijar el home de Google. Necesita ADB conectado, y tras un reinicio el puerto es otro: ver [ADB](adb.md).
