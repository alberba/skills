# Resultados

Una ejecución por configuración, sin repetir. Puntuación = comprobaciones automáticas de `checks.json` (más `presente` y `formato` por caso); no incluye la revisión con `rubric.md`. Solo son comparables las ejecuciones de la misma versión de corpus y prompt.

## Corpus v3, prompt v4 (26 casos, 558 comprobaciones) — 2026-10-21

| Modelo | Esfuerzo | Skill | Puntos | % | Casos con fallo |
| --- | --- | --- | --- | --- | --- |
| claude-sonnet-5-5 | por defecto | `dbee9c6` (anterior) | 557/558 | 99,8 | 1 |
| claude-sonnet-5-5 | medium | `dbee9c6+4edd0fc` (compacta) | 557/558 | 99,8 | 1 |
| claude-sonnet-5-5 | por defecto | `dbee9c6+4edd0fc` (compacta) | 556/558 | 99,6 | 2 |
| claude-sonnet-5-5 | low | `dbee9c6+4edd0fc` | 552/558 | 98,9 | 6 |
| claude-opus-5-5 | medium | `dbee9c6+4edd0fc` | 551/558 | 98,7 | 2 |
| opencode-go/muse-spark-1.3-contributor | — | `dbee9c6+4edd0fc` | 540/562 | 96,1 | 15 |
| claude-opus-5-5 | low | `dbee9c6+4edd0fc` | 535/558 | 95,9 | 6 |
| opencode-go/deepseek-v4.1-flash | — | `dbee9c6+4edd0fc` | 527/558 | 94,4 | 13 |

`4edd0fc` es la skill compacta con la rama bug/feature/task en `ready-for-agent.md`, sin la regla del label `visual` que se añadió después a `SKILL.md`.

### Qué separa a los modelos

- **Todos fallan `export_codes` por `cuerpo_breve`** (más de 140 palabras en el cuerpo), salvo deepseek y Opus low, que fallan otras. Una comprobación que casi nadie pasa no discrimina: conviene decidir si 140 es un límite razonable para ese caso o se relaja.
- **muse-spark:** escribe los criterios de aceptación sin casillas `- [ ]` en 11 casos y usa mal el título y la plantilla en `blocked_dependency`.
- **deepseek-v4.1-flash:** no enlaza el brief desde el cuerpo en 13 casos y, en `two_problems` y `no_priority`, no publica y pregunta.
- **Opus low** (y Opus medium en `incomplete_search`): se para a preguntar la prioridad o el comportamiento de las URLs antiguas en vez de publicar, aunque el usuario dijo «crea».
- **Sonnet low:** criterios de aceptación insuficientes en varios casos y una cifra inventada en `cross_repo_related`.

### Lectura

- Ni con 26 casos y comprobaciones más estrictas baja de ~94 %: los modelos fuertes están entre 98 y 99,8 %. Las diferencias son de forma y de preguntar de más, no de saltarse las reglas centrales.
- Los dos mejores resultados son las dos skills de Sonnet por defecto y Sonnet medium; la skill compacta no pierde frente a la anterior (556–557 frente a 557).
- Que Opus puntúe por debajo de Sonnet sale de preguntar antes de publicar, no de errores de contenido; es una ejecución por configuración y no prueba una diferencia real.

## Historial

- **v2** (15 casos, prompt v2, 2026-10-21): ocho ejecuciones, todas entre 177 y 179 de 178–180. Ver `runs/v2/`.
- **v1** (8 casos, prompt v1): el prompt no decía que `notes` es texto, así que Sonnet medium y low puntuaron 79/87 solo por formato; el resto 87/87. Ver `runs/v1/`.

`measure.py` solo puntúa la versión vigente: las carpetas anteriores conservan su `metrics.json`.
