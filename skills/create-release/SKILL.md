---
name: create-release
description: Preparar y publicar releases de GitHub, estables o prereleases, con versión semántica y notas basadas en los cambios reales.
---

# Crear una release

Usa las instrucciones y convenciones del repositorio. Resuelve el repositorio y su rama principal en GitHub; consulta allí ramas, tags, releases, commits y PR, sin modificar el checkout ni sus referencias. La rama objetivo es la principal para una release estable (por defecto) y la rama de pruebas indicada por el proyecto para una beta; verifica que existe. Si no está definida, pregunta cuál usar.

## Preparar

1. Busca el último tag estable y la versión de la rama objetivo. Compara ambos en GitHub y comprueba que el rango está completo y que el tag es antecesor de la rama. Si no hay base estable o el rango no puede establecerse, explica la incertidumbre antes de proponer una versión.
2. Identifica todos los cambios del rango y las PR asociadas, incluidos commits directos. Expande las PR que agrupan ramas en sus PR individuales, contrastando referencias con los commits incluidos; conserva los cambios sin PR. Usa el título, cuerpo y diff como evidencia, no solo los prefijos de commit.
3. Propón la siguiente versión según el impacto acumulado: patch para correcciones, rendimiento y mantenimiento compatible; minor para capacidades nuevas compatibles destinadas a usuarios del producto; major para cambios incompatibles. Las herramientas de operación o desarrollo son mantenimiento aunque usen `feat`. Respeta la convención de tags del repositorio y sus reglas de versionado si difieren.
4. Para una beta usa la versión destino seguida de `-beta.N`, con N igual al mayor contador existente para esa versión más uno. Comprueba también tags sin release y evita colisiones. Las notas abarcan todo el rango desde la última estable y añaden los cambios desde la beta anterior de esa versión. Si no hay cambios incrementales, avisa antes de publicar. Si la versión destino cambia respecto de betas anteriores, explica el salto; conserva las betas anteriores.
5. Redacta las notas en español, salvo que el proyecto indique otro idioma, siguiendo su plantilla y convenciones. Categoriza cada cambio por su impacto y audiencia: nuevas funcionalidades de producto, correcciones, rendimiento, seguridad o mantenimiento; añade documentación si la convención la contempla. Omite secciones vacías, enlaza issues y PR, y enumera todas las PR individuales incluidas. Para betas identifica la subida; las notas estables cubren el rango desde la estable anterior sin mencionar betas. Aplica los criterios editoriales del proyecto cuando existan.

## Confirmar y publicar

Presenta el modo, tag, rama, SHA objetivo y notas completas, con riesgos o dudas materiales. Para betas indica el contador, las betas previas y el rango incremental. Solicita confirmación explícita de la propuesta antes de publicar. Si una clasificación o versión sigue siendo ambigua, resuélvela con el usuario.

Crea la release apuntando al SHA revisado, no al nombre de la rama; marca las betas como prerelease. Comprueba en GitHub la URL, tag, commit, publicación y estado de prerelease. Si falla la creación, comprueba si existe antes de reintentar. No edites ni elimines betas al publicar una estable. Desplegar es una operación independiente: solo ejecútala si el usuario la pide; si el proyecto documenta cómo desplegar el tag beta, comunica el comando.
