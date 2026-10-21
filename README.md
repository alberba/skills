# Skills personales

Repositorio privado de skills y sus evaluaciones.

- [create-issue](skills/create-issue/SKILL.md): creación de issues con un reporte centrado en el impacto para el usuario y un Agent Brief completo en un comentario separado.
- [Benchmarks de create-issue](benchmarks/create-issue/README.md): casos sintéticos, variantes, resultados y rúbricas, sin datos de incidencias reales.

La skill vigente está en `skills/`. Las copias dentro de `benchmarks/` son variantes históricas para comparar; no representan la versión elegida para uso habitual.

El cuerpo de la issue sigue el template del repositorio de destino. El Agent Brief conserva la estructura de triage y todo el detalle necesario para implementar y validar, sin límites de palabras.

## Instalar con skills.sh

Usar el [CLI de skills.sh](https://github.com/vercel-labs/skills/blob/main/docs/commands.md) desde el proyecto donde se quiera instalar:

```sh
npx skills add alberba/skills
```

El asistente permite elegir las skills y los agentes. Para instalar `create-issue` globalmente para Codex:

```sh
npx skills add alberba/skills --skill create-issue --agent codex --global
```

Al ser un repositorio privado, hace falta acceso mediante la autenticación de Git, GitHub CLI o SSH.

Para descubrir las skills disponibles y actualizar las instaladas:

```sh
npx skills add alberba/skills --list
npx skills update
```

Para probar cambios locales, sustituir `alberba/skills` por la ruta absoluta de este clon. Cada skill vive en `skills/<nombre>/SKILL.md`, con frontmatter `name` y `description`; sus referencias y recursos se guardan dentro de la misma carpeta.
