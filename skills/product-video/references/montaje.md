# Montaje y revisión

Las tomas se montan con `recorded`. Las escenas diseñadas se definen en
`<proyecto>/diseno.py`, que puede hacer `import montaje as m`:

```python
import montaje as m

ESCENAS = {
    "33": lambda sid: m.title(sid, "TU EQUIPO", ["Todo en un lugar."], "Planifica y comparte."),
}
```

Cada función devuelve `(duración, html)`; consulta las firmas de
[montaje.py](../scripts/montaje.py) antes de usar una pieza.

- `title` abre con texto, `card` introduce un bloque.
- `recorded(sid, extra=AIR, zoom=None)` monta la toma, con tiempo final para
  leer el resultado. `AIR` vale 1,4 s y se ajusta según el ritmo aprobado.
- `before_after(sid, palabra)` usa `NN-antes.mp4/json` y `NN.mp4/json`.
- `phone(p, sid)` enmarca una toma móvil real 780×1528 en un teléfono con barra
  de estado y de inicio. El resto del diseño lo hace el proyecto.
- `closing_logo(sid, name="product")` cierra con un logo;
  `closing(..., product="product", creator="creator")` añade un crédito
  opcional. Los logos viven en `assets/marca/<nombre>.svg` o `.png` del
  proyecto; se prefiere SVG. Si no hay logo, diseña un cierre tipográfico.
- `voiced(sid, extra)` da la duración; `wt(sid, palabra)` sincroniza un efecto
  con la voz. `window_html`, `window_still`, `web_scene` y `wrap` permiten
  escenas propias.

El kit conserva un estilo de papel, foco sin borde y cursor de flecha suave;
son un punto de partida. La marca, colores, cierre y duración se deciden para
el producto actual. No incorpora logos ni una voz de Nougrup/Isitech.

## Revisión visual

Usa una cámara estable por escena: solo acerca si mejora la lectura, con
límite ×1,35 y umbral ×1,2. Una marca `zoom` activa el acercamiento; no se
necesita en cada frase. La cámara hereda el plano anterior y vuelve al plano
abierto antes de una escena diseñada. Revisa las uniones además de los frames.

`assets/marcas.txt` indica segundos globales para `hyperframes snapshot --at`.
Comprueba en cada marca que el foco enmarca el bloque completo y coincide con
lo narrado. Revisa también escenas sin marcas e inicio/cierre. El informe de
continuidad señala saltos de página/scroll y scroll que se deshace: resuélvelos
en `escenas.py` o justifica el corte diseñado en el guion.

Las escenas móviles, esquemas y rótulos se revisan ampliados en snapshot y
preview: las hojas de contacto no muestran bien capas desplazadas, logos
pixelados, etiquetas duplicadas ni barras recortadas. Centra elementos animados
con un contenedor flex; una transformación de centrado puede ser sobrescrita
por la animación y verse distinta en preview.

Antes de un efecto propio, busca una pieza en el catálogo HyperFrames si el
CLI lo ofrece. Mantén una timeline pausada y determinista. El foco anima
opacidad, no `left`/`top`. Si hay skills HyperFrames instaladas, usa las
referencias que correspondan al efecto concreto.

El montaje regenera `compositions/frames/` y `assets/stills/`. Guarda capturas
manuales en `assets/capturas/`; esos directorios generados no deben contener
fuentes únicas. Si una toma termina antes que la voz, queda su último frame.
La prevalidación rechaza audio ausente/desactualizado y huellas incompatibles
antes de borrar composiciones; revisa todos los errores de `hyperframes check`
y los avisos relevantes antes de entregar.

La geometría móvil del kit es fija: viewport 390×764, toma 780×1528 y área
visible del teléfono 368×721. Una toma 390×844 no encaja: regraba al viewport
del kit si el encargo lo permite, o adapta conjuntamente `MOVIL`, el tamaño
de salida del grabador y `phone`. Comprueba el encuadre sin recortar ni
estirar barras; insertar la toma más alta con `object-fit: cover` las corta.
