---
name: create-issue
description: Crear issues de GitHub desde reportes locales y añadir evidencia a incidencias existentes.
---

# Crear issues de GitHub

## Resolver y contrastar

Recuperar el reporte y la autorización del contexto. Resolver ORG/REPO con el destino indicado, tracker local y remoto Git; contrastar discrepancias y preguntar solo si persiste ambigüedad. Usar `gh` con `--repo ORG/REPO`.

Leer las convenciones y el template aplicable. Buscar duplicadas abiertas y cerradas antes de redactar; listar primero título, número y estado, y abrir los candidatos relevantes. Buscar también en otros repos si el contexto los señala.

- Mismo problema abierto: informar su URL; añadir comentario si está solicitado o aporta evidencia nueva dentro del alcance autorizado.
- Antecedente cerrado: comprobar recuperación y recurrencia; no reabrir automáticamente.
- Relacionada con alcance distinto: referenciarla sin fusionar reportes.

Si la búsqueda queda incompleta, indicar esa limitación. Separar problemas independientes y mantener juntos pasos y criterios del mismo resultado.

## Preparar

Explorar el componente relevante en solo lectura, sin convertir la creación en una implementación. Distinguir reporte, evidencia verificada e hipótesis; conservar discrepancias y relacionar identificadores solo cuando lo acrediten los datos. La causa desconocida no impide registrar un bug investigable.

Redactar el cuerpo con el template y prefijo del repo: problema, resultado esperado, caso concreto y adjuntos. Sin template usar `## Descripción` e `## Información adicional`. Mantenerlo legible de una lectura. Para alcance resuelto, preparar un comentario Agent Brief según [Preparación para agentes](references/ready-for-agent.md); para decisiones pendientes, registrar lo acordado y el pendiente concreto en el cuerpo.

Consultar labels y aplicar los ejes obligatorios de la taxonomía local. Inferir tipo y prioridad del reporte; conservar las elecciones del usuario. Crear labels solo si la convención o el usuario lo autorizan. Usar el estado que corresponda a la información disponible.

Si hay imágenes o vídeos existentes, leer [Adjuntos](references/adjuntos.md). Preparar textos, labels, referencias, adjuntos y pendientes antes de pedir una decisión.

## Publicar y verificar

Respetar la autorización vigente: una petición de crear habilita crear y publicar el brief aplicable; un cambio de prioridad no revoca una instrucción de dejarlo en borrador. Reunir solo las decisiones que realmente impidan avanzar. No pedir tiempo de commit ni añadir proyectos por defecto.

Guardar el texto exacto en temporales y usar `--body-file`. Crear la issue sin `ready-for-agent`; si está preparada, publicar el brief, enlazar el comentario desde el cuerpo y verificarlo. Después sustituir el estado canónico anterior por `ready-for-agent`, conservando las demás etiquetas aplicables.

Tras un error o timeout, consultar los recursos remotos y completar solo la operación pendiente. Reutilizar issue, adjuntos y comentario si ya existen; comprobar su ausencia antes de repetir una creación.

Verificar texto, brief, enlace, labels y adjuntos. Terminar con las URLs y cualquier pendiente concreto. En lote, registrar cada resultado y continuar únicamente los pendientes.
