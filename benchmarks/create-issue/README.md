# Benchmark sintético de create-issue

Mide cómo cumple una skill `create-issue` veintiséis escenarios inventados: redacción, alcance, autorización, duplicadas, recurrencia, recuperación, destino, datos que faltan e instrucciones inyectadas en la evidencia. Está pensado para repetirse con cada modelo y cada versión de la skill y comparar las ejecuciones guardadas. No contiene capturas, enlaces ni datos reales; las evidencias son fixtures, no hechos observados.

| Fichero | Contenido |
| --- | --- |
| [`PROMPT.md`](PROMPT.md) | Prompt literal de ejecución y formato de salida. |
| [`cases.json`](cases.json) | Corpus: reglas comunes y veintiséis casos. Lo único que ve el agente evaluado, junto a la skill. |
| [`checks.json`](checks.json) | Comprobaciones binarias por caso. |
| [`rubric.md`](rubric.md) | Criterio semántico, para la revisión manual. |
| [`selected-body.md`](selected-body.md) | Ejemplo sintético del cuerpo esperado. |
| [`measure.py`](measure.py) | Valida una ejecución, aplica `checks.json` y mide longitud. |
| [`results.md`](results.md) | Puntuaciones y lectura. |
| `runs/v<N>/` | Una carpeta por ejecución, agrupadas por versión del corpus. |

## Ejecutar

1. Copiar la skill a evaluar y `cases.json` a un directorio temporal, sin `checks.json` ni `rubric.md`.
2. Dar `PROMPT.md` a un agente nuevo del modelo a evaluar, sin red ni escrituras externas, con las rutas sustituidas. Una ejecución por agente, sin contexto previo.
3. Guardar la salida en `runs/v<corpus>/<AAAA-MM-DD>-<modelo>-skill-<SHA>/output.json` junto a un `meta.json`:

   ```json
   {
     "date": "2026-10-21",
     "model": "id exacto del modelo",
     "harness": "herramienta y versión con la que se ejecutó",
     "skill": "SHA del commit de la skill, con «+» si había cambios sin commitear",
     "corpus_version": 3,
     "prompt_version": 4
   }
   ```

4. Desde este directorio: `python3 measure.py runs/v3/<ejecución>`. Escribe `metrics.json` en esa carpeta e imprime las comprobaciones fallidas.
5. Revisar los textos con la rúbrica: las comprobaciones son necesarias, no suficientes.

Las ejecuciones son estocásticas: una sola no prueba que una skill sea mejor que otra. Repetir cada configuración antes de atribuir una diferencia.

## Versiones

Cambiar `cases.json` sube `version` (también en `checks.json`); cambiar `PROMPT.md` sube `prompt_version` en `checks.json`. No se comparan ejecuciones de corpus distintos; las anteriores se conservan como historial. Las variantes de skill se reconstruyen desde git con el SHA de `meta.json`; las experimentales previas están en el commit `dbee9c6`, bajo `benchmarks/create-issue/variants/`.
