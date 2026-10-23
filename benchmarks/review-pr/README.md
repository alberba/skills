# Benchmark de review-pr

Compara versiones de la skill contra una revisión sin skill sobre dos PRs reales de un repositorio privado (Django). El corpus no se publica: aquí quedan el método, la rúbrica, las métricas y las conclusiones, con los hallazgos descritos de forma genérica.

| Archivo | Uso |
| --- | --- |
| [`rubric.md`](rubric.md) | Criterios de precisión de los hallazgos y reglas de publicación. |
| [`results.md`](results.md) | Ejecuciones, coste, tiempo, notas y límites. |
| [`retro.md`](retro.md) | Qué instrucciones aportaron, cuáles sobraron y por qué se llegó a la versión actual. |

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
