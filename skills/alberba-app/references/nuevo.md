# Proyecto nuevo

## 1. Generar el esqueleto

Ejecutar el generador oficial en su última versión. Antes, `<generador> --help` para ver las banderas de hoy y evitar preguntas interactivas.

| Stack | Generador |
| --- | --- |
| Astro | `pnpm create astro@latest` |
| TanStack Start | `pnpm dlx @tanstack/cli@latest create`, con React, TypeScript y pnpm |
| React con Vite y TanStack Router | `pnpm dlx @tanstack/cli@latest create --router-only`, con TypeScript y pnpm |
| Python | `uv init` |

Los generadores instalan dependencias de hace semanas. Después de generar, subir todo a la última con `pnpm up --latest` o `uv lock --upgrade`.

Para TanStack, comprobar las opciones vigentes en la [documentación oficial del CLI](https://tanstack.com/cli/latest/docs/quick-start) y en su `--help`; elegir Vite y solo los complementos que requiera el proyecto.

Hecho = el proyecto arranca (`pnpm dev` o `uv run`), su gestor es pnpm o uv, y `pnpm outdated` o `uv tree --outdated` no lista nada que la ventana de edad permita instalar.

## 2. Piezas opcionales

Montar cada pieza elegida en el arranque (Better Auth, Drizzle, Postgres, push, worker) leyendo su documentación actual. Organizar auth, acceso a datos y migraciones según las convenciones del stack elegido; mantener credenciales y acceso directo a la base de datos en el servidor.

Si el proyecto lleva TypeScript: `pnpm add effect`.

Hecho = cada pieza elegida funciona con una prueba mínima, y la migración inicial está versionada.

## 3. Capa común

Seguir la sección 4 de `SKILL.md`. El orden en Node es este: generar, añadir el control de edad al `pnpm-workspace.yaml` (crearlo si falta), `pnpm up --latest`, y resolver los rechazos como indica [Versiones](versiones.md). Conservar las instrucciones para agentes que incluya el generador.
