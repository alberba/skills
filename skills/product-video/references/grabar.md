# Guion y grabación

`STORYBOARD.md` usa este formato (todos los campos de texto, una línea):

```markdown
## Frame 33 — Introducción
- src: compositions/frames/33-intro.html
- voiceover: "Organiza el trabajo de tu equipo en un solo lugar."
- section: Presentación
- lead: 0.35

## Frame 4 — Proyectos
- src: compositions/frames/04-proyectos.html
- voiceover: "Abres Proyectos y ves lo que queda pendiente."
- section: Proyectos
```

`section` y `lead` son opcionales. Los ids y `src` son únicos; el orden del
documento manda. `src` está dentro de `compositions/frames/`, salida generada.
Cada frame exige locución; adapta el montaje antes de introducir escenas mudas.

## Contrato de escenas.py

```python
import os

BASE_URL = "http://localhost:3000"
# Regex de rutas completas que admiten escrituras, solo en este origen.
# Con () se bloquean todas. Incluye login solo si la aplicación lo necesita.
ALLOW_WRITES = (r"/api/auth/login",)
DIFUMINAR = ".customer-email, .customer-address { filter: blur(12px) !important; }"
# Con datos sintéticos ya verificados: DIFUMINAR = ""
CSS = ""                 # CSS adicional del proyecto
MODES = ()               # clases HTML propias; no hay modos de Django/tours
CONTINUA = {"05": "04"}  # página y scroll al final de la toma anterior
PREP = {}                # opcional: {"04": fn(page, base)}, fuera de plano


def setup(page, base, who):
    # Hook opcional, ejecutado fuera de plano en cada contexto nuevo.
    # Adapta al login real del repo, con variables de entorno y usuario de prueba.
    page.goto(base + "/login")
    page.get_by_label("Email").fill(os.environ["DEMO_EMAIL"])
    page.get_by_label("Contraseña").fill(os.environ["DEMO_PASSWORD"])
    page.get_by_role("button", name="Entrar").click()
    page.wait_for_url(base + "/dashboard")


def s04(h):
    h.goto("/dashboard")
    h.at("Abres", ahead=0.8)
    h.click(h.text("Proyectos", exact=True))
    h.page.get_by_role("heading", name="Proyectos").wait_for()
    h.point("Pendientes", h.text("Pendientes", exact=True), "pendiente", within=".project-card")

SCENES = {"04": (s04, "desktop")}
# Añade SCENES["05"] y la función correspondiente antes de usar CONTINUA.
# Los frames diseñados no aparecen en SCENES: los resuelve diseno.py.
```

`who` se pasa al hook sin interpretar: puede distinguir usuarios propios del
producto. `"mobile"` además usa un viewport 390×764, DPR 2, sin cursor.
La tupla admite un tercer campo con una lista de modos que sustituye `MODES`.
Para capturas sueltas, tras `grabador.cargar(root)`, usa
`ctx, page = grabador.abrir(browser, root, grabador.css_extra(mod), ...)` y
llama al hook `setup` antes de capturar.

## Red y privacidad

El filtro permite GET/HEAD/OPTIONS y bloquea las demás peticiones salvo rutas
de `ALLOW_WRITES` del mismo origen. Usa regex acotadas; login, búsquedas por
POST o preparación local pueden necesitar excepciones distintas. Un bloqueo
aborta la petición e imprime un diagnóstico: corrige la toma, no amplíes la
lista para completar un envío real. El hook y `PREP` comparten el filtro.

El CSS `DIFUMINAR` se inyecta desde el inicio de cada documento y se aplica
también a elementos dinámicos. Identifica los selectores de esa aplicación:
el kit no conoce nombres, NIF, emails ni direcciones de otros repos. Datos en
canvas, iframes o popups requieren tratamiento propio. Verifica fotogramas a
10 fps tras cada navegación: una captura al final no detecta una exposición
transitoria. `--sin-difuminar` solo se usa si el brief autoriza datos visibles.

## Gestos y continuidad

- `h.point(nombre, elemento, palabra, within=...)` lleva el cursor y marca el
  bloque al decir la palabra. `h.show` marca sin cursor; `h.at(palabra,
  ahead=s)` anticipa una acción que necesita carga.
- Vincula las marcas narrativas a su palabra con estos métodos. Una marca
  sin `cue` queda fuera del informe de desfase: no acredita sincronía.
- Las palabras se buscan hacia delante, ignorando tildes y mayúsculas;
  repetir la última palabra reutiliza su tiempo. `h.text(..., exact=True)`
  evita coincidencias en etiquetas parecidas.
- `within` enfoca tarjeta o panel con título y opciones, no una etiqueta
  suelta. `block=N` sube N cajas con borde o fondo. Se avisa si el foco ocupa
  menos del 3 % de pantalla. Una frase no requiere una marca por palabra.
- La primera `h.goto("/ruta/")` debe llevar ruta literal: se carga antes de
  grabar. Si sigue a otra toma web, navega por el menú o enlace visible.
  `CONTINUA` conserva URL y scroll de la toma anterior; no vuelvas arriba.
- Si la navegación no cabe antes de la primera palabra, aumenta `lead` en el
  storyboard. Ante una marca con más de 0,25 s de retraso, repite primero para
  descartar carga en frío; si persiste, cambia el tiempo o la frase.
- `h.loaded()` espera `networkidle`; en apps con tráfico continuo espera un
  selector visible con `h.page` en su lugar.
- Un móvil muestra navegación real por la app, con toques y scroll dentro de
  la pantalla, sin mover el marco ni duplicar barras.

Cada toma genera vídeo, JSON con marcas y huella de voz, URL/scroll iniciales
y finales. Una toma fallida deja `NN-error.png`; el comando continúa con las
demás y termina con error. Monta cuando todas las tomas existan, el comando
termine con éxito, ninguna marca narrativa supere 0,25 s de retraso y la
privacidad esté revisada tras las navegaciones. El desfase solo genera avisos:
compruébalos aunque el comando termine con éxito. Cambiar CSS o cursor exige
repetir las tomas que lo contienen; cambiar voz, tiempos o `lead`, las afectadas.
