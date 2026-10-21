# Preparación para agentes

Una issue está `ready-for-agent` cuando un agente puede comenzar sin pedir decisiones de producto o alcance y puede comprobar cuándo ha terminado. La ausencia de una causa raíz o de una implementación prescrita no impide ese estado si el problema y el resultado solicitado están definidos.

## Reporte y brief

El **cuerpo** sigue el template del repositorio y permite entender el reporte de una lectura: problema, comportamiento esperado, caso concreto y adjuntos. Termina con un enlace al brief cuando esté publicado.

El comentario **Agent Brief** aporta las decisiones necesarias para implementar y comprobar el resultado. El cuerpo explica al lector qué falla; el brief se apoya en ese reporte y añade solo lo que falte. Usa párrafos y criterios concretos proporcionados al problema.

Ejemplo de una corrección sencilla:

- Cuerpo: «El selector de idioma pierde el valor elegido al volver a abrir el formulario. Debe conservarlo» más los campos obligatorios del template.
- Comentario: «## Agent Brief
Alcance: conservar el idioma guardado al reabrir el formulario. Aceptación: el idioma guardado reaparece al abrirlo; cambiarlo y guardar actualiza la selección». Solo añade hallazgos si condicionan esta corrección.

En un caso complejo, añade el contraste de datos que explica el fallo y los límites acordados. Una lista larga de observaciones del diagnóstico no es una especificación más completa.

Añadir reproducción, dependencias o accesos solo cuando sean necesarios para comenzar o validar. Referenciar las guías operativas existentes. Conservar las decisiones de la conversación que condicionen la tarea; resumir la investigación en lugar de transcribirla. La evidencia extensa imprescindible puede ir en un bloque desplegable del mismo comentario.

Si el repositorio exige otra estructura de brief o una firma, respetarla. Al actualizarlo, editar el comentario vigente y mantener el enlace del cuerpo.

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
