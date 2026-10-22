---
name: product-video
description: Crear o editar vídeos de producto web (demos, recorridos y novedades) con grabación real, voz sincronizada y subtítulos. Usar para una demo grabada o un vídeo que explique una aplicación; requiere Playwright, FFmpeg e HyperFrames para el montaje.
---

# Vídeos de producto

Convierte un recorrido real de una aplicación web en un vídeo narrado. El kit
no presupone framework, login, marca ni integraciones del repositorio.
`<SKILL_DIR>` significa la ruta absoluta de esta carpeta instalada: resuélvela
antes de ejecutar comandos; el proyecto del vídeo puede vivir en otro repo.

La fuente es `STORYBOARD.md`: texto, orden, pantallas y tiempos. `escenas.py`
define la navegación y el acceso a la aplicación; `diseno.py`, las escenas
ilustradas. Los HTML se regeneran: cambia sus fuentes, no el resultado.

## Preparar el encargo

Reutiliza las decisiones y autorizaciones de la conversación y del proyecto.
Completa en `BRIEF.md` el público, alcance, idioma/acento, marca, destino,
privacidad e importes visibles. Pregunta solo por decisiones pendientes que
cambien la entrega; con datos sintéticos y sin importes no hay cuestionario de
privacidad. Para datos reales, resuelve qué ocultar antes de grabarlos.

Si está instalada, usa la skill `hyperframes` para preparar el proyecto y su
brief, en flujo companion. Si falta, consulta el CLI instalado y crea un
proyecto con `hyperframes.json`; conserva guion y fuentes si el render no está
disponible. No sustituyas grabaciones reales por pantallas inventadas.

Lee [entorno.md](references/entorno.md) para preparar una copia local, aislar
integraciones y configurar el kit. Verifica allí cada pantalla antes de
incluirla: una funcionalidad exclusiva de otra variante no entra en el guion.

## Guion y recorrido, por bloques

Recorre la aplicación y escribe el texto en el mismo orden que la navegación.
Cada frase desarrolla una idea y una acción visible. Revisa el texto por
bloques y graba cada bloque antes de desarrollar el siguiente; respeta las
aprobaciones existentes. Para el formato, lee [grabar.md](references/grabar.md).

Mantén en **el mismo storyboard y preview** todas las piezas aprobadas,
incluidas las introducciones añadidas después. El orden es el del documento,
no el número del frame. Todos los frames de este kit llevan locución; si se
necesita una escena muda, adapta el montaje explícitamente antes de usarla.

## Voz y tomas

Antes de generar voz con ElevenLabs, lee [voz.md](references/voz.md): resuelve
la API key, el id de voz y el modelo desde la configuración y las decisiones
ya aprobadas. Pide únicamente lo que falte. Reutiliza audio vigente y la voz
aprobada; confirma acento y pronunciación con una muestra si la voz es nueva.

```sh
uv run --no-project --with elevenlabs python <SKILL_DIR>/scripts/voz.py <proyecto> --voz <id> --modelo <modelo> --idioma es --escuchar
uv run --no-project --with playwright python <SKILL_DIR>/scripts/grabador.py <proyecto> [NN ...]
```

Las tomas siguen [grabar.md](references/grabar.md): cada gesto cae con la
palabra que lo nombra y cada pantalla continúa el recorrido anterior.
Hecho cuando todas las tomas existen, el comando termina con éxito, ninguna
marca supera 0,25 s de retraso y has revisado la privacidad tras las
navegaciones. Cambiar voz, tiempos o `lead` invalida las tomas afectadas.

## Montaje y entrega

Lee [montaje.md](references/montaje.md) para las piezas, logos y revisión visual.

```sh
python3 <SKILL_DIR>/scripts/montaje.py <proyecto>
cd <proyecto>
npx hyperframes check
```

El montaje exige una locución vigente por frame y rechaza tomas de otra
locución. Comprueba que el inicio, los bloques y el cierre aprobados aparecen
en el preview completo. Revisa fotogramas por marca, las uniones entre escenas
y, ampliadas, las escenas diseñadas y móviles. `check` no verifica estética,
privacidad ni que el guion cubra lo solicitado.

Muestra el preview entero con sonido y aplica las notas en sus fuentes.
Renderiza cuando esté autorizado; una autorización existente sigue siendo
válida para su alcance. Entrega el MP4, su ubicación y las limitaciones reales.
Elimina las sesiones temporales (`.sesion.json`) al acabar.

```sh
npx hyperframes render -q delivery --video-frame-format png -o <destino>.mp4
```
