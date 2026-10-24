# Proyecto existente

Las herramientas del proyecto se mantienen. Dos migraciones se aplican siempre: npm a pnpm y pip a uv.

## 1. Informe de diferencias

Leer el proyecto (gestor, `pubspec.yaml`, lockfile, bot de dependencias, CI, tests, `Dockerfile`, `DESIGN.md`) y comparar con las reglas de la sección 2 de `SKILL.md`. Emitir una tabla con una fila por regla: cumple, falta, o difiere con la decisión del proyecto como motivo.

Hecho = una fila por regla, sin reglas omitidas.

## 2. Migrar el gestor

- npm a pnpm: `pnpm import` desde `package-lock.json`, borrar el lockfile de npm, fijar `packageManager` en `package.json`, y cambiar los comandos de scripts, CI y `Dockerfile`.
- pip a uv: `uv init` si falta `pyproject.toml`, pasar los requisitos con `uv add -r requirements.txt`, borrar el fichero viejo y cambiar los comandos de CI y `Dockerfile`.

pnpm 11 no ejecuta los scripts de instalación de las dependencias: `pnpm install` deja en `pnpm-workspace.yaml` un `allowBuilds` con cada paquete por decidir. Poner `true` a los que el proyecto necesita (`esbuild`, `workerd`) y `false` al resto (`sharp`, `unrs-resolver`), y volver a ejecutar `pnpm install --frozen-lockfile`.

Hecho = install congelado, tests y build pasan con el gestor nuevo, y el lockfile antiguo ya no está.

## 3. Añadir lo que falta

Seguir la sección 4 de `SKILL.md` solo para las filas «falta» del informe. Un `DESIGN.md`, `ci.yml` o `dependabot.yml` existente recibe una propuesta con las secciones ausentes, que el usuario aprueba antes de escribirla.

Las versiones antiguas de acciones, Node o dependencias del proyecto van en el informe como «difiere»; Dependabot las sube con sus PR.

Effect se añade a un proyecto TypeScript existente cuando el usuario lo pide.
