---
name: chromecast-launcher
description: Chromecast con Google TV / Android TV por ADB inalámbrico. Limpiar apps, instalar un launcher propio y hacer que el botón Home lo abra.
---

# Chromecast con Google TV: limpiar y poner un launcher propio

Todo se hace por ADB inalámbrico, sin tocar el mando salvo para leer datos en la pantalla. Cada paso termina en una comprobación visible: una captura de la tele o la salida de un comando.

`$TV` = `IP:PUERTO` de ADB. Los scripts lo leen de `TV_SERIAL`.

## 1. Conectar

Sigue [ADB](references/adb.md). Hecho cuando `adb -s $TV shell getprop ro.product.model` responde.

## 2. Respaldar

Antes de cambiar nada, guarda `pm list packages`, `pm list packages -d` y `cmd package query-activities --brief -a android.intent.action.MAIN -c android.intent.category.HOME` en una carpeta de respaldo. Copia [`restore-home.sh`](scripts/restore-home.sh) junto a ella. Hecho cuando el respaldo existe y el script se ha leído entero.

## 3. Limpiar apps

Usa `pm disable-user --user 0 <paquete>`, que se revierte con `pm enable`. Desinstalar queda fuera. Deja `com.google.android.tungsten.setupwraith` y `com.google.android.apps.tv.launcherx` hasta el paso 5. Pide confirmación del usuario por cada paquete que no sea una app que él instaló. Hecho cuando cada paquete desactivado está en el respaldo y las apps de uso diario siguen abriendo.

## 4. Launcher propio

Copia [`assets/launcher`](assets/launcher) fuera de la skill y edita `LauncherConfig.java` (`DOCK_PACKAGES`, `DOCK_FALLBACK_LABELS`). Compila con `build.sh`, instala con `adb install -r` y haz una captura con [`capture.py`](scripts/capture.py). Para el diseño, el comportamiento del foco y lo que el usuario ya decidió, sigue [Launcher](references/launcher.md). Hecho cuando la captura muestra los favoritos y la lista de apps, y `logcat -s AndroidRuntime:E` no tiene errores.

## 5. Home

Solo con el visto bueno explícito del usuario, porque cambia el comportamiento de la tele. Sigue [Home](references/home.md). Hecho cuando Home abre el launcher desde dentro de otra app tres veces seguidas, Ajustes se abre, y el usuario ha reiniciado la tele y sigue viéndolo.

## Pruebas sin tocar el mando a ciegas

Cambia el estado con extras de intent (`am start -n dev.clean.tvlauncher/.MainActivity --ei bg 4`) y usa teclas solo para moverte (`DPAD_*`). `DPAD_CENTER` sobre un elemento sin comprobar activa lo que haya debajo: en una prueba abrió los ajustes de Wi-Fi y apagó la red, y la tele se desconectó. Si pasa, pide al usuario que reactive el Wi-Fi y reconecta con [ADB](references/adb.md).

`pm clear dev.clean.tvlauncher` borra los favoritos y el orden guardados. Tras una prueba que lo use, dile al usuario que las preferencias se han reiniciado.
