# Benchmark de product-video

El benchmark separa dos cosas: regresiones ejecutables del kit y decisiones de un agente ante quince escenarios sintéticos. Los casos están inspirados en sesiones reales, con evidencia anonimizada en `retro.md`. Consulta [results.md](results.md) para lo ejecutado y sus límites.

| Archivo | Uso |
| --- | --- |
| [`cases.json`](cases.json) | Quince escenarios sintéticos con solicitudes y evidencia disponible para cada uno. No incluye respuestas esperadas. |
| [`PROMPT.md`](PROMPT.md) | Instrucciones literales y formato JSON para producir una salida evaluable. |
| [`rubric.md`](rubric.md) | Criterios esperados separados del corpus, para evaluación manual. |
| [`test_product_video.py`](test_product_video.py) | Pruebas de guion, montaje, caché y grabación real con datos sintéticos locales. |
| [`results.md`](results.md) | Resultados observados y limitaciones. |
| [`retro.md`](retro.md) | Hallazgos priorizados de sesiones reales pertinentes, sin reproducir logs. |

## Regresiones del kit

Desde la raíz del repo, con FFmpeg/ffprobe instalados:

```sh
uv run --no-project --with playwright==1.64.0 python -m playwright install chromium
uv run --no-project --with playwright==1.64.0 python -m unittest discover -s benchmarks/product-video -p 'test_*.py' -v
```

Las pruebas levantan un servidor HTTP local y Chromium, generan audio sintético con FFmpeg y un MP4 de captura. El límite externo de ElevenLabs se sustituye por un proveedor de prueba: se mide la reutilización de audio y sus tiempos sin consumir créditos. El MP4 acredita el grabador, no el render final de HyperFrames. No se usan sesiones ni datos de otro proyecto.

## Evaluación de agentes

1. Prepara un checkout aislado de la skill bajo evaluación y un directorio de salida temporal. Entrega al agente `SKILL_DIR`, `cases.json` y `PROMPT.md`; no le des la rúbrica ni la retrospectiva.
2. Ejecuta una vez por modelo y versión de la skill, sin contexto previo. Mantén cada ejecución sin red, secretos ni escrituras reales. La salida debe ser el JSON indicado por el prompt.
3. Guarda el resultado junto a un `meta.json` y revisa manualmente cada caso con `rubric.md`. La rúbrica permite asignar 0, 1 o 2 por criterio, pero ninguna puntuación se considera medida hasta evaluar una salida real.

Ejemplo de metadatos por ejecución:

```json
{
  "date": "AAAA-MM-DD",
  "model": "identificador exacto del modelo",
  "harness": "producto y versión",
  "skill_digest": "SHA-256 del árbol skills/product-video",
  "skill_git_revision": "SHA o SHA+dirty",
  "corpus_version": 1,
  "prompt_version": 1,
  "rubric_version": 1,
  "hyperframes_version": "versión o unavailable",
  "playwright_version": "versión",
  "elevenlabs_client_version": "versión o no usado",
  "voice_model": "identificador elegido para la ejecución"
}
```

Calcula `skill_digest` con SHA-256 sobre los archivos de la skill (sin `__pycache__` ni bytecode), ordenados por ruta relativa, incorporando para cada archivo su ruta, un byte NUL, su contenido y otro NUL. Registra la revisión Git además del digest para diferenciar contenido commiteado de cambios locales. Las versiones de herramientas y el modelo de voz describen el entorno de esa ejecución; nunca guardes claves, tokens ni valores de entorno secretos en los metadatos.

Sube `corpus_version` si cambia `cases.json`, `prompt_version` si cambia el contrato de `PROMPT.md` y `rubric_version` si cambian los criterios. Conserva resultados anteriores y no compares puntuaciones de versiones distintas como si fueran la misma prueba. Las conclusiones sobre calidad requieren revisar los artefactos, no solo el JSON o una suma.

## Guardrails

Antes de esta migración no había CI ni hooks activos; solo existía `benchmarks/create-issue/measure.py`. El workflow [check.yml](../../.github/workflows/check.yml) ejecuta ahora Ruff (errores de Python) y las regresiones de `product-video`. Se ha ejecutado la suite localmente; la ejecución alojada en GitHub queda pendiente del push.
