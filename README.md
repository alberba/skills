<div align="center">

# Skills

**Mi colección de flujos para agentes de código.**

Issues con contexto, vídeos de producto y pruebas para seguir mejorándolos.

[![Checks](https://github.com/alberba/skills/actions/workflows/check.yml/badge.svg?branch=main)](https://github.com/alberba/skills/actions/workflows/check.yml)
[![Instalar con skills.sh](https://img.shields.io/badge/instalar-skills.sh-111827?style=flat)](#instalación)
[![Benchmarks](https://img.shields.io/badge/benchmarks-casos%20y%20resultados-6366f1?style=flat)](#evaluaciones)

[Catálogo](#catálogo) · [Instalación](#instalación) · [Evaluaciones](#evaluaciones) · [Desarrollo local](#desarrollo-local)

</div>

---

## Catálogo

| Skill | Para qué sirve | Ejemplo de petición |
| --- | --- | --- |
| [**create-issue**](skills/create-issue/SKILL.md) | Crear issues de GitHub con el impacto para el usuario en el cuerpo y el Agent Brief en un comentario separado. | «Crea una issue para este error, con contexto suficiente para implementarlo.» |
| [**product-video**](skills/product-video/SKILL.md) | Grabar demos, recorridos y novedades de una aplicación web, con voz, subtítulos y montaje en HyperFrames. | «Prepara un vídeo que explique este recorrido del producto.» |
| [**review-pr**](skills/review-pr/SKILL.md) | Revisar una PR buscando defectos de producción y publicar una review breve, con el detalle en comentarios inline. | «Revisa la PR 123.» |
| [**alberba-app**](skills/alberba-app/SKILL.md) | Empezar una app con las mismas reglas de siempre (pnpm o uv, Dependabot, Effect, Astro o TanStack según el proyecto, `DESIGN.md`, PWA y app Android con Flutter) o adoptarlas en un proyecto existente. | «Empieza una app nueva para llevar mis gastos.» |
| [**chromecast-launcher**](skills/misc/chromecast-launcher/SKILL.md) | Limpiar un Chromecast con Google TV por ADB inalámbrico, instalar un launcher propio y hacer que Home lo abra. | «Pon un launcher propio en mi Chromecast.» |

Cada skill incluye sus instrucciones y, cuando hacen falta, referencias y scripts. `product-video` configura el acceso, la privacidad, la voz y la marca por proyecto.

## Instalación

Desde el proyecto donde quieras usarlas:

```sh
npx skills add alberba/skills
```

El asistente permite elegir las skills y los agentes. **Este repositorio es privado:** necesitas acceso mediante tu autenticación de Git, GitHub CLI o SSH.

<details>
<summary><strong>Instalar una skill globalmente para Codex</strong></summary>

```sh
npx skills add alberba/skills --skill create-issue --agent codex --global
npx skills add alberba/skills --skill product-video --agent codex --global
```

Instala la que necesites. Para otros agentes, usa la selección del asistente.

</details>

<details>
<summary><strong>Listar skills y actualizar las instaladas</strong></summary>

```sh
npx skills add alberba/skills --list
npx skills update
```

Consulta los comandos en la [documentación de skills.sh](https://github.com/vercel-labs/skills/blob/main/docs/commands.md).

</details>

> **Para crear vídeos:** `product-video` utiliza Playwright, FFmpeg, HyperFrames y ElevenLabs. La API key se configura en el entorno o en el `.env.local` del vídeo; la voz se selecciona por su ID. La [guía de voz](skills/product-video/references/voz.md) explica la configuración y cómo conservar una voz ya aprobada.

## Evaluaciones

Las skills se acompañan de casos, criterios y ejecuciones guardadas. Cada resultado identifica la revisión o el digest evaluado: los cambios posteriores no heredan esa puntuación.

<details>
<summary><strong>create-issue · 26 casos sintéticos y ejecuciones por modelo</strong></summary>

Evalúa redacción, alcance, autorización, duplicadas, recuperación e instrucciones inyectadas en la evidencia. Combina comprobaciones automáticas con una rúbrica para revisión semántica.

[Cómo ejecutarlo](benchmarks/create-issue/README.md) · [Resultados por modelo](benchmarks/create-issue/results.md) · [Rúbrica](benchmarks/create-issue/rubric.md)

</details>

<details>
<summary><strong>product-video · 15 escenarios y 12 pruebas del kit</strong></summary>

Los escenarios cubren portabilidad, intro aprobada, voz, sincronía, continuidad, privacidad y móvil. Las pruebas del kit usan Chromium y FFmpeg reales, con datos sintéticos y una sustitución local del proveedor de voz.

Los resultados distinguen las regresiones del código de la evaluación de planes de un agente. No equivalen a validar un vídeo final ni la API real de ElevenLabs.

[Cómo ejecutarlo](benchmarks/product-video/README.md) · [Resultados y límites](benchmarks/product-video/results.md) · [Retrospectiva](benchmarks/product-video/retro.md)

</details>

<details>
<summary><strong>review-pr · 8 ejecuciones sobre 2 PRs reales</strong></summary>

Compara versiones de la skill con una revisión sin skill: precisión de los hallazgos, cobertura, coste, tiempo y diez reglas de publicación. El corpus es privado; se publican el método, las métricas y las conclusiones.

[Método](benchmarks/review-pr/README.md) · [Resultados](benchmarks/review-pr/results.md) · [Rúbrica](benchmarks/review-pr/rubric.md) · [Retrospectiva](benchmarks/review-pr/retro.md)

</details>

Una sola ejecución sirve para detectar fallos; comparar modelos o versiones requiere repetir con el mismo corpus y revisar sus salidas.

## Desarrollo local

```text
skills/
  alberba-app/        Reglas de arranque, plantillas y referencias para empezar o adoptar una app
  create-issue/       Instrucciones y referencias para crear issues
  product-video/      Instrucciones, referencias y scripts de vídeo
  review-pr/          Instrucciones de revisión y publicación
  misc/
    chromecast-launcher/  Limpieza, launcher y Home de un Chromecast con Google TV
benchmarks/
  create-issue/       Casos, comprobaciones y resultados
  product-video/      Casos, pruebas del kit y resultados
  review-pr/          Método, rúbrica y resultados
```

Para probar cambios locales, sustituye `alberba/skills` en el comando de instalación por la ruta absoluta de este clon. Cada skill se descubre desde `skills/<nombre>/SKILL.md`; sus recursos viven en la misma carpeta.

El workflow de [Checks](https://github.com/alberba/skills/actions/workflows/check.yml) ejecuta Ruff y las pruebas del kit de vídeo. Los comandos para repetir cada evaluación están en el README de su benchmark.
