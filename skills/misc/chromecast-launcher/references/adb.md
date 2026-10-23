# ADB inalámbrico en Google TV

## Conectar

1. En la tele: *Ajustes → Sistema → Opciones de desarrollador → Depuración inalámbrica*. Pide al usuario la IP y el puerto que aparecen.
2. `adb connect IP:PUERTO`. Si dice `failed to authenticate` o el dispositivo sale `offline`, empareja: pide al usuario *Emparejar dispositivo con código* y ejecuta `adb pair IP:PUERTO_DE_EMPAREJAMIENTO CÓDIGO`.
3. El puerto de conexión cambia al reiniciar la tele y al apagar o encender el Wi-Fi. `adb mdns services` lista los puertos vigentes (`_adb-tls-connect._tcp`); prueba cada uno, solo responde el activo.
4. Un puerto abierto que da `offline` sin emparejar no sirve: escanear puertos no lo arregla. Empareja primero.

## Comprobar

`adb devices` debe mostrar `IP:PUERTO  device`. Si aparece también una entrada `adb-…._adb-tls-connect._tcp`, es la misma tele por mDNS.

## Capturas

`scripts/capture.py SALIDA.png [TECLA…]` envía las teclas y guarda `adb exec-out screencap -p`. Sin sleep, la captura de una animación sale a medias: usa `adb exec-out screencap -p > f.png` directamente para fotogramas intermedios. Para revisar varias pantallas a la vez, monta una hoja de contacto con Pillow (`resize((640,360))`).
