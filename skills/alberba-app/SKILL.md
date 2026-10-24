---
name: alberba-app
description: Empezar una app nueva con las reglas de alberba (pnpm o uv, Dependabot, Effect, Astro o Next, DESIGN.md), o adoptar esas reglas en un proyecto existente.
---

# Empezar una app

## 1. Arranque

Hacer una sola ronda con estas preguntas, cada una con su default para aceptar con «sí»:

1. Nombre y propósito en una frase. Default: el nombre del directorio.
2. Piezas opcionales: auth (Better Auth), Postgres (Drizzle), push o worker. Default: las que pida el tipo de proyecto de la tabla.
3. Ambiente visual en una frase y color de acento, solo si lleva interfaz.
4. ¿Proyecto nuevo o existente? Default: existente si el directorio tiene `package.json`, `pyproject.toml` o `.git` con commits.

Hecho = las cuatro respuestas anotadas y el tipo de proyecto fijado con la tabla de la sección 2.

## 2. Reglas

Estas reglas deciden cada elección de arranque.

| Proyecto | Stack |
| --- | --- |
| Página estática o de contenido | Astro. Con interacción, una isla de React |
| App con interacción, login o base de datos | Next, React, Better Auth, Drizzle y Postgres. `nas-dashboard` (github.com/alberba/nas-dashboard) es la referencia de estructura |
| Servicio o script en Python | `uv`, `ruff` y `pytest` |
| Cualquier otro | Las reglas comunes; el resto, preguntarlo |

- Node usa `pnpm`. Python usa `uv`.
- Todo va en la última versión estable: librerías, Node, Python, Postgres, imágenes Docker y acciones de CI. Para resolverlas, seguir [Versiones](references/versiones.md). Si una herramienta no soporta la última de otra, fijar solo esa pieza con un comentario que diga por qué y cuándo quitarla.
- Si lleva TypeScript, usar Effect.
- Dependabot cubre pnpm (ecosistema `npm`) o `uv`, `docker` y `github-actions`. Un bot de dependencias ya configurado, como Renovate, cuenta como cumplido.
- Las dependencias nuevas esperan su ventana de edad: `minimumReleaseAge` en pnpm, `exclude-newer` en uv.
- Un `.env.example` documenta el entorno; `.env*` va en `.gitignore`, y los workflows usan secretos falsos marcados «solo para CI».
- Un `ci.yml` ejecuta install congelado, typecheck, lint, test, build y E2E.
- Tests: Vitest y Playwright en TypeScript, `pytest` en Python.
- Las migraciones de base de datos se versionan en el repo.
- Lo que se autohospeda lleva `Dockerfile` multi-etapa y `compose.yaml`.
- Documentación y commits en español; identificadores de código en inglés.
- Un proyecto con interfaz tiene `DESIGN.md` antes de la primera pantalla.

## 3. Modo

Nuevo: seguir [Proyecto nuevo](references/nuevo.md). Existente: seguir [Proyecto existente](references/adoptar.md).

Hecho = en nuevo, el esqueleto generado con el generador oficial en su última versión; en existente, el informe de diferencias emitido y sus migraciones de gestor aplicadas.

## 4. Capa común

Añadir lo que falte, con los ficheros de `assets/` y el detalle de [Node](references/node.md) o [Python](references/python.md) según el stack. Ante un fichero que ya existe, proponer las secciones que faltan y dejar el resto como está.

- `.github/dependabot.yml`, ensamblado con [assets/dependabot](assets/dependabot) (`header.yml` y los bloques del stack): lunes 9:00 Europe/Madrid, grupo `security` aparte, grupos por afinidad y los mayores como PR individuales.
- `.github/workflows/audit.yml`, `.github/workflows/ci.yml` y el control de edad de dependencias.
- `DESIGN.md`, si hay interfaz, rellenado según [Diseño](references/diseno.md).

Hecho = cada fichero existe, sin marcadores `{{nombre}}` sin resolver (las expresiones `${{ … }}` de GitHub Actions se quedan), y las versiones de acciones, Node, Python y Postgres son las resueltas hoy.

## 5. Verificar

Ejecutar typecheck, lint, test y build en Node, o `ruff` y `pytest` en Python. Contar lo que falla y decirlo con el número.

Hecho = cada comando ejecutado, con su resultado en el informe final.

## 6. Remoto

Crear el repo en GitHub, hacer push, crear etiquetas y activar Dependabot son acciones fuera de la máquina. Proponerlas en una lista y ejecutar solo las que el usuario confirme.

Hecho = lista propuesta; nada ejecutado sin confirmación.
