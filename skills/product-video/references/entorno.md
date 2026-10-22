# Preparar la aplicación

1. Usa el entorno local y las instrucciones del repo; para otra rama, su
   gestor de worktrees. Verifica login, búsqueda, imágenes y las pantallas
   del guion con esa variante. Prepara datos sintéticos; si se usan datos
   reales, acuerda qué ocultar antes de capturar.
2. Comprueba los efectos externos del servidor: una base de datos local puede
   seguir enviando a un ERP, correo o pasarela reales. Usa sandboxes o desactiva
   esos conectores y sus workers según el repo. El filtro del navegador no
   aísla llamadas que el servidor hace desde un GET, una tarea o un websocket.
3. Configura `<proyecto>/escenas.py` según [grabar.md](grabar.md). Usa sesiones
   y credenciales de prueba autorizadas; el hook `setup` implementa el login.
   El grabador usa Chromium con service workers bloqueados y filtra las
   escrituras antes de ejecutar ese hook.
4. Mantén el directorio de vídeo fuera de git, o ignora explícitamente sus
   sesiones, audios, capturas y secretos. No presupongas que `videos/` está
   ignorado en otro repo. `.env.local` contiene las claves; no se lee ni imprime
   como evidencia.

Dependencias: Python 3.10+, `uv`, FFmpeg/ffprobe, Playwright con Chromium y el
CLI HyperFrames. Verifica los comandos instalados antes de capturar; si falta
Chromium, `uv run --no-project --with playwright python -m playwright install
chromium`. Los scripts de voz necesitan además ElevenLabs. Usa la versión del
CLI del proyecto cuando exista.

## Dos versiones

Para un antes/después usa dos checkouts y puertos, con datos y ajustes
equivalentes. Comprueba las pantallas de ambos; no asumas que una restauración
nueva funciona con código antiguo. Graba cada versión por separado y asigna
su sesión con `setup`. `BASE_URL` del entorno prevalece sobre la del módulo.
`--antes` pone `VERSION=antes` y escribe `NN-antes.mp4/json`.

Documenta en el docstring de `escenas.py` cómo restablecer el estado: carritos,
impersonación y registros creados pueden sobrevivir entre tomas. Ejecuta esa
preparación local antes de repetir una grabación completa.

## Migrar un vídeo de nougrup-ecommerce

El origen de este kit es `demo-video` de ese repo. Sus comandos de restauración,
búsqueda y media se consultan en la documentación de nougrup-ecommerce. Sus
workers pueden comunicarse con el ERP real: deben estar detenidos o aislados.

Para reutilizar un vídeo existente hay que mover al proyecto su login y
cambio staff/cliente, sus modos de tours y selectores de difuminado, y sus
logos autorizados a `assets/marca/`. La antigua lista de rutas ERP bloqueadas
no equivale a una lista de escrituras permitidas: permite solo las operaciones
locales que necesita el recorrido, incluido el login. Configura voz y modelo
explícitos. Renombra `closing_isitech` a `closing_logo(..., name="creator")`;
`closing` admite `product="product", creator="creator"`. Los nuevos logos
pueden usar esos nombres, sin que el kit incluya las marcas originales.
