# El launcher de la plantilla

Launcher Java nativo (sin Gradle), pensado para mando de TV: 5 apps por fila, sin desplazamiento horizontal y con la cuadrícula de apps en vertical.

## Compilar

`assets/launcher/build.sh` usa las últimas build-tools y la última plataforma de `ANDROID_SDK_ROOT`, descarga RecyclerView de Google Maven y firma con `~/.android/tv-launcher.keystore` (la crea si falta). Conserva esa clave: con la misma firma, `adb install -r` actualiza sin desinstalar. `WORK_DIR` y `OUT` cambian dónde se compila y dónde queda el APK.

`hardwareAccelerated="true"` en el manifiesto: sin él, el recorte redondeado (`clipToOutline`) y la elevación no se dibujan.

## Lo que el usuario ya decidió

- Diseño Apple TV fijo (`Design.ALL.get(1)`); el botón de cambiar de diseño se quitó. Los otros diseños siguen en `Design.java` sin acceso desde la interfaz. «Taller» usa Manrope y Unbounded, que no van en la plantilla y caen a la fuente del sistema.
- Favoritos: Jellyfin, YouTube, Netflix, Prime Video, Movistar+. Máximo 5.
- Sin texto bajo las tarjetas, sin «Favorita» ni «Pulsa OK», sin borde ni brillo al enfocar. Zoom 1.10, hueco 12 dp, tarjeta 162×91 dp.
- El título grande solo aparece con los favoritos enfocados; al bajar a la lista se desvanece.
- Fondo por defecto: Montañas. El botón «Fondo» rota entre nueve.

## Comportamiento

- Con el foco en favoritos: panel gris traslúcido abajo, hero arriba, lista oculta. Al bajar, el panel se disuelve y los favoritos pasan a ser la primera fila. Con el foco a partir de la 4.ª fila de apps, los favoritos salen por arriba.
- Mover apps: mantener OK levanta la tarjeta, las flechas la mueven (también entre favoritos y lista), OK o Atrás la suelta. El orden se guarda en `SharedPreferences` (`favs`, `apps`).

## Trampas de foco y layout

- El foco con flechas depende de la geometría: la lista oculta debe quedar **debajo** del panel de favoritos, sin solaparse; si se solapan, Abajo no llega.
- Una `RecyclerView` que recorta (`clipChildren` + `clipToPadding`) corta la tarjeta ampliada en los bordes: deja margen en las tarjetas (`topMargin`/`bottomMargin`), no relleno.
- Para centrar una fila, calcula el relleno a partir del ancho real; el hueco de la última tarjeta se descuenta del relleno derecho.
- Anima el balanceo con `ObjectAnimator`. Un `ViewPropertyAnimator` sobre la misma vista pisa el movimiento del `ItemAnimator`.
- Durante el modo mover, `dispatchKeyEvent` consume todas las teclas; ignora las repeticiones del OK que activó el modo.
- `am start --ei bg N` sobre un launcher ya abierto llega a `onNewIntent`; si no está abierto, `onCreate` lo ignora: lanza dos veces.
