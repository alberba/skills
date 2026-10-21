---
name: create-issue
description: Crear issues de GitHub desde un repositorio local, individualmente o en lote; añadir contexto a issues existentes cuando el reporte corresponda.
---

# Crear issues de GitHub

## 1. Resolver destino y alcance

Recuperar la descripción del mensaje y del contexto previo. Si no hay una descripción identificable, pedirla antes de preparar acciones.

Resolver `ORG/REPO` desde el destino indicado por el usuario, la configuración local del tracker y los remotos Git. Si configuración y remoto discrepan, verificar el repositorio vigente en GitHub; preguntar solo si persiste una ambigüedad de destino. Usar `--repo ORG/REPO` en las operaciones.

Separar problemas con alcance independiente, aunque aparezcan en una sola descripción. Los bullets de pasos o criterios de un mismo problema pertenecen a una sola issue. Cada reporte queda asociado a una acción y un destino; incluir comentarios en issues existentes cuando el usuario los solicite.

## 2. Contrastar duplicadas y relacionadas

Buscar issues abiertas y cerradas por términos del problema, componente y partner. Ampliar a otros repositorios cuando el usuario los señale o el contexto indique que allí puede estar la incidencia. Leer título y body de los candidatos; consultar comentarios cuando afecten al diagnóstico o estado.

- **Duplicada:** mismo problema y alcance ya cubiertos. Informar URL y estado; preparar un comentario solo si aporta contexto nuevo o el usuario lo solicita. Una issue cerrada requiere comprobar si el reporte es una recurrencia, sin reabrirla automáticamente.
- **Relacionada:** problemas conectados con alcance distinto. Proponer la referencia con URL; usar `ORG/REPO#N` si pertenece a otro repo.
- **Sin coincidencias:** continuar. Si la búsqueda falla o queda incompleta, comunicar la limitación sin afirmar que no existen duplicadas.

Compartir un síntoma, como un error 502, no basta para clasificar una duplicada. Al terminar, cada reporte queda resuelto como creación, comentario o duplicada sin acción.

## 3. Preparar acciones

Leer las convenciones del tracker y los templates del repositorio. Inferir el tipo por la intención global (`bug`, `feature`, `task`, `epic`), usando `task` cuando ninguna domine; mapearlo al template y al nombre real del label local.

Explorar el código en solo lectura hasta identificar el componente relevante y las referencias que sustentan el reporte. Si no se localiza, preparar la issue con la información disponible y señalar esa limitación. Separar hechos reportados, observaciones verificadas, hipótesis y propuestas de solución.

Seguir el template correspondiente, incluidos sus campos y prefijo de título. Si no existe, usar `## Descripción` y `## Notas técnicas`. Conservar como pendientes los datos desconocidos; formular criterios de aceptación derivados del comportamiento solicitado.

Cuando el alcance permita comenzar la implementación, preparar el comentario `Agent Brief` siguiendo [Preparación para agentes](references/ready-for-agent.md): reporte breve en el cuerpo y especificación de implementación en un comentario `Agent Brief`, con criterios verificables y decisiones de alcance resueltas. Resolver con el contexto y el código lo que sea posible; reunir las preguntas que realmente bloqueen la implementación. Si el usuario prefiere registrar la issue antes de resolverlas, conservar lo establecido y los pendientes con el estado de triage correspondiente.

Consultar los labels existentes y aplicar la taxonomía documentada del repo, respetando sus nombres exactos y los ejes obligatorios (p. ej. partner o módulo). Proponer la prioridad según las convenciones locales y el impacto conocido. Crear labels ausentes solo cuando la convención lo requiera o el usuario lo autorice; si falta un dato obligatorio o un permiso, mostrarlo como pendiente.

Si el usuario pega imágenes/vídeo o menciona sus rutas, leer [Adjuntos](references/adjuntos.md) para asociarlos, inspeccionarlos y preparar su ubicación. Esta rama usa ficheros existentes; la captura de media nueva pertenece a otro flujo.

La preparación termina cuando cada acción tiene destino, título/body, brief o comentario aplicable, labels, adjuntos, estado recomendado y pendientes identificados. La autorización para crear una issue incluye publicar su brief cuando esté preparada para implementación. Si solo se registra una petición con decisiones pendientes, conservar esas decisiones en el cuerpo y el estado de triage correspondiente; el brief se prepara al resolverlas.

## 4. Presentar decisiones pendientes

Mostrar el resultado concreto antes de pedir aprobación: destino, acción, título/body y brief o comentario aplicable, labels, referencias y adjuntos. Indicar si queda lista para un agente o qué decisión lo impide. En lote, presentar un resumen por acción y los textos correspondientes.

Respetar la autorización explícita ya dada para publicar o comentar; no pedirla de nuevo para el mismo alcance. Si sigue pendiente, reunir la confirmación y las decisiones de contenido en una sola pregunta. Una respuesta que solo cambia un dato (p. ej. «P1») actualiza el borrador y por sí sola no confirma su publicación. Una aprobación parcial habilita únicamente las acciones aprobadas.

Publicar cuando la acción esté autorizada y sus pendientes relevantes estén resueltos. No pedir estimación temporal ni asociar issues a proyectos salvo petición expresa.

## 5. Publicar y verificar

Escribir el texto exacto en un fichero temporal y pasarlo mediante `--body-file` a `gh issue create` o `gh issue comment`. Pasar título, labels y rutas como argumentos correctamente escapados; gestionar el temporal separado del comando de publicación.

Crear la issue sin `ready-for-agent`. Si está preparada para implementar, publicar el brief, enlazar su comentario desde el cuerpo y verificar ambos. Después establecer `ready-for-agent`, sustituyendo el estado canónico anterior según la taxonomía local y conservando las demás etiquetas aplicables.

Si se interrumpe la publicación, consultar el estado remoto y completar solo lo pendiente. Reutilizar la issue, adjuntos y comentario existentes aunque la llamada de creación terminase con error o timeout. Confirmar que no existen antes de repetir una creación. Registrar las URLs de los recursos publicados.

Verificar en GitHub el cuerpo, brief, enlace entre ambos, labels, referencias y adjuntos aplicables. En lote, reanudar únicamente acciones pendientes. Terminar con las URLs publicadas y cualquier pendiente concreto; distinguir publicación verificada de verificación incompleta.
