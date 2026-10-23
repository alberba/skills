---
name: review-pr
description: Revisar una PR de GitHub, añadir comentarios inline y resumen de revisión firmado por el agente que la ejecuta.
argument-hint: "<url-de-pr> o <numero> [owner/repo]"
---

Revisa la PR $ARGUMENTS buscando defectos que cambien el comportamiento en producción. Lint, tests y comprobaciones de migraciones son del CI.

**Cobertura.** La revisión termina cuando:

- cada función, modelo o tarea con comportamiento cambiado está seguida un nivel hasta quien la llama y comparada con la base (`git show origin/<base>:<ruta>`);
- cada promesa (docstrings, documentación, cuerpo de la PR, implementación equivalente en otro proveedor o módulo) está contrastada con lo que el código hace;
- si una migración renombra o borra tablas o columnas, o transforma datos, está probada con filas sembradas desde el estado de la base, ida y vuelta, con la receta de entorno del repositorio.

Cada hallazgo se queda solo con evidencia (código o salida), regresión (no existía en la base) y escenario alcanzable. Lo que no llega a ese listón se descarta o, si cambia la decisión, entra como pregunta de una línea.

**Orden.** Cierra tu lista de hallazgos antes de leer lo publicado (`gh api .../pulls/N/reviews` y `.../comments`). Después deduplica: lo ya publicado y pendiente entra en el resumen como enlace, con la gravedad de su comentario original. Publica solo si aportas algo nuevo o cambias la valoración publicada.

## Publicación

Una sola review: `gh api .../pulls/N/reviews --method POST --input payload.json` con `commit_id`, `event`, `body` y `comments` (`path`, `line`, `side: RIGHT`). Evento: `COMMENT` en PR propia o draft; si no, `REQUEST_CHANGES` con algún obligatorio y `APPROVE` sin ninguno. Limpia después el entorno que hayas levantado.

**Comentario inline**: el único sitio donde se explica cada hallazgo, en tres frases como máximo:

```
⚠️ Problema, obligatorio — <qué pasa y cuándo>. <impacto en producción>. <corrección concreta>.
```

Severidad por impacto real: `🔴 Bug crítico`, `⚠️ Problema`, `ℹ️ Sugerencia`; cada uno `obligatorio` u `opcional`. La evidencia, una línea y solo si es la que convence.

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
