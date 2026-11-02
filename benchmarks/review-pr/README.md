# Benchmark de review-pr

Compara versiones de la skill contra una revisión sin skill sobre dos PRs reales de un repositorio privado (Django). El corpus no se publica: aquí quedan el método, la rúbrica, las métricas y las conclusiones, con los hallazgos descritos de forma genérica.

| Archivo | Uso |
| --- | --- |
| [`rubric.md`](rubric.md) | Criterios de precisión de los hallazgos y reglas de publicación. |
| [`results.md`](results.md) | Ejecuciones, coste, tiempo, notas y límites. |
| [`retro.md`](retro.md) | Qué instrucciones aportaron, cuáles sobraron y por qué se llegó a la versión actual. |
| [`harness/`](harness/) | Montaje para repetir el benchmark: repos limpios por PR, condiciones del subagente y coste. |

## Método

- **Modelo:** Claude Sonnet 5.5, esfuerzo `medium`, un subagente por ejecución en un worktree aislado.
- **Brazos:** sin skill (prompt de cuatro líneas, sin leer reviews publicadas, sin publicar) y cada versión de la skill (publicando como `COMMENT`).
- **Métricas:** coste API calculado desde la transcripción con la tarifa pública de Sonnet 5.5 ($2/M entrada, $10/M salida, $2,50/M escritura de caché, $0,20/M lectura), peticiones al modelo, llamadas a herramientas y tiempo de pared.
- **Verificación:** el agente principal comprobó cada hallazgo contra el código del head y de la base antes de puntuarlo. La revisión no es ciega: el evaluador conocía la versión de cada ejecución.

## PRs

| PR | Tamaño | Rasgo |
| --- | --- | --- |
| A | ~200 ficheros, +3.400 líneas | Retirada de una dependencia grande con migraciones destructivas (renombres de modelo y columnas, borrados). Ya tenía varias reviews publicadas. |
| B | 10 ficheros, +1.400 líneas | Nuevo proveedor de sincronización con un ERP, una migración aditiva. Tenía una review previa. |

Una ejecución por brazo y PR: sirve para detectar fallos de la skill, no para afirmar diferencias estables entre versiones.

## Repetir

```bash
export BENCH=/ruta/de/trabajo
harness/prepare.sh repo <clon-local> <owner/repo> <pr> [sha-del-head]   # una vez por PR
harness/prepare.sh runs <pr> v4-<pr>-1 v4-<pr>-2                         # un worktree por ejecución
```

`prepare.sh repo` deja en `$BENCH/repos/pr-<pr>` solo el head y la base de la PR: en una PR ya mergeada, la base es el commit anterior al merge, y no hay historia posterior que delate el arreglo. Para fijar el head de una PR abierta a un commit concreto (el que vio la review que se quiere reproducir), pásalo como cuarto argumento.

Cada ejecución es un subagente con este prompt, que no lee nada fuera de su directorio, `HARNESS.md` y la skill:

```
Directorio del run: $BENCH/runs/<run>
1. Lee harness/HARNESS.md (condiciones que mandan).
2. Lee <skill>.md y síguela con $ARGUMENTS = <pr> <owner/repo>.
PR #<pr>, base `origin/<base>`, checkout en `wt/` del directorio del run.
```

Lo que se espera encontrar en cada PR se fija antes de lanzar y se guarda fuera del alcance de los subagentes. Al puntuar un hallazgo de rendimiento, se sigue hasta el serializer o la vista que de verdad se ejecuta: un queryset sin `select_related` no es N+1 si el serializer no lee esa relación.

`harness/cost.py etiqueta=transcripcion.jsonl ...` saca coste, tiempo, peticiones y herramientas de cada ejecución; con otro modelo, `--precios entrada,salida,escritura,lectura`. El bot de review en CI puede usar otro modelo que el benchmark: compáralo con el mismo.
