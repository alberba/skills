---
name: create-release
description: Preparar y publicar releases de GitHub estables o betas, con versión semántica y notas basadas en los cambios reales. Usar también para prereleases, al pedir subir a pruebas o para revisar qué falta antes de una subida.
---

# Crear una release

Trabaja en GitHub en solo lectura: ramas, tags, releases, commits y PR se consultan allí, con el checkout y sus referencias intactos. Antes de empezar, localiza las convenciones de release del proyecto (`docs/agents/releases.md`, `AGENTS.md`, la plantilla de PR y la documentación de despliegue): rama candidata, plantilla de notas, canales editoriales, valores ligados a la versión y vía de despliegue. Lo que el proyecto no documente se dice en la propuesta.

## 1. Modo y rango

El modo es **estable** (por defecto), **beta** o **revisión previa**. La revisión previa responde a «qué falta antes de la subida»: recorre los pasos 1 a 5 y entrega el resultado sin publicar. En modo beta, lee también [Betas](references/beta.md).

La candidata es la rama principal para una estable. Si el proyecto integra el sprint en una rama propia (`release/*` u otra documentada) que aún no está fusionada, la candidata es esa rama: la revisión se hace sobre ella y la estable se publica después de la fusión. Elige la que nombre el usuario; si no nombra ninguna, la rama de integración más reciente sin fusionar que tenga commits fuera de la base; si hay más de una posible, pregunta. En una beta, la candidata es la rama de pruebas del proyecto. Verifica que existe; si no está definida, pregunta cuál usar.

La base es el último tag estable. El rango son los commits alcanzables desde la candidata y no desde la base (`<tag>..<candidata>`). Lista también los commits de la rama principal que no están en la candidata, incluidos los de tags estables publicados después de que la candidata se separase: sin ellos la candidata no sustituye a la principal, y traerlos encabeza los pendientes.

Rango listo = base, candidata con su SHA y lista de la principal fuera de la candidata («nada» incluido). Si no hay base estable o el rango no puede establecerse, explica la incertidumbre antes de proponer versión.

## 2. Cambios

Identifica todos los cambios del rango. Expande las PR que agrupan ramas, y las apiladas sobre otra rama, en sus PR individuales, contrastando sus referencias con los commits incluidos. Los commits sin PR se conservan como tales. La evidencia es el título, el cuerpo y el diff, más allá del prefijo del commit.

Cambios listos = cada commit del rango pertenece a una PR identificada o figura como commit sin PR.

## 3. Versión

Propón la siguiente versión por el impacto acumulado: patch para correcciones, rendimiento y mantenimiento compatible; minor para capacidades nuevas compatibles destinadas a usuarios del producto; major para cambios incompatibles. Las herramientas de operación o desarrollo cuentan como mantenimiento aunque usen `feat`. La convención de tags y las reglas de versionado del repositorio prevalecen.

## 4. Preflight

El preflight es lo que debe estar hecho o previsto para que la versión salga sin parches al día siguiente. Recorre cada PR y cada commit sin PR del rango y llena tres listas:

- **Contenido pendiente**, por cada canal editorial que el proyecto define (por ejemplo novedades, tour, FAQ o documentación), leyendo el bloque correspondiente de la PR. Cuenta como pendiente lo marcado como trabajo pendiente, lo enlazado a una issue o borrador sin cerrar y el cambio funcional sin bloque. Comprueba en GitHub el estado de cada issue enlazada, también en otros repositorios.
- **Pasos de despliegue**: los que declaran las PR y los que revela el diff. Busca migraciones de esquema o datos (y si revierten sin pérdida), cambios de índices de búsqueda, variables de entorno o secretos nuevos, tareas periódicas nuevas o retiradas y comandos de una sola vez. Cada paso lleva la vía de despliegue que el proyecto documenta para ese caso.
- **Valores ligados a la versión**: los que el proyecto declara, como manifests de novedades, constantes de versión o changelog, comparados con la versión propuesta.

Preflight completo = cada PR y cada commit sin PR del rango con su resultado en las tres listas, «nada» incluido. Lo que no hayas podido verificar queda como pendiente con su motivo.

## 5. Notas

Redacta las notas en español, salvo que el proyecto indique otro idioma, con su plantilla y convenciones. Categoriza cada cambio por impacto y audiencia: nuevas funcionalidades de producto, correcciones, rendimiento, seguridad o mantenimiento; documentación si la convención la contempla. Incluye solo las secciones con cambios, enlaza issues y PR y enumera todas las PR individuales. Las notas estables cubren el rango desde la estable anterior, sin mencionar betas. Aplica los criterios editoriales del proyecto cuando existan. El preflight va en las notas solo si la plantilla tiene sección para él; si no, acompaña a la propuesta.

## 6. Confirmar y publicar

Presenta modo, tag, candidata, SHA objetivo, el preflight con lo pendiente primero, las notas completas y los riesgos o dudas materiales. En una revisión previa, la entrega termina aquí.

Pide confirmación explícita antes de publicar y resuelve con el usuario cualquier clasificación o versión ambigua. Una estable se publica sobre un SHA de la rama principal: si la candidata está sin fusionar, la publicación espera a la fusión y repite el rango sobre el SHA fusionado.

Crea la release sobre el SHA revisado, nunca sobre el nombre de una rama. Comprueba en GitHub URL, tag, commit, publicación y estado de prerelease. Si la creación falla, comprueba si la release existe antes de reintentar. Al publicar una estable, las betas existentes se conservan tal cual.

El despliegue es una operación aparte y se ejecuta solo a petición del usuario. Al cerrar, entrega los pasos de despliegue del preflight con los comandos que documenta el proyecto y las tareas posteriores que describa, como el anuncio de novedades.
