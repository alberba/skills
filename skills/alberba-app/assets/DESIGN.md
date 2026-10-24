# {{nombre}} — Referencia de estilo

> {{cita de una línea: la imagen que resume el ambiente}}

**Tema:** {{claro, oscuro o varios; cuál es el por defecto}}

{{Un párrafo: el ambiente, el papel del acento, qué tipografía lleva las cifras y los títulos, la familia de formas, el tono y el movimiento.}}

## Tokens — Colores

| Nombre | Valor | Token | Rol |
| --- | --- | --- | --- |
| Lienzo | `{{#…}}` | `--color-bg` | Fondo de la página |
| Panel | `{{#…}}` | `--color-panel` | Tarjetas, popovers y hojas |
| Panel hundido | `{{#…}}` | `--color-panel2` | Pistas, tickers, ítem de nav activo |
| Filete | `{{#…}}` | `--color-line` | Borde de tarjeta y separador de fila |
| Filete de control | `{{#…}}` | `--color-ctrl-line` | Borde de chips y campos |
| Texto | `{{#…}}` | `--color-text` | Texto principal |
| Texto suave | `{{#…}}` | `--color-soft` | Lede, texto en reposo |
| Texto atenuado | `{{#…}}` | `--color-muted` | Etiquetas, metadatos, ejes |
| Acento | `{{acento}}` | `--color-accent` | Acción principal, sección activa, foco |
| Sobre acento | `{{#…}}` | `--color-on-accent` | Texto sobre `--color-accent` |
| Acento como texto | `{{#…}}` | `--color-accent-text` | El acento cuando es texto; en temas claros se oscurece hasta 4,5:1 |
| Ganancia | `{{#…}}` | `--color-gain` | Deltas positivos, solo en texto |
| Pérdida | `{{#…}}` | `--color-loss` | Deltas negativos y acciones destructivas |

Añadir los tokens de serie, barra neutra, selección y sombra que use la app.

## Temas

Una columna por tema, con los mismos tokens. Cada tema declara su `color-scheme`.

## Tokens — Tipografía

- **Display:** `{{familia}}`, para títulos de página y cifras. Pesos, tamaños y tracking.
- **Texto:** `{{familia}}`, para todo lo demás. Pesos y tamaños.
- **Escala:** tabla con rol, familia, peso, tamaño, interlineado, tracking y token.

## Tokens — Espaciado y formas

- **Unidad base** y escala de espaciado con su token.
- **Radios:** una tabla por elemento (botón, tarjeta, popover, campo, hoja, avatar).
- **Layout:** ancho máximo, barra lateral, padding de página y de tarjeta, altura de control y de fila.

## Componentes

Un apartado por componente que la app usa. Cada uno lleva su rol y sus medidas: botón primario, secundario, de icono, tarjeta, popover, hoja, chip, segmentado, campo, fila de lista, barra de progreso, gráfico y estado vacío.

## Qué hacer y qué no

### Hacer

- {{Una regla de uso por línea: profundidad, uso del acento, cifras, formas, colores semánticos, tamaño mínimo de control, movimiento y títulos.}}

### No hacer

- {{Una regla por línea, en positivo cuando se pueda; las prohibiciones duras al final.}}

## Superficies y elevación

Niveles de superficie (barra lateral, lienzo, panel, panel hundido, selección) y qué flota con sombra.

## Iconografía

Familia de iconos, `viewBox`, trazo, tamaños y contenedor de categoría.

## Layout

Escritorio y móvil: estructura, columnas, navegación y cabeceras.

## Números

Formato de dinero, porcentajes y fechas, y qué columnas se alinean a la derecha.

## Movimiento

| Nombre | De | Duración | Curva | Uso |
| --- | --- | --- | --- | --- |

Todo dentro de `@media (prefers-reduced-motion: no-preference)`. Foco con `outline` del acento en `:focus-visible`. Hover solo en `@media (hover: hover) and (pointer: fine)`.

## Quick Start

```css
:root,
[data-theme='{{tema-por-defecto}}'] {
  --color-bg: {{#…}};
  --color-panel: {{#…}};
  --color-text: {{#…}};
  --color-accent: {{acento}};
  color-scheme: {{light o dark}};
}
```

El bloque `@theme` de Tailwind v4 repite los valores del tema por defecto; los bloques `[data-theme]` los cambian en ejecución.
