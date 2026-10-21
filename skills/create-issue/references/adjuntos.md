# Adjuntos existentes

## Preparar

Asociar cada fichero con el reporte donde el usuario lo menciona o pega; si la asociación es ambigua, resolverla antes de publicar ese adjunto. Cada acción puede llevar cero, uno o varios ficheros.

Comprobar que los ficheros existen y son legibles. Admitir rutas fuera del repositorio y con espacios: las imágenes pegadas suelen vivir en directorios temporales. Si falta un fichero, explicar cuál y resolver con el usuario si publicar sin él o esperar.

Inspeccionar las imágenes con la herramienta disponible y redactar un alt text breve basado en lo observado. Para vídeos, usar el contexto conocido y el mecanismo de reproducción disponible si hace falta entender su contenido. Los vídeos no llevan alt text en `gh`.

Consultar `gh issue create --help` o `gh issue comment --help` para comprobar soporte de `--attach` en la instalación actual. Si no está disponible, dejar preparado el texto y explicar el impedimento antes de publicar con media.

## Publicar

Añadir un `--attach <ruta>` por fichero al mismo comando que crea la issue o el comentario. Para imágenes, usar `--attach '<ruta>#<alt>'`. Pasar cada argumento con quoting seguro o mediante una lista de argumentos de proceso.

Para ubicar una imagen en una sección concreta, escribir `![alt](<ruta>)` en el body y adjuntar esa misma ruta: `gh` sustituye la referencia por la URL subida. Usar la sintaxis de enlace que admita la ruta, incluidos espacios. Los adjuntos sin referencia en el body se añaden al final.

Si falla alguna subida, conservar la URL devuelta y verificar qué adjuntos llegaron. Aplicar la recuperación del paso «Publicar y verificar» de la skill antes de cualquier reintento; completar los adjuntos faltantes en la issue existente mediante las operaciones disponibles en la ayuda de `gh`.
