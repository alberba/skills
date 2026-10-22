---
name: product-video
description: Crear o editar demos y recorridos de aplicaciones web con grabación real, voz sincronizada y subtítulos, usando Playwright, FFmpeg e HyperFrames.
---

# Vídeos de producto

Graba la aplicación real y monta un recorrido narrado con el kit de esta
carpeta. `<SKILL_DIR>` es su ruta absoluta; `<proyecto>`, la carpeta del vídeo.

Fuentes: `STORYBOARD.md` para texto, orden y tiempos; `escenas.py` para acceso
y navegación; `diseno.py` para escenas diseñadas. Edita estas fuentes: el HTML
se regenera.

## 1. Recuperar el encargo

Recupera el guion, medios, configuración y decisiones existentes. Completa
solo lo que falte en `BRIEF.md`: público, alcance, idioma/acento, marca,
destino, duración, privacidad e importes visibles. Pregunta por huecos que
cambien la entrega; con datos sintéticos y sin importes basta documentarlo.

Usa `hyperframes` en flujo companion para preparar el proyecto. Si la skill
falta, consulta el CLI instalado y crea `hyperframes.json`; si el render no
está disponible, entrega las fuentes e indica ese límite.

## 2. Preparar guion y muestra

Lee [entorno.md](references/entorno.md) para preparar la aplicación y aislar
integraciones. Incluye solo pantallas y funciones verificadas en esa versión.

Lee [grabar.md](references/grabar.md) para escribir el storyboard y el
recorrido. En un vídeo nuevo, lleva primero un bloque representativo hasta
el preview con voz y foco antes de desarrollar los demás. Con un guion
aprobado, conserva su alcance y trabaja los bloques pendientes.

## 3. Preparar la voz

Lee [voz.md](references/voz.md) para configurar ElevenLabs y generar la
locución por escena. Comprueba acento, pronunciación y ritmo con una muestra
si la voz es nueva; conserva las elecciones y audios vigentes.

```sh
uv run --no-project --with elevenlabs python <SKILL_DIR>/scripts/voz.py <proyecto> --voz <id> --modelo <modelo> --idioma es --escuchar
```

## 4. Grabar el recorrido

```sh
uv run --no-project --with playwright python <SKILL_DIR>/scripts/grabador.py <proyecto> [NN ...]
```

Resuelve tomas fallidas y valida sincronía, continuidad y privacidad según
[grabar.md](references/grabar.md) antes de montar.

## 5. Montar y comprobar

Lee [montaje.md](references/montaje.md) para las piezas y comprobaciones del kit;
usa HyperFrames para los efectos y la revisión general.

```sh
python3 <SKILL_DIR>/scripts/montaje.py <proyecto>
cd <proyecto>
npx hyperframes check
```

Incluye todas las piezas aprobadas en el mismo storyboard y preview, también
las intros añadidas después. Revisa las uniones y compara la duración con el
brief: si una acción excede su locución, ajusta la frase o el tiempo de lectura.

## 6. Mostrar el preview y esperar aprobación

Reproduce el preview entero con sonido y aplica las notas en las fuentes.
Si no puedes revisar el audio o el corte completo, facilita el preview y deja
explícita la revisión pendiente; `check` no acredita esa revisión.

```sh
npx hyperframes preview
```

Presenta el preview completo al usuario y detente hasta que apruebe
explícitamente ese corte para exportarlo. Aprobar el guion, la voz o el encargo
no sustituye esta aprobación. Si ya aprobó ese mismo preview y sigue intacto,
continúa sin volver a preguntarlo; si cambia el corte, muestra el nuevo preview.

Tras la aprobación, sigue [la exportación](references/montaje.md#exportar-el-corte-aprobado)
y entrega el MP4, su ubicación y el estado real de revisión. Elimina las
sesiones temporales (`.sesion.json`) al acabar.
