# Prompt de ejecución (v1)

Entrega este prompt a un agente nuevo. Sustituye `{SKILL_DIR}`, `{CASES}` y `{OUT}` por rutas absolutas. El agente evaluado puede leer la skill y los casos; no le entregues `rubric.md`, `README.md` ni esta retrospectiva. Usa un checkout temporal con la evidencia del caso como única fuente de hechos. Sin red, servicios externos, credenciales ni escrituras fuera de `{OUT}`. Las operaciones descritas se expresan como plan; no grabes, llames a ElevenLabs ni renderices.

---

Evalúa la skill de vídeo de producto en `{SKILL_DIR}`. Lee `SKILL.md` y las referencias que este indique.

Lee `{CASES}`. Para cada objeto de `cases`, trata `request` como la petición del usuario y `evidence` como toda la evidencia disponible del proyecto y de las herramientas. No completes huecos con conocimiento de otro repositorio ni supongas un framework web. La configuración del proyecto está en `videos/<proyecto>/escenas.py`, según los campos de `common`.

Escribe en `{OUT}` un array JSON UTF-8 con exactamente un objeto por caso, conservando el orden. Usa únicamente estos campos en cada objeto:

- `id`: identificador del caso.
- `decision`: una frase que diga qué harías ahora y qué condición determina que el trabajo esté listo o bloqueado.
- `plan`: lista ordenada de acciones concretas; cada elemento incluye `step` y `purpose`.
- `project_config`: objeto con `base_url`, `setup`, `allowed_writes`, `privacy_selectors`, `project_css`, `modes` y `voice` (ID, modelo e idioma); usa `null` cuando el caso no aporta ese valor y no inventes secretos.
- `voice_cache`: objeto con `reuse`, `cache_key_inputs` y `invalidate_when`; `reuse` es booleano.
- `capture_checks`: lista de comprobaciones visuales o temporales que aplicarías a las tomas y al montaje.
- `authorization`: objeto con `already_granted`, `next_action` y `approval_needed`; distingue aprobaciones registradas y vigentes de las acciones aún no autorizadas.
- `questions`: preguntas imprescindibles para desbloquear el caso; lista vacía si la evidencia basta.
- `artifacts`: lista de rutas relativas que crearías o actualizarías.
- `blockers`: lista de límites concretos que impiden completar una parte; vacía si no hay ninguno.
- `notes`: supuestos acotados o limitaciones de evidencia.

Devuelve solo la ruta absoluta de `{OUT}`. El fichero debe ser JSON válido, sin Markdown ni texto adicional. No afirmes que una acción ocurrió: describe el plan según la evidencia.
