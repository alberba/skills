# Retrospectiva de vídeo de producto

Síntesis por severidad de evidencia real pertinente en sesiones de Claude. Las fechas identifican sesiones, no cada mensaje. Los detalles de clientes, rutas privadas y credenciales se omiten. Los casos de `cases.json` son sintéticos y no representan estos proyectos reales.

## P1 — Entrega incompleta o contenido móvil engañoso

- **Intro aprobada fuera del corte.** El 22 de octubre, el usuario señaló que faltaba la intro después de haber pedido probarla pegada al recorrido. La intro se había producido como proyecto aparte y el plan inicial era unirla al final; la corrección posterior la incorporó al mismo proyecto. Evidencia: sesión `e5ad5897-3563-4e8b-ba50-f5227d162be0` (22 oct 2026), continuación del trabajo de `126e566d-e3bc-4ff3-a945-06d4ff662296` (14–15 oct 2026). **Lección:** comprobar el orden y la presencia de cada pieza aprobada en el corte final, no inferir que un render separado ya quedó incluido.
- **Móvil con composición y navegación defectuosas.** El 22 de octubre el usuario preguntó qué había pasado con la diapositiva móvil y pidió considerar la parte superior e inferior de un iPhone. En esa sesión aparecen el still duplicado y desplazado sobre el teléfono, una toma que terminaba en pantalla vacía, scroll que desplazaba el borde inferior y una toma móvil que solo recorría la portada sin navegación por la app. Evidencia: sesión `e5ad5897-3563-4e8b-ba50-f5227d162be0` (22 oct 2026), continuación de `126e566d-e3bc-4ff3-a945-06d4ff662296` (14–15 oct 2026). **Lección:** validar a tamaño ampliado las capas, barras superior e inferior, fin de la toma, cursor y recorrido móvil real; un mockup con una captura estática no demuestra comportamiento móvil.

## P2 — Continuidad visual y sincronía

- **Zoom agresivo y cortes sin continuidad.** El 22 de octubre el usuario dijo que los zooms eran demasiado agresivos y no conectaban entre escenas; enumeró movimientos raros en varios cortes. Evidencia: sesión `e5ad5897-3563-4e8b-ba50-f5227d162be0` (22 oct 2026). **Lección:** mantener una cámara suave con relación entre escalas y encuadres consecutivos, y revisar fotogramas de cada transición en el vídeo completo.
- **Scroll que retrocede o altera el marco del teléfono.** El usuario reportó que el scroll móvil estaba roto porque el borde inferior subía. La inspección de la toma encontró que el scroll de la página y la composición del teléfono no mantenían su geometría. Evidencia: sesión `e5ad5897-3563-4e8b-ba50-f5227d162be0` (22 oct 2026). **Lección:** revisar `scroll_inicio`/`scroll_fin`, continuidad de tomas y posición fija del marco y controles durante toda la navegación.
- **Voz y tomas con versiones temporales distintas.** En la sesión del 15 de octubre se documentó una voz regenerada a otra velocidad mientras el montaje aún tenía tomas grabadas con tiempos anteriores; los artefactos advertían que había que volver a grabar para alinear marcas. También apareció una caché antigua sin metadatos de velocidad que se podía reutilizar aunque la configuración hubiera cambiado. Evidencia: sesión `ea810bfb-c6b5-4bf4-8966-9503306b6204` (15 oct 2026); seguimiento en `126e566d-e3bc-4ff3-a945-06d4ff662296` (14–15 oct 2026). **Lección:** vincular caché, marcas y tomas a voz, modelo, idioma, texto y velocidad; revisar desfases antes de montar.

## P3 — Decisiones de foco y acento

- **Foco como decisión visible del vídeo.** En el trabajo del 15 de octubre se eligió para ese vídeo un foco que oscurecía el resto sin borde, distinto de la regla general anterior. La evidencia indica una decisión contextual aceptada, no un defecto universal. Evidencia: sesión `ea810bfb-c6b5-4bf4-8966-9503306b6204` (15 oct 2026). **Lección:** respetar la decisión del vídeo actual y no convertir una excepción visual en valor global sin autorización.
- **Acento aprobado y velocidad explícita.** En la continuación del 14–15 de octubre se aprobó la locución; el 22 de octubre el usuario reiteró que la velocidad debía ser 1, no 0,95. La sesión del 15 también recoge que el acento depende de la voz elegida. Evidencia: `126e566d-e3bc-4ff3-a945-06d4ff662296` (14–15 oct 2026) y `e5ad5897-3563-4e8b-ba50-f5227d162be0` (22 oct 2026). **Lección:** fijar voz, idioma y velocidad de forma explícita por proyecto y volver a confirmar sincronía si cambia cualquiera de esos valores.

## P2 — Guardrails y portabilidad

En el repo de destino no había `package.json`, CI ni hooks activos que
comprobaran el kit. `benchmarks/create-issue/measure.py` ya era un precedente
útil; no valida los scripts de vídeo. Se añadió una suite local y CI con Ruff
y Chromium/FFmpeg para las invariantes mecánicas. La estética, el acento y la
privacidad completa siguen necesitando revisar los medios.

El código de origen mezclaba captura/montaje con login Django, impersonación,
rutas del ERP, selectores de la tienda, logos y una voz privada. Se trasladó
el mecanismo compartido y se dejaron esos datos en la configuración del vídeo.
La referencia `entorno.md` conserva una guía para migrar proyectos existentes.
El checkout de nougrup-ecommerce no se ha modificado durante este traslado.
