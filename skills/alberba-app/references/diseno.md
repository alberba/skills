# Diseño

`DESIGN.md` nace de [assets/DESIGN.md](../assets/DESIGN.md): la estructura de secciones del sistema de diseño de «finanzas.» con tokens de ejemplo. La identidad es de cada app.

## Rellenar

1. Del ambiente visual de la sección 1, escribir el título, la cita de una línea y el párrafo de tema.
2. Elegir la paleta con el acento dado. Cada par texto sobre fondo cumple 4,5:1; en temas claros, el acento como texto (`--color-accent-text`) se oscurece hasta cumplirlo.
3. Elegir tipografías con una pareja display y texto, instaladas por `@fontsource-variable/<familia>`.
4. Dejar fuera las secciones de componentes que la app no usa. Cada componente que sí aparece lleva su medida y su rol.
5. Pasar los tokens de «Quick Start» a `@theme` de Tailwind cuando el proyecto lo use.

Hecho = ningún `{{…}}` queda en el fichero, los pares de color cumplen 4,5:1 y cada token de la tabla existe en el CSS.
