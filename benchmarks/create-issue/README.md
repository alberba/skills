# Benchmarks sintéticos de create-issue

Todos los casos de este directorio son inventados. No contiene capturas, correos, documentos, enlaces a incidencias ni datos de clientes reales. Las evidencias del corpus son fixtures de herramientas, no hechos observados en producción.

## Criterio vigente

El cuerpo empieza por el impacto para el usuario y conserva un caso concreto: [ejemplo sintético](selected-body.md). El Agent Brief va en un comentario separado, mantiene la estructura completa de triage y no tiene objetivos de compactación.

- [Casos](cases.json): ocho escenarios independientes de redacción, alcance, autorización, duplicadas, recurrencia y recuperación.
- [Rúbrica](rubric.md): comprobaciones de fidelidad, cobertura y acciones previstas.
- [Variantes](variants/): alternativas experimentales de instrucciones; la skill vigente está en `../../skills/create-issue/`.
- `outputs/`: únicamente salidas generadas a partir de este corpus sintético.

Las salidas y métricas del corpus anterior no se conservan: no son resultados de estos casos. Tampoco se atribuyen a este corpus sus comparaciones históricas.

## Ejecución

Dar a un agente nuevo la skill que se quiera evaluar y `cases.json`, sin darle la rúbrica ni otras salidas. No permitir red ni escrituras externas. Las evidencias proporcionadas sustituyen las consultas. Pedir un array JSON con un elemento por caso: `id`, `action`, `title`, `body`, `brief`, `labels`, `questions`, `operations` y `notes`.

Solo escribir el resultado en `outputs/`. La decisión de crear o comentar debe representarse como un plan, respetando las limitaciones de cada petición. No ejecutar ese plan. El campo `operations` contiene objetos con `operation` y `target`.

Desde este directorio:

```bash
python3 measure.py outputs/current.json
```

El script valida estructura y mide texto; no evalúa significado. Revisar también la rúbrica. La longitud es una señal secundaria del cuerpo: no se premia reducir palabras del Agent Brief. Una ejecución agrupada de ocho casos no acredita superioridad estadística ni verifica llamadas reales a GitHub.
