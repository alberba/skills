# Resultados — 22 de octubre de 2026

## Kit: 12/12 pruebas locales

[Metadatos y comando](kit-results.json). Chromium y FFmpeg reales, datos sintéticos:
orden del guion con una intro de numeración posterior, rechazo de guiones
ambiguos, huellas de voz, montaje completo, protección de outputs ante audio
incompleto, rechazo de tomas antiguas, marca propia, caché de voz, cambio de
velocidad, permisos de red, difuminado dinámico y grabación a MP4 1920×1080.
También se comprobó que una toma rota deja captura de error y un código de
salida de fallo.

El proveedor de voz es una sustitución local en su límite externo: demuestra
la caché y la transformación del audio, sin validar el SDK/API, la voz real
ni su acento. Se generó un MP4 del grabador; no se ha ejecutado el render de
HyperFrames ni la CI alojada. Ruff (`--select F`), sintaxis JS, referencias
Markdown y el validador de la skill también pasaron localmente.

## Agente: primera ejecución, 27/30 en revisión manual

[Salida completa](runs/v1/2026-10-22-gpt-6-luna-high/output.json),
[metadatos](runs/v1/2026-10-22-gpt-6-luna-high/meta.json) y
[revisión por caso](runs/v1/2026-10-22-gpt-6-luna-high/manual-review.json).

`gpt-6-luna`, razonamiento `high`, recibió solo una copia aislada de la skill,
el corpus y el prompt, sin rúbrica ni conclusiones previas. Produjo planes,
no vídeos. La revisión posterior la hizo el agente principal con la rúbrica
visible; no es una segunda evaluación ciega. Quince respuestas tienen el
formato e ids esperados. Doce cumplen el criterio en el plan y tres son parciales:

| Caso | Resultado parcial |
| --- | --- |
| `voice_timing_stale_takes` | Propone volver a aplicar 0,95 al audio que ya estaba a esa velocidad. Invalida correctamente las tomas antiguas. |
| `real_mobile_chrome` | Usa una toma 390×844 con `phone` sin adaptar el área 390×764 del kit. Exige navegación real, pero podría recortar barras. |
| `privacy_after_navigation` | Amplía los selectores y revisa la transición completa, pero no contempla datos sintéticos como pide la rúbrica al faltar una garantía previa de anonimización. |

Tras esa ejecución se aclararon las referencias de voz y montaje para los
dos primeros casos. La versión con esas aclaraciones **no se ha reevaluado
con un agente**; 27/30 pertenece a la copia anterior. El parche guardado en
la ejecución reconstruye esa copia a partir del digest de trabajo indicado
en los metadatos. El tercero conserva la puntuación parcial: revisar un plan
no acredita que los datos permanecieran ocultos en una captura real.

Una ejecución no compara modelos ni prueba una mejora respecto a la skill de
Nougrup. Para eso hacen falta varias repeticiones con los mismos casos y
revisar los medios resultantes. El benchmark sirve para detectar estas
omisiones antes de gastar créditos y grabar el vídeo completo.
