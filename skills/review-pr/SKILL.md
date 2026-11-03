---
name: review-pr
description: Revisar una PR de GitHub, añadir comentarios inline y resumen de revisión firmado por el agente que la ejecuta.
argument-hint: "<url-de-pr> o <numero> [owner/repo]"
---

Revisa la PR $ARGUMENTS buscando defectos que cambien el comportamiento o el coste en producción. Lint, tests y comprobaciones de migraciones son del CI.

**PR grande.** Con más de unas 2.000 líneas de código propio en el diff (sin docs, CSS, ficheros generados ni lock files), lee [`GRANDES.md`](GRANDES.md) antes de empezar: reparte la revisión por capas.

**Diff.** Si `gh pr diff` responde `406` (más de 300 ficheros o de 20.000 líneas), no abandones: es una PR grande; aplica [`GRANDES.md`](http://GRANDES.md), que lee el diff desde el checkout con `git diff origin/<base>...HEAD -- <ruta>`.

**Cobertura.** La revisión termina cuando:

- cada función, modelo o tarea con comportamiento cambiado está seguida un nivel hasta quien la llama y comparada con la base (`git show origin/<base>:<ruta>`);
- cada componente, include o helper existente que el diff usa con argumentos nuevos está abierto para ver cómo los interpreta;
- cada punto de entrada que escribe en las mismas tablas que el diff (tarea, comando, vista, señal) aplica las mismas protecciones: lock, transacción y permisos;
- cada promesa (docstrings, documentación, cuerpo de la PR, implementación equivalente en otro proveedor o módulo) está contrastada con lo que el código hace;
- si una migración renombra o borra tablas o columnas, o transforma datos, está probada con filas sembradas desde el estado de la base, ida y vuelta, con la receta de entorno del repositorio;
- cada bucle nuevo o modificado que consulta la base de datos, directamente o a través de un servicio, está entre tus hallazgos o tus descartes con el tamaño máximo que alcanza en producción y la fuente de esa cifra; una docstring o un comentario no son fuente, y un bucle sin cifra justificada entra como pregunta de una línea que pide esa cifra;
- cada área de *Dónde buscar* que el diff toca está mirada.

Cada hallazgo se queda solo con evidencia (código o salida), regresión (no existía en la base) o incumplimiento de lo que la PR promete en el camino normal, y escenario alcanzable. Un valor que viene de un ERP, de datos maestros o de otro usuario es entrada externa; una carrera que puede darse en cada ejecución programada (incremental, beat, reintento) es un escenario alcanzable. Lo que no llega a ese listón se descarta o, si cambia la decisión, entra como pregunta de una línea.

**Dónde buscar.**

- **Runtime**: APIs o firmas mal usadas, `None`, colecciones vacías, fechas, zonas horarias, redondeos, condiciones invertidas, parámetros o settings que no llegan a su consumidor, respuestas HTTP no comprobadas, timeouts.
- **Seguridad**: inyección (SQL, comandos, OData, rutas, fórmulas en exports CSV o Excel), XSS (`innerHTML`, `x-html`, `|safe`, `mark_safe`), SSRF, CSRF o CORS debilitados, secretos versionados (`🔴`, sin repetir el valor; recomendar rotarlos), datos personales en logs o respuestas.
- **Autorización y multiempresa**: cada queryset que recibe IDs se limita a la empresa o usuario antes de leer, modificar, exportar o borrar; `get_object()`, `@action`, exports, adjuntos, tareas Celery. El cliente no puede fijar propietario, empresa ni estado interno. Las transiciones de estado se validan en servidor. Un IDOR es `🔴`.
- **Contratos**: campos, tipos, códigos HTTP, paginación o semántica que cambian; buscar a sus consumidores (templates, JS, tareas, integraciones). Romper un consumidor desplegado es `🔴`; alterar resultados sin avisar es `⚠️`.
- **Rendimiento**: consultas por elemento dentro de un bucle (FK o M2M sin `select_related`/`prefetch_related`, `.get()`/`.filter().first()`/`.count()`/`.exists()` por elemento, un servicio llamado una vez por grupo); si un serializer gana un campo de relación, cada queryset que lo alimenta. También querysets sin acotar sobre tablas grandes, `save()` en bucle donde cabe `bulk_*`/`update()`/`F()` e importaciones sin lotes.
- **Atomicidad y concurrencia**: escrituras de varios pasos sin `transaction.atomic()`, read-modify-write sin `select_for_update()` o sin constraint, `update_fields` incompleto, efectos no idempotentes ante reintentos de Celery o webhooks. Una transacción puede ser atómica y aun así permitir duplicados.
- **Migraciones y despliegue**: falta la migración de un cambio de modelo; `NOT NULL` o reescritura de tabla grande; índices sin `CONCURRENTLY`; data migrations con red o sin lotes; código viejo y nuevo conviviendo durante el despliegue.
- **Errores**: `except Exception` que convierte un fallo en éxito aparente o deja datos a medias, reintentos sin límite, integraciones externas sin timeout.
- **Tests**: las rutas de riesgo (permisos, reglas de negocio, estados, fechas, importaciones) con tests de comportamiento; un fix de bug, con un test que fallaba antes. La ausencia es `⚠️` solo si hace probable una regresión.
- **Frontend**: doble envío sin estado de carga, errores no comunicados, controles inaccesibles por teclado, datos de otro usuario visibles.
- **Código muerto**: ramas inalcanzables, parámetros o salidas sin consumidor. Es `ℹ️ Sugerencia`.

**Orden.** Cierra tu lista de hallazgos antes de leer lo publicado (`gh api .../pulls/N/reviews` y `.../comments`). Después deduplica: lo ya publicado y pendiente entra en el resumen como enlace, con la gravedad de su comentario original. Publica solo si aportas algo nuevo o cambias la valoración publicada.

## Publicación

Una sola review: `gh api .../pulls/N/reviews --method POST --input payload.json` con `commit_id`, `event`, `body` y `comments` (`path`, `line`, `side: RIGHT`). Evento: `COMMENT` en PR propia o draft; si no, `REQUEST_CHANGES` con algún obligatorio y `APPROVE` sin ninguno. Limpia después el entorno que hayas levantado.

**Comentario inline**: el único sitio donde se explica cada hallazgo, en tres frases como máximo:

```
⚠️ Problema, obligatorio — <qué pasa y cuándo>. <impacto en producción>. <corrección concreta>.
```

Severidad por impacto real: `🔴 Bug crítico` y `⚠️ Problema` son siempre `obligatorio`; `ℹ️ Sugerencia` es siempre `opcional`. La evidencia, una línea y solo si es la que convence.

**Resumen (`body`)**, para el autor de la PR:

```
> *Made by <agente> (<modelo>) — revisión automática de PR*

<una o dos frases: valoración y si se puede mergear>

**Obligatorio antes del merge**
- <una línea por hallazgo: los propios nombran su comentario inline; los ya publicados, con enlace>

**Opcional**
- <igual>

**Pruebas**: <qué se ejecutó y su resultado, o que no se ejecutó nada y por qué>.
```

Antes del POST, el borrador cumple: cada hallazgo se desarrolla en un único sitio; el texto habla del código y sus efectos, sin relato del proceso ni identificadores de reviews; cada línea ayuda a decidir; la gravedad corresponde a la consecuencia en producción.
