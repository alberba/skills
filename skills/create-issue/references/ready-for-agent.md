# Preparación para agentes

Una issue está `ready-for-agent` cuando un agente puede comenzar sin pedir decisiones de producto o alcance y puede comprobar cuándo ha terminado. La ausencia de una causa raíz o de una implementación prescrita no impide ese estado si el problema y el resultado solicitado están definidos.

## Reporte y brief

El **cuerpo** sigue el template del repositorio: empezar por el efecto del problema para el usuario, aportar un caso concreto con las discrepancias relevantes y expresar el resultado esperado. Distinguir el impacto reportado del alcance comprobado. Conservar los adjuntos y terminar con un enlace al brief cuando esté publicado.

El comentario **Agent Brief** sigue el enfoque de triage: es la especificación autosuficiente y el contrato de implementación; el reporte y la discusión aportan contexto. Su extensión viene determinada por lo necesario para implementar y validar, sin objetivos de compactación ni límites de palabras. Puede retomar los hechos del cuerpo que necesite para entenderse por sí solo.

```markdown
## Agent Brief

**Categoría:** tipo de tarea según el tracker.
**Resumen:** resultado que debe conseguirse.

**Comportamiento actual:**
Qué ocurre, con el caso y la evidencia relevantes. Distinguir lo verificado,
lo reportado y las hipótesis.

**Comportamiento deseado:**
Qué debe ocurrir después del cambio, incluidos los casos límite y errores
que formen parte del alcance acordado.

**Interfaces clave:**
Conceptos, tipos, funciones o configuración implicados y sus contratos.

**Criterios de aceptación:**
- [ ] Resultados concretos, completos y verificables de forma independiente.

**Fuera de alcance:**
Trabajo adyacente que no forma parte de esta tarea.
```

Describir el comportamiento y los contratos, dejando la implementación al agente. Nombrar interfaces y tipos que permitan orientarse aunque el código cambie; evitar recetas basadas en rutas de código, números de línea o una estructura interna que pueda quedar obsoleta.

Conservar en el brief las decisiones de la conversación, la reproducción y la evidencia necesarias para ejecutar el trabajo sin reconstruir toda la discusión. Añadir dependencias y accesos cuando condicionen el comienzo o la validación; enlazar las guías operativas existentes. Los hallazgos adyacentes no amplían por sí solos el alcance acordado.

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
