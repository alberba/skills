# Proyecto nuevo

## 1. Generar el esqueleto

Ejecutar el generador oficial en su última versión. Antes, `<generador> --help` para ver las banderas de hoy y evitar preguntas interactivas.

| Stack | Generador |
| --- | --- |
| Astro | `pnpm create astro@latest` |
| Next | `pnpm create next-app@latest`, con TypeScript, ESLint, Tailwind, App Router y `src/` |
| Python | `uv init` |

Los generadores instalan dependencias de hace semanas. Después de generar, subir todo a la última con `pnpm up --latest` o `uv lock --upgrade`.

Hecho = el proyecto arranca (`pnpm dev` o `uv run`), su gestor es pnpm o uv, y `pnpm outdated` o `uv tree --outdated` no lista nada que la ventana de edad permita instalar.

## 2. Piezas opcionales

Montar cada pieza elegida en el arranque (Better Auth, Drizzle, Postgres, push, worker) leyendo su documentación actual. Tomar de `nas-dashboard` la estructura (`src/lib/auth.ts`, `db.ts`, `schema.ts`, `scripts/migrate.ts`, `drizzle/`) y escribir el código con las APIs de hoy.

Si el proyecto lleva TypeScript: `pnpm add effect`.

Hecho = cada pieza elegida funciona con una prueba mínima, y la migración inicial está versionada.

## 3. Capa común

Seguir la sección 4 de `SKILL.md`. El orden en Node es este: generar, añadir el control de edad al `pnpm-workspace.yaml` que ya crea el generador, `pnpm up --latest`, y resolver los rechazos como indica [Versiones](versiones.md). Next trae su propio `AGENTS.md`: se queda como está.
