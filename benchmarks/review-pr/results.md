# Resultados — 23 de octubre de 2026

Claude Sonnet 5.5, esfuerzo `medium`, una ejecución por fila.

## PR A (refactor grande con migraciones destructivas)

| Brazo | Coste | Tiempo | Herramientas | Hallazgos nuevos verificados | Nota | Publicación (10 reglas) |
| --- | --- | --- | --- | --- | --- | --- |
| Skill original (~450 líneas) | $1,02 | 2 min 45 s | 27 | 1 | 5,5 | no evaluada |
| Sin skill | $3,05 | 8 min 29 s | 70 | 7 | **7,5** | no publica |
| Skill optimizada (pasos + checklist por capa) | $2,39 | 14 min 9 s | 68 | 2 | 6,5 | 2 ✅ · 2 ⚠️ · 6 ❌ |
| Corta v1 | $1,48 | 7 min 38 s | 63 | 2 | 7 | 2 ✅ · 2 ⚠️ · 6 ❌ |
| Corta v2 (sin validaciones del CI, pasada de flujos) | $2,58 | 8 min 55 s | 67 | 2 | 6,5 | 2 ✅ · 3 ⚠️ · 5 ❌ |

Hallazgos de la unión verificada, en términos genéricos: permisos que no se renombran porque el framework renombra el content type antes del `RunPython`; la vuelta atrás de esas migraciones falla en bases con datos; un borrado lógico que elimina líneas de cestas ligadas a ofertas; columnas con datos vivos del ERP borradas sin declararlo; un ADR que afirma que no cambia el esquema; textos que pierden su traducción al retirar la dependencia; una referencia documental a un fichero que no está en la rama.

- La ejecución sin skill fue la única que siguió los servicios hasta encontrar el borrado de líneas de oferta y las traducciones perdidas.
- La prueba de migraciones con filas sembradas dio las evidencias más sólidas (permisos duplicados en la base, `IntegrityError` al revertir).
- La skill original llegó a su único bloqueante copiándolo de una review ya publicada y se saltó su propio paso de validación.
- Un hallazgo repetido por varias skills (`logger.exception` en un caso de negocio previsto) contradecía una decisión registrada en la PR: falso positivo.

## PR B (proveedor nuevo de sincronización)

| Brazo | Coste | Tiempo | Herramientas | Encontrados por su cuenta | Nota | Publicación |
| --- | --- | --- | --- | --- | --- | --- |
| Corta v3 (reglas de publicación) | $0,89 | 3 min 5 s | 26 | 0 nuevos; enlazó los 4 publicados | 6,5 | 9 ✅ · 1 ⚠️ |
| Sin skill (sin leer lo publicado) | $0,75 | 3 min 49 s | 21 | 3 de 4 publicados + 1 nuevo | 7,5 | no publica |
| **Corta v4 (versión actual)** | $0,85 | 3 min 13 s | 23 | **4 de 4 publicados + 1 nuevo** | **8** | 9 ✅ · 1 ⚠️ |

El hallazgo nuevo fue una promesa incumplida: la docstring de la tarea anuncia un cierre ordenado por presupuesto de tiempo que el proveedor nuevo no implementa. La v4 lo encontró por el criterio de contrastar promesas con código.

## Límites

- Una ejecución por brazo; la varianza entre ejecuciones no está medida.
- La v4 no se ha ejecutado sobre la PR A: su criterio de migraciones con datos solo se probó en v2, que costó $2,58 allí.
- Las ejecuciones posteriores veían las reviews publicadas por las anteriores. Para medir la independencia, la v4 entregó su lista antes de deduplicar.
- La evaluación la hizo el agente principal conociendo cada brazo.
