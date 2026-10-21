# Preparación para agentes

Una issue está `ready-for-agent` cuando un agente puede comenzar sin pedir decisiones de producto o alcance y puede comprobar cuándo ha terminado. La ausencia de una causa raíz o de una implementación prescrita no impide ese estado si el problema y el resultado solicitado están definidos.

## Reporte y contrato

El cuerpo sigue el template y conserva el problema, un caso verificable, la evidencia decisiva y el resultado solicitado. Agrupar los datos del mismo caso en un párrafo o tabla; enlazar el diagnóstico extenso si existe. Mantener explícitas las discrepancias relevantes y los límites de lo comprobado.

El comentario `## Agent Brief` convierte ese reporte en un contrato de aceptación. Empieza con una referencia al reporte y escribe los resultados verificables que completan la tarea. Cada criterio describe un resultado distinto. La explicación del fallo ya vive en el cuerpo: el brief se apoya en ella sin repetir la reproducción, los identificadores completos ni la lista de observaciones.

Solo añadir un párrafo de alcance cuando haya decisiones acordadas que no se entiendan del cuerpo. Añadir un dato técnico adicional únicamente si cambia un criterio o evita una ambigüedad concreta. Un brief puede ser una referencia y dos criterios; una investigación compleja puede requerir más resultados. Los hallazgos adyacentes no se convierten automáticamente en requisitos y los pasos ya solicitados no requieren volver a acordarse.

Si todavía faltan decisiones para implementar, registrar esos pendientes en el cuerpo con el estado correspondiente. Preparar el contrato al resolverlos, sin bloquear el registro solicitado ni volver a preguntar ahora por lo que el usuario ha pospuesto.

Respetar el formato o firma exigidos por el repositorio. Al publicar, enlazar el brief desde el cuerpo. Si hay un brief vigente, editar ese comentario en vez de crear otro contrato.

## Contrastar y cerrar pendientes

Reutilizar decisiones ya tomadas y, para issues existentes, leer body, comentarios y notas de triage antes de formular preguntas. Buscar por concepto de dominio si el comportamiento solicitado ya existe; consultar rechazos previos documentados cuando el repo disponga de ellos. Si existe, comprobar si el reporte describe una regresión o un caso distinto antes de descartar la creación.

Para bugs, intentar verificar el caso con evidencia existente o una reproducción de solo lectura dentro del alcance autorizado. Registrar si está confirmado, no reproducido o faltan datos. Un reporte suficiente puede dejar lista la investigación del bug sin acceso a producción; si ese acceso es indispensable para comenzar, explicitar el bloqueo.

Preguntar solo por decisiones o datos que cambien el resultado, el alcance o la posibilidad de validarlo. Registrar lo resuelto y formular pendientes concretos, sin inventar respuestas para obtener el label.

## Estado

Mapear los estados a las convenciones locales y mantener un único estado canónico de triage:

- `ready-for-agent`: especificación suficiente y trabajo ejecutable por un agente.
- `needs-info`: falta un dato concreto del reportador necesario para avanzar.
- `needs-triage`: queda pendiente evaluar la petición.
- `ready-for-human`: el trabajo requiere ejecución humana; explicar el motivo.

Conservar las etiquetas locales de alcance o bloqueo que tengan significado propio. `needs-discussion` expresa una decisión de alcance pendiente; resolverla antes de recomendar `ready-for-agent`. Declarar las dependencias como bloqueos cuando impidan empezar. Añadir un comentario a una duplicada no cambia por sí solo su estado: reevaluar la issue completa y cambiarlo únicamente dentro del alcance autorizado.
