"""Monta la composición de HyperFrames de un proyecto con la voz y las tomas.

  python3 <SKILL_DIR>/scripts/montaje.py videos/<proyecto>

Lee el STORYBOARD.md, assets/vo/vo.json y assets/clips/NN.json, y escribe
compositions/frames/*.html (el `src` de cada escena), compositions/captions.html
e index.html. Cambiar el vídeo es cambiar esos datos o el diseño y volver a
montar: las composiciones generadas no se editan a mano.

Una escena con toma se monta sola (`recorded`). Las demás (apertura, rótulos
de bloque, esquemas, firma) las da `videos/<proyecto>/diseno.py`; ver
references/montaje.md. Lo de este módulo es la marca común de los vídeos:
lienzo de papel, ventana de navegador, foco, título, antes y después y firma.
"""

import importlib.util
import json
import re
import shutil
import subprocess
import sys
from collections.abc import Callable
from html import escape
from pathlib import Path

from comun import TAIL, escenas, firma_voz, locucion, norm, proyecto

Scene = tuple[float, str]  # (duración, html de la composición)

ROOT = Path()
VO: dict = {}
PLAN: dict = {}

# Marca de los vídeos
PAPER, INK, ACCENT, MUTED = "#f5f1e8", "#1a1515", "#c4521c", "#6b625a"
W, H = 1920, 1080
WIN_X, WIN_Y, WIN_W, WIN_H, BAR = 240, 40, 1440, 850, 40
VIEW_H = WIN_H - BAR  # 810: 1440x810 es 16:9
BASE_S = WIN_W / W  # 0.75
ZOOM = 1.35  # tope del acercamiento; con menos de ZOOM_MIN no merece la pena
ZOOM_MIN = 1.2
FOCUS_PAD, FOCUS_GAP = 14, 3.0  # margen del foco (px de vídeo); pausa que lo apaga
FOCUS_DIM = 0.52  # cuánto oscurece el resto (el foco no lleva borde)
AIR = 1.4  # segundos que cada escena se queda con el resultado en pantalla
RIGHT = {"x": 330, "y": 40, "scale": 0.6}  # la ventana apartada a la derecha
JS_SEP = "\n        "
# Cámara con la que acaba la escena anterior: la siguiente parte de ahí, así
# entre escenas no hay saltos de encuadre.
LAST_CAM = (BASE_S, 0.0, 0.0)
RESET_AT_END = False  # la escena siguiente es diseñada: vuelve al plano abierto


def lead(sid: str) -> float:
    return PLAN[sid]["lead"]


def voiced(sid: str, extra: float = 0.0) -> float:
    """Duración de una escena que dura lo que su voz (más `extra`)."""
    return VO[sid]["duration_s"] + lead(sid) + TAIL + extra


def wt(sid: str, word: str, floor: float = 0.0) -> float:
    """Segundo de la escena en que la locución dice `word`."""
    key = norm(word)
    for w in VO[sid].get("words", []):
        if norm(w["text"]).startswith(key):
            return max(floor, lead(sid) + w["start"])
    msg = f"«{word}» no está en la locución de {sid}"
    raise ValueError(msg)


def clip(name: str) -> dict:
    """JSON de la toma `name` (`NN` o `NN-antes`). Se niega a montar una toma
    grabada con otra locución: regrábala (`grabador.py`)."""
    c = json.loads((ROOT / "assets/clips" / f"{name}.json").read_text())
    sid = name.split("-")[0]
    if c.get("voz") != firma_voz(VO[sid], lead(sid)):
        sys.exit(
            f"la toma {name} es de otra locución (texto, velocidad o lead): regrábala"
        )
    return c


def still(clip: str, at: float, name: str) -> str:
    """Un fotograma de una toma, como imagen para las escenas diseñadas."""
    out = ROOT / "assets/stills" / f"{name}.jpg"
    if not out.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        source = ROOT / "assets/clips" / f"{clip}.mp4"
        subprocess.run(
            ["ffmpeg", "-loglevel", "error", "-y", "-ss", str(at), "-i", str(source)]
            + ["-frames:v", "1", "-q:v", "2", str(out)],
            check=True,
        )
    return f"assets/stills/{name}.jpg"


def logo(name: str) -> str:
    """Logo del proyecto; SVG preferido sobre PNG. No copia marcas del kit."""
    for ext in ("svg", "png"):
        relative = Path("assets/marca") / f"{name}.{ext}"
        if (ROOT / relative).is_file():
            return relative.as_posix()
    raise FileNotFoundError(f"Falta assets/marca/{name}.svg o .png en el proyecto")


# --- Piezas comunes ---------------------------------------------------------------


def common_css(p: str) -> str:
    return f"""
#root {{ position: absolute; inset: 0; overflow: hidden; background: {PAPER};
  font-family: Montserrat, sans-serif; color: {INK}; }}
#{p}-paper {{ position: absolute; inset: 0;
  background-image:
    radial-gradient(circle at 1px 1px, rgba(26,21,21,.13) 1.4px, transparent 0);
  background-size: 32px 32px; }}
#{p}-glow {{ position: absolute; left: -10%; top: -20%; width: 70%; height: 90%;
  border-radius: 50%;
  background: radial-gradient(closest-side, rgba(196,82,28,.16), rgba(196,82,28,0)); }}
.{p}-win {{ position: absolute; left: {WIN_X}px; top: {WIN_Y}px;
  width: {WIN_W}px; height: {WIN_H}px;
  border-radius: 16px; background: #fff; overflow: hidden; transform-origin: 50% 50%;
  box-shadow: 0 30px 70px rgba(26,21,21,.20), 0 0 0 2px rgba(26,21,21,.10); }}
.{p}-bar {{ position: absolute; left: 0; top: 0; right: 0; height: {BAR}px;
  background: #ece6da;
  display: flex; align-items: center; gap: 10px; padding: 0 18px; }}
.{p}-dot {{ width: 13px; height: 13px; border-radius: 50%; background: #cfc6b8; }}
.{p}-url {{ margin-left: 18px; height: 26px; border-radius: 13px; background: #fbf8f2;
  padding: 0 18px; display: flex; align-items: center;
  font: 500 16px 'IBM Plex Mono', monospace; color: {MUTED}; }}
.{p}-view {{ position: absolute; left: 0; top: {BAR}px;
  width: {WIN_W}px; height: {VIEW_H}px; overflow: hidden; background: #fdfdfd; }}
.{p}-cam {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px;
  transform-origin: 0 0; }}
.{p}-cam video, .{p}-cam img {{ position: absolute; left: 0; top: 0;
  width: {W}px; height: {H}px; }}
.{p}-pill {{ background: {INK}; color: #fbf8f2; font: 700 30px Montserrat, sans-serif;
  padding: 12px 22px 13px; border-radius: 12px; white-space: nowrap;
  display: flex; align-items: center; gap: 12px; }}
.{p}-pill i {{ width: 12px; height: 12px; border-radius: 50%; background: {ACCENT};
  display: block; }}
.{p}-kicker {{ font: 600 26px 'IBM Plex Mono', monospace; color: {ACCENT};
  letter-spacing: .06em; }}
.{p}-head {{ font-weight: 800; font-size: 104px; line-height: .98;
  letter-spacing: -.035em; }}
.{p}-head span, .{p}-sub span {{ display: block; }}
.{p}-sub {{ font-weight: 500; font-size: 40px; line-height: 1.25; color: {MUTED}; }}
"""


def window_html(p: str, sid: str, inner: str, cls: str = "") -> str:
    url = escape(PLAN[sid]["section"] or "Producto")
    dots = f'<span class="{p}-dot"></span>' * 3
    return f"""
<div class="{p}-win {cls}" id="{p}-win">
  <div class="{p}-bar">{dots}
    <span class="{p}-url">{url}</span></div>
  <div class="{p}-view" id="{p}-view">{inner}</div>
</div>"""


PHONE_INK = "#1a1515"


def phone(p: str, sid: str, left: int = 560, top: int = 70) -> str:
    """Un iPhone con la toma móvil `sid` dentro (780x1528): barra de estado
    (9:41, isla, señal, wifi, batería) arriba y barra de inicio abajo. El
    último fotograma queda debajo por si la toma acaba antes que la escena."""
    c = clip(sid)
    end = still(sid, c["duration"] - 0.1, f"{sid}-movil-fin")
    fill = "position:absolute;left:0;top:0;width:368px;height:721px;object-fit:cover"
    return f"""
<div id="{p}-phone" style="position:absolute;left:{left}px;top:{top}px;width:400px;height:820px;border-radius:56px;background:{PHONE_INK};padding:16px;box-shadow:0 30px 70px rgba(26,21,21,.25)">
  <div style="width:368px;height:788px;position:relative;border-radius:42px;overflow:hidden;background:#fdfdfd">
    <div style="position:absolute;left:0;top:44px;width:368px;height:721px;overflow:hidden">
      <img src="{end}" alt="" style="{fill}" />
      <video id="{p}-v" src="assets/clips/{sid}.mp4" muted playsinline data-start="0" data-duration="{c["duration"]:.2f}" style="{fill}"></video>
    </div>
    <div style="position:absolute;left:0;top:0;width:368px;height:44px;background:#fdfdfd;font:600 15px -apple-system,'Helvetica Neue',sans-serif;color:{PHONE_INK}">
      <span style="position:absolute;left:34px;top:14px">9:41</span>
      <div style="position:absolute;left:50%;top:10px;margin-left:-55px;width:110px;height:30px;border-radius:15px;background:{PHONE_INK}"></div>
      <svg style="position:absolute;right:26px;top:16px" width="68" height="13" viewBox="0 0 68 13" fill="{PHONE_INK}">
        <rect x="0" y="8" width="3" height="5" rx="1"/><rect x="5" y="5.5" width="3" height="7.5" rx="1"/><rect x="10" y="3" width="3" height="10" rx="1"/><rect x="15" y="0" width="3" height="13" rx="1"/>
        <path d="M30 3.2c2.6 0 5 1 6.8 2.7l-1.2 1.3a8.3 8.3 0 0 0-11.2 0L23.2 5.9A9.8 9.8 0 0 1 30 3.2zm0 4.2c1.5 0 2.9.6 4 1.6l-1.3 1.3a4.3 4.3 0 0 0-5.4 0L26 9a5.8 5.8 0 0 1 4-1.6zm0 4a1.6 1.6 0 1 1 0 3 1.6 1.6 0 0 1 0-3z" transform="translate(0 -1.5)"/>
        <rect x="41.5" y="0.5" width="23" height="12" rx="3.5" fill="none" stroke="{PHONE_INK}" stroke-opacity=".4"/><rect x="43" y="2" width="20" height="9" rx="2.2"/><rect x="65.5" y="4.2" width="1.8" height="4.6" rx=".9" fill-opacity=".4"/>
      </svg>
    </div>
    <div style="position:absolute;left:0;bottom:0;width:368px;height:22px;background:#fdfdfd"><div style="position:absolute;left:50%;bottom:7px;margin-left:-67px;width:134px;height:5px;border-radius:3px;background:{PHONE_INK}"></div></div>
  </div>
</div>"""  # noqa: E501


def window_still(p: str, sid: str, src: str) -> str:
    """La ventana con una imagen quieta dentro (rótulos, esquemas, firma)."""
    size = f"width:{WIN_W}px;height:{VIEW_H}px;display:block"
    return window_html(p, sid, f'<img src="{src}" alt="" style="{size}" />')


def wrap(p: str, duration: float, css: str, body: str, js: str) -> str:
    glow = (
        f'tl.fromTo("#{p}-glow", {{ x: 0, scale: 1 }}, '
        f"{{ x: 140, scale: 1.12, duration: {duration:.2f}, "
        f'ease: "sine.inOut" }}, 0);'
    )
    return f"""<!doctype html>
<html>
  <head><meta charset="UTF-8" /></head>
  <body>
    <template>
      <style>{common_css(p)}{css}</style>
      <div id="root" data-composition-id="{p}" data-width="{W}" data-height="{H}"
        data-duration="{duration:.2f}">
        <div id="{p}-paper"></div><div id="{p}-glow" data-layout-allow-overflow></div>
        {body}
      </div>
      <script>
        const tl = gsap.timeline({{ paused: true }});
        {glow}
        {js}
        window.__timelines["{p}"] = tl;
      </script>
    </template>
  </body>
</html>
"""


# --- La tienda en la ventana: cámara y foco ----------------------------------------


def cam_at(box: list[int], z: float) -> tuple[float, float, float]:
    s = BASE_S * z
    if z == 1:
        return s, 0.0, 0.0
    cx, cy = box[0] + box[2] / 2, box[1] + box[3] / 2
    x = min(0, max(WIN_W - W * s, WIN_W / 2 - cx * s))
    y = min(0, max(VIEW_H - H * s, VIEW_H / 2 - cy * s))
    return s, x, y


def _media(p: str, media: list[dict]) -> tuple[list[str], list[str]]:
    """Vídeo e imágenes de la escena, y la entrada de cada imagen."""
    items, js = [], []
    for i, m in enumerate(media):
        if m["kind"] == "video":
            items.append(
                f'<video id="{p}-v{i}" src="{m["src"]}" muted playsinline '
                f'data-start="{m["start"]:.2f}" data-duration="{m["dur"]:.2f}"></video>'
            )
            continue
        items.append(f'<img id="{p}-i{i}" src="{m["src"]}" alt="" />')
        if i:
            js.append(
                f'tl.fromTo("#{p}-i{i}", {{ opacity: 0 }}, '
                f'{{ opacity: 1, duration: .35, ease: "power1.out" }}, '
                f"{m['start']:.2f});"
            )
        else:
            js.append(f'tl.set("#{p}-i{i}", {{ opacity: 1 }}, 0);')
    return items, js


def plan_cam(marks: list[dict], zoom_cap: float) -> tuple[float, float, float]:
    """Un plano por escena: encuadra todas las marcas a la vez. Se acerca solo si
    lo marcado cabe holgado a más de ZOOM_MIN; si no, se queda en el plano abierto."""
    boxes = [m["box"] for m in marks]
    x0, y0 = min(b[0] for b in boxes), min(b[1] for b in boxes)
    x1, y1 = max(b[0] + b[2] for b in boxes), max(b[1] + b[3] for b in boxes)
    z = min(zoom_cap, 0.85 * W / max(x1 - x0, 1), 0.85 * H / max(y1 - y0, 1))
    if z < ZOOM_MIN:
        return cam_at([0, 0, W, H], 1)
    return cam_at([x0, y0, x1 - x0, y1 - y0], z)


def _camera(p: str, marks: list[dict], zoom_cap: float, duration: float) -> list[str]:
    """Una sola maniobra por escena, desde la cámara de la anterior hasta el plano
    de ésta; termina en la primera marca, no empieza en ella. Al final se queda."""
    global LAST_CAM
    cam = plan_cam(marks, zoom_cap)
    js = [
        f'tl.set("#{p}-cam", {{ scale: {LAST_CAM[0]:.4f}, x: {LAST_CAM[1]:.1f}, '
        f"y: {LAST_CAM[2]:.1f} }}, 0);"
    ]
    if cam != LAST_CAM:
        first = min(m["t"] for m in marks)
        start = max(0.1, first - 0.9)
        dur = 0.9  # un deslizamiento lento: nunca un tirón
        js.append(
            f'tl.to("#{p}-cam", {{ scale: {cam[0]:.4f}, x: {cam[1]:.1f}, '
            f'y: {cam[2]:.1f}, duration: {dur:.2f}, ease: "power2.inOut" }}, '
            f"{start:.2f});"
        )
    LAST_CAM = cam
    if RESET_AT_END and cam != cam_at([0, 0, W, H], 1):
        js.append(
            f'tl.to("#{p}-cam", {{ scale: {BASE_S}, x: 0, y: 0, duration: .6, '
            f'ease: "power2.inOut" }}, {duration - 0.75:.2f});'
        )
        LAST_CAM = (BASE_S, 0.0, 0.0)
    return js


def _camera_still(p: str) -> list[str]:
    """Escena sin acercamiento: parte de la cámara anterior y se abre."""
    return _camera(p, [{"t": 0.0, "box": [0, 0, W, H]}], 1, 0)


def _focus(p: str, marks: list[dict], duration: float) -> tuple[list[str], list[str]]:
    """Un recuadro fijo por marca, dentro de la capa de cámara; al pasar a la
    siguiente se funden uno en otro (animar left/top no pasa el lint)."""
    real = [m for m in marks if m["name"] != "zoom"]
    boxes, js = [], []
    for j, m in enumerate(real):
        x, y, w, h = m["box"]
        # Dentro del encuadre, para que el marco se vea también en bloques a sangre.
        x0, y0 = max(x - FOCUS_PAD, 8), max(y - FOCUS_PAD, 8)
        x1, y1 = min(x + w + FOCUS_PAD, W - 8), min(y + h + FOCUS_PAD, H - 8)
        boxes.append(
            f'<div class="{p}-focus" id="{p}-f{j}" style="left:{x0}px;top:{y0}px;'
            f'width:{x1 - x0}px;height:{y1 - y0}px"></div>'
        )
        on = max(0.05, m["t"] - 0.3)
        nxt = real[j + 1]["t"] if j + 1 < len(real) else None
        if nxt is None:
            off = duration - 0.55
        elif nxt - m["t"] > FOCUS_GAP:
            off = m["t"] + 2.0
        else:
            off = max(0.05, nxt - 0.3)
        js.append(
            f'tl.to("#{p}-f{j}", {{ opacity: 1, duration: .3, '
            f'ease: "power1.out" }}, {on:.2f});'
        )
        if off > on + 0.3:
            js.append(
                f'tl.to("#{p}-f{j}", {{ opacity: 0, duration: .3, '
                f'ease: "power1.inOut" }}, {off:.2f});'
            )
    return boxes, js


def focus_css(p: str) -> str:
    """Estilo del recuadro de foco: solo oscurece el resto, sin borde."""
    return (
        f".{p}-focus {{ position: absolute; opacity: 0; border-radius: 18px;"
        f" pointer-events: none;"
        f" box-shadow: 0 0 0 4000px rgba(26,21,21,{FOCUS_DIM}); }}"
    )


def web_scene(
    sid: str,
    media: list[dict],
    marks: list[dict],
    duration: float,
    force_zoom: float | None = None,
) -> str:
    """La tienda en la ventana: la cámara llega a cada marca y un foco oscurece
    el resto salvo lo que nombra la voz.
    `media`: [{kind: video|img, src, start, dur}]; `marks` como las del grabador."""
    p = f"s{sid}"
    zoom = force_zoom or (ZOOM if any(m["name"] == "zoom" for m in marks) else 0)
    items, js = _media(p, media)
    js += _camera(p, marks, zoom, duration) if zoom else _camera_still(p)
    boxes, focus_js = _focus(p, marks, duration)
    js += focus_js
    inner = (
        f'<div class="{p}-cam" id="{p}-cam" data-layout-allow-overflow>'
        f"{''.join(items)}{''.join(boxes)}</div>"
    )
    css = f".{p}-cam img {{ opacity: 0; }}" + focus_css(p)
    return wrap(p, duration, css, window_html(p, sid, inner), JS_SEP.join(js))


def recorded(sid: str, extra: float = AIR, zoom: float | None = None) -> Scene:
    """Escena con toma. Dura lo que la voz más `extra` de aire: si es más que la
    toma, su último fotograma se queda debajo en lugar de cortar a negro.
    `zoom` acerca la cámara a cada marca (si no, solo a las marcas «zoom»)."""
    c = clip(sid)
    d = max(c["duration"], voiced(sid, extra))
    media = []
    if d > c["duration"] + 0.05:
        last = still(sid, c["duration"] - 0.1, f"{sid}-fin")
        media.append({"kind": "img", "src": last, "start": 0})
    media.append(
        {
            "kind": "video",
            "src": f"assets/clips/{sid}.mp4",
            "start": 0,
            "dur": c["duration"],
        }
    )
    return d, web_scene(sid, media, c["marks"], d, force_zoom=zoom)


def before_after(
    sid: str,
    word: str,
    ahead: float = 0.2,
    dur: float = 1.4,
    extra: float = 1.8,
    skip_antes: tuple[str, ...] = (),
) -> Scene:
    """Cortina de antes y ahora: dos tomas de la misma pantalla (`NN-antes.mp4`
    y `NN.mp4`) y una línea naranja que revela «ahora» de izquierda a derecha.

    La línea arranca `ahead` segundos antes de `word`, para que la tienda nueva
    esté entera cuando la voz la nombra, y tarda `dur` en recorrer la pantalla.
    Cada toma lleva sus propios focos; `skip_antes` descarta marcas de «antes» que
    caen pegadas a la siguiente (con menos de 0,6 s el foco anterior no se apaga y
    se verían dos a la vez). `extra` es el aire final con «ahora» en pantalla."""
    p, pa, pb = f"s{sid}", f"s{sid}a", f"s{sid}b"
    a, b = clip(f"{sid}-antes"), clip(sid)
    d = max(a["duration"], b["duration"], voiced(sid, extra))
    t = wt(sid, word) - ahead

    marks_a = [mk for mk in a["marks"] if mk["name"] not in skip_antes]
    boxes_a, js_a = _focus(pa, marks_a, d)
    boxes_b, js_b = _focus(pb, b["marks"], d)
    video = (
        '<video id="{id}" src="assets/clips/{src}.mp4" muted playsinline '
        'data-start="0" data-duration="{dur:.2f}"></video>'
    )
    # Si la voz dura más que la toma, el último fotograma se queda debajo.
    fin_a = still(f"{sid}-antes", a["duration"] - 0.1, f"{sid}-antes-fin")
    fin_b = still(sid, b["duration"] - 0.1, f"{sid}-fin")
    cam = f"""
<div class="{p}-cam" id="{p}-cam" data-layout-allow-overflow>
  <img src="{fin_a}" alt="" />
  {video.format(id=f"{p}-va", src=f"{sid}-antes", dur=a["duration"])}
  {"".join(boxes_a)}
  <div id="{p}-layer" data-layout-allow-overflow
    style="position:absolute;left:0;top:0;width:{W}px;height:{H}px">
    <img src="{fin_b}" alt="" />
    {video.format(id=f"{p}-vb", src=sid, dur=b["duration"])}
    {"".join(boxes_b)}
  </div>
  <div id="{p}-line" style="position:absolute;left:0;top:0;width:6px;height:{H}px;
    background:{ACCENT};opacity:0"></div>
</div>
<div class="{p}-pill" id="{p}-pa" style="position:absolute;left:24px;bottom:24px;
  opacity:0"><i></i>ANTES</div>
<div class="{p}-pill" id="{p}-pb" style="position:absolute;left:24px;bottom:24px;
  opacity:0;background:{ACCENT}"><i style="background:#fbf8f2"></i>AHORA</div>"""

    wipe = f'ease: "power2.inOut", duration: {dur:.2f}'
    js = [
        f'tl.set("#{p}-cam", {{ scale: {BASE_S}, x: 0, y: 0 }}, 0);',
        *js_a,
        *js_b,
        # el foco de «antes» se apaga antes de la cortina
        f'tl.to(".{pa}-focus", {{ opacity: 0, duration: .25 }}, '
        f"{max(0.05, t - 0.35):.2f});",
        f'tl.fromTo("#{p}-pa", {{ opacity: 0 }}, {{ opacity: 1, duration: .35 }}, .2);',
        f'tl.fromTo("#{p}-layer", {{ clipPath: "inset(0 100% 0 0)" }}, '
        f'{{ clipPath: "inset(0 0% 0 0)", {wipe} }}, {t:.2f});',
        f'tl.set("#{p}-line", {{ opacity: 1, x: 0 }}, {t:.2f});',
        f'tl.to("#{p}-line", {{ x: {W - 6}, {wipe} }}, {t:.2f});',
        f'tl.set("#{p}-line", {{ opacity: 0 }}, {t + dur + 0.02:.2f});',
        f'tl.to("#{p}-pa", {{ opacity: 0, duration: .25 }}, {t + 0.1:.2f});',
        f'tl.fromTo("#{p}-pb", {{ opacity: 0 }}, '
        f"{{ opacity: 1, duration: .35 }}, {t + dur * 0.6:.2f});",
    ]
    css = f".{p}-cam img {{ opacity: 1; }}" + focus_css(pa) + focus_css(pb)
    return d, wrap(p, d, css, window_html(p, sid, cam), JS_SEP.join(js))


# --- Escenas diseñadas comunes -------------------------------------------------------


def card(
    sid: str,
    kicker: str,
    lines: list[str],
    sub: list[str],
    still_src: str,
    *,
    from_center: bool = True,
    extra: float = 1.2,
) -> Scene:
    """Rótulo de bloque: la ventana se aparta y el título se escribe en el papel."""
    p, duration = f"s{sid}", voiced(sid, extra)
    head = "".join(f"<span>{escape(t)}</span>" for t in lines)
    subhtml = "".join(f"<span>{escape(t)}</span>" for t in sub)
    rule = f"height:3px;width:120px;background:{ACCENT};margin:26px 0 30px"
    body = f"""
{window_still(p, sid, still_src)}
<div id="{p}-text" style="position:absolute;left:120px;top:250px;width:760px">
  <div class="{p}-kicker" id="{p}-k">{escape(kicker)}</div>
  <div style="{rule}" id="{p}-rule"></div>
  <div class="{p}-head" id="{p}-h">{head}</div>
  <div class="{p}-sub" id="{p}-s" style="margin-top:34px">{subhtml}</div>
</div>"""
    aside = f"x: {RIGHT['x']}, y: {RIGHT['y']}, scale: {RIGHT['scale']}"
    if from_center:
        js = [
            f'tl.fromTo("#{p}-win", {{ x: 0, y: 0, scale: 1 }}, '
            f'{{ {aside}, duration: .8, ease: "power3.inOut" }}, 0);'
        ]
    else:
        js = [f'tl.set("#{p}-win", {{ {aside} }}, 0);']
    t0 = 0.45 if from_center else 0.1
    js += [
        f'tl.fromTo("#{p}-k", {{ opacity: 0, x: -30 }}, '
        f'{{ opacity: 1, x: 0, duration: .45, ease: "power2.out" }}, {t0:.2f});',
        f'tl.fromTo("#{p}-rule", {{ scaleX: 0, transformOrigin: "0 50%" }}, '
        f'{{ scaleX: 1, duration: .5, ease: "expo.out" }}, {t0 + 0.1:.2f});',
        f'tl.fromTo("#{p}-h span", {{ opacity: 0, y: 50 }}, '
        f'{{ opacity: 1, y: 0, duration: .6, stagger: .12, ease: "expo.out" }}, '
        f"{t0 + 0.15:.2f});",
        f'tl.fromTo("#{p}-s span", {{ opacity: 0, y: 20 }}, '
        f'{{ opacity: 1, y: 0, duration: .45, stagger: .5, ease: "power2.out" }}, '
        f"{t0 + 0.6:.2f});",
        # salida: el texto se va y la ventana vuelve al centro para la escena siguiente
        f'tl.to("#{p}-text", {{ opacity: 0, x: -40, duration: .4, '
        f'ease: "power2.in" }}, {duration - 0.85:.2f});',
        f'tl.to("#{p}-win", {{ x: 0, y: 0, scale: 1, duration: .75, '
        f'ease: "power3.inOut" }}, {duration - 0.8:.2f});',
    ]
    return duration, wrap(p, duration, "", body, JS_SEP.join(js))


def title(
    sid: str, kicker: str, lines: list[str], sub: str, extra: float = 0.6
) -> Scene:
    """Portada: texto sobre el papel, sin la tienda detrás. Abre el vídeo; la voz
    entra con el `lead` de la escena, cuando el título ya está en pantalla."""
    p, duration = f"s{sid}", voiced(sid, extra)
    head = "".join(f"<span>{escape(t)}</span>" for t in lines)
    rule = f"height:3px;width:120px;background:{ACCENT};margin:34px auto 38px"
    body = f"""
<div id="{p}-text" style="position:absolute;left:0;right:0;top:250px;text-align:center">
  <div class="{p}-kicker" id="{p}-k">{escape(kicker)}</div>
  <div style="{rule}" id="{p}-rule"></div>
  <div class="{p}-head" id="{p}-h" style="font-size:132px">{head}</div>
  <div class="{p}-sub" id="{p}-s" style="margin-top:44px">{escape(sub)}</div>
</div>"""
    js = [
        f'tl.fromTo("#{p}-k", {{ opacity: 0, y: -20 }}, '
        f'{{ opacity: 1, y: 0, duration: .6, ease: "power2.out" }}, .3);',
        f'tl.fromTo("#{p}-rule", {{ scaleX: 0 }}, '
        f'{{ scaleX: 1, duration: .7, ease: "expo.out" }}, .5);',
        f'tl.fromTo("#{p}-h span", {{ opacity: 0, y: 60 }}, '
        f'{{ opacity: 1, y: 0, duration: .8, stagger: .18, ease: "expo.out" }}, .7);',
        f'tl.fromTo("#{p}-s", {{ opacity: 0, y: 24 }}, '
        f'{{ opacity: 1, y: 0, duration: .6, ease: "power2.out" }}, 1.6);',
        f'tl.to("#{p}-text", {{ opacity: 0, duration: .5, ease: "power2.in" }}, '
        f"{duration - 0.55:.2f});",
    ]
    hidden = f"#{p}-k, #{p}-s, #{p}-h span {{ opacity: 0; }}"
    return duration, wrap(p, duration, hidden, body, JS_SEP.join(js))


def closing_logo(sid: str, extra: float = 2.2, name: str = "product") -> Scene:
    """Cierre con un logo del proyecto, centrado con un contenedor flex."""
    p, duration = f"s{sid}", voiced(sid, extra)
    body = f"""
<div style="position:absolute;left:0;top:0;width:{W}px;height:{H}px;display:flex;
  align-items:center;justify-content:center;padding-bottom:90px;box-sizing:border-box">
  <img id="{p}-logo" src="{logo(name)}" alt=""
    style="height:300px;width:auto;display:block" />
</div>"""
    js = [
        f'tl.fromTo("#{p}-logo", {{ opacity: 0, y: 24, scale: .96 }}, '
        f'{{ opacity: 1, y: 0, scale: 1, duration: 1.0, ease: "expo.out" }}, .3);',
    ]
    return duration, wrap(
        p, duration, f"#{p}-logo {{ opacity: 0; }}", body, JS_SEP.join(js)
    )


def closing(
    sid: str,
    line: str,
    line_word: str,
    credit_word: str,
    still_src: str,
    extra: float = 2.0,
    product: str = "product",
    creator: str | None = None,
) -> Scene:
    """Firma con logo de producto y crédito opcional. Los nombres buscan logos
    en assets/marca; las palabras sincronizan la frase y el crédito."""
    p, duration = f"s{sid}", voiced(sid, extra)
    column = "display:flex;flex-direction:column;align-items:center"
    row = "display:flex;align-items:center;justify-content:center;gap:22px"
    big = "font-weight:700;font-size:60px;letter-spacing:-.02em"
    credit = (
        f'<div id="{p}-by" style="position:absolute;inset-inline:0;inset-block-start:930px;{row}">'
        f'<div class="{p}-kicker" style="color:{MUTED};font-size:20px">DESARROLLADO POR</div>'
        f'<img src="{logo(creator)}" alt="" style="height:38px;width:auto;display:block" /></div>'
        if creator else ""
    )
    body = f"""
{window_still(p, sid, still_src)}
<div id="{p}-sign" style="position:absolute;left:0;right:0;top:120px;{column}">
  <img id="{p}-logo" src="{logo(product)}" alt=""
    style="height:400px;width:auto;display:block" />
  <div id="{p}-rule"
    style="height:3px;width:120px;background:{ACCENT};margin:48px 0 40px"></div>
  <div id="{p}-line" style="{big}">{escape(line)}</div>
</div>
{credit}"""
    js = [
        f'tl.to("#{p}-win", {{ scale: .2, opacity: 0, y: -60, duration: 1.0, '
        f'ease: "power3.inOut" }}, 0);',
        f'tl.fromTo("#{p}-logo", {{ opacity: 0, y: 30, scale: .96 }}, '
        f'{{ opacity: 1, y: 0, scale: 1, duration: .8, ease: "expo.out" }}, .6);',
        f'tl.fromTo("#{p}-rule", {{ scaleX: 0 }}, '
        f'{{ scaleX: 1, duration: .6, ease: "expo.out" }}, 1.0);',
        f'tl.fromTo("#{p}-line", {{ opacity: 0, y: 24 }}, '
        f'{{ opacity: 1, y: 0, duration: .7, ease: "power2.out" }}, '
        f"{wt(sid, line_word, 1.1) - 0.2:.2f});",
        # el crédito entra después del último subtítulo, para no pisarlo
        f'tl.fromTo("#{p}-by", {{ opacity: 0, y: 12 }}, '
        f'{{ opacity: 1, y: 0, duration: .6, ease: "power2.out" }}, '
        f"{(wt(sid, credit_word, 2.0) + 0.7) if creator else 0:.2f});",
    ]
    if creator is None:
        js = js[:-1]
    hidden = f"#{p}-logo, #{p}-line, #{p}-by {{ opacity: 0; }}"
    return duration, wrap(p, duration, hidden, body, JS_SEP.join(js))


# --- Subtítulos y montaje -------------------------------------------------------------


def caption_chunks(words: list[dict], dur: float) -> list[tuple[float, float, str]]:
    """Subtítulos con los tiempos reales de cada palabra: cortes en fin de frase
    (. : ? !), en coma tras una frase hecha, y como mucho 52 caracteres por
    línea."""
    groups, cur = [], []
    for w in words:
        text = " ".join(x["text"] for x in cur)
        if cur and (
            len(text) + len(w["text"]) > 52
            or re.search(r"[.:?!]$", text)
            or (len(text) > 22 and re.search(r",$", text))
        ):
            groups.append(cur)
            cur = []
        cur.append(w)
    groups.append(cur)
    out = []
    for i, g in enumerate(groups):
        start = g[0]["start"]
        end = (
            groups[i + 1][0]["start"]
            if i + 1 < len(groups)
            else min(dur, g[-1]["end"] + 0.4)
        )
        out.append((start, max(0.3, end - start), " ".join(x["text"] for x in g)))
    return out


def cargar(root: Path) -> dict[str, Callable[[str], Scene]]:
    global ROOT, VO, PLAN
    ROOT, VO, PLAN = root, locucion(root), escenas(root)
    path = root / "diseno.py"
    if not path.exists():
        return {}
    spec = importlib.util.spec_from_file_location("diseno", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.ESCENAS


def index_html(scenes: list[str], audio: list[str], total: float) -> str:
    lines = "\n".join(f"      {x}" for x in [*scenes, "{captions}", *audio]).strip()
    captions = (
        f'<div id="hcaptions" data-track-kind="captions" '
        f'data-composition-id="captions" '
        f'data-composition-src="compositions/captions.html" data-start="0" '
        f'data-duration="{total:.2f}" data-track-index="1" '
        f'data-width="{W}" data-height="{H}"></div>'
    )
    return f"""<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden;
        background: {PAPER}; }}
      #root {{ position: relative; width: 100%; height: 100%; background: {PAPER}; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0"
      data-duration="{total:.2f}" data-width="{W}" data-height="{H}">
      {lines.replace("{captions}", captions)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""


def captions_html(caps: list[str], total: float) -> str:
    lines = "\n".join(f"        {c}" for c in caps).strip()
    return f"""<!doctype html>
<html>
  <head><meta charset="UTF-8" /></head>
  <body>
    <template>
      <style>
        #root {{ position: absolute; inset: 0; }}
        .cap {{ position: absolute; left: 160px; right: 160px; top: 918px;
          height: 120px; display: flex;
          align-items: center; justify-content: center; text-align: center; }}
        .cap span {{ font: 600 42px/1.2 Montserrat, sans-serif; color: {INK};
          letter-spacing: -.01em; }}
      </style>
      <div id="root" data-composition-id="captions" data-width="{W}" data-height="{H}"
        data-duration="{total:.2f}">
        {lines}
      </div>
      <script>
        window.__timelines["captions"] = gsap.timeline({{ paused: true }});
      </script>
    </template>
  </body>
</html>
"""


def continuidad(order: list[str], designed: dict) -> None:
    """Avisa de los saltos entre tomas seguidas: una toma debe empezar en la página
    y el scroll donde acabó la anterior, y no deshacer su propio scroll."""
    prev = None
    for sid in order:
        if sid in designed:
            prev = None
            continue
        c = clip(sid)
        if "url_inicio" in c:
            lo, hi = c["scroll_max"] - c["scroll_fin"], 200
            if lo > hi:
                print(f"  {sid}: baja y vuelve a subir ({lo:.0f}px): revisa el scroll")
            if prev:
                name, last = prev
                same = last["url_fin"].split("?")[0] == c["url_inicio"].split("?")[0]
                if not same or abs(last["scroll_fin"] - c["scroll_inicio"]) > 200:
                    print(f"  {name}→{sid}: salto de página o de scroll: ver CONTINUA")
            prev = (sid, c)


def main() -> None:
    root = proyecto(sys.argv[1])
    designed = cargar(root)
    for sid, scene in PLAN.items():
        if sid not in VO or VO[sid].get("text") != scene["voiceover"]:
            raise ValueError(f"{sid}: falta locución vigente; ejecuta voz.py")
        if sid not in designed:
            clip(sid)
    # Lo generado se rehace entero: si no, una escena renumerada o borrada deja
    # su composición vieja apuntando a tomas que ya no existen.
    shutil.rmtree(root / "assets/stills", ignore_errors=True)
    shutil.rmtree(root / "compositions/frames", ignore_errors=True)
    (root / "compositions/frames").mkdir(parents=True)
    t = 0.0
    scenes, audio, caps = [], [], []
    global LAST_CAM, RESET_AT_END
    order = list(PLAN)
    LAST_CAM = (BASE_S, 0.0, 0.0)
    revision = []
    for i, sid in enumerate(order):
        # Una escena diseñada empieza con el plano abierto: la toma anterior lo
        # recupera al final en vez de cortar desde un acercamiento.
        RESET_AT_END = i + 1 < len(order) and order[i + 1] in designed
        if sid in designed:
            LAST_CAM = (BASE_S, 0.0, 0.0)
        d, html = designed[sid](sid) if sid in designed else recorded(sid)
        if sid not in designed:
            marks = [t + m["t"] for m in clip(sid)["marks"] if m["name"] != "zoom"]
            revision.append(f"{sid} " + ",".join(f"{x:.1f}" for x in marks))
        src = PLAN[sid]["src"]
        (root / src).parent.mkdir(parents=True, exist_ok=True)
        (root / src).write_text(html)
        scenes.append(
            f'<div id="h{sid}" data-composition-id="s{sid}" '
            f'data-composition-src="{src}" data-start="{t:.2f}" '
            f'data-duration="{d:.2f}" data-track-index="0" '
            f'data-width="{W}" data-height="{H}"></div>'
        )
        vs = t + lead(sid)
        v = VO[sid]
        audio.append(
            f'<audio id="vo{sid}" src="{v["path"]}" data-start="{vs:.2f}" '
            f'data-duration="{v["duration_s"]:.2f}" data-track-index="2" '
            f'data-volume="1"></audio>'
        )
        chunks = caption_chunks(v["words"], v["duration_s"])
        for k, (ct, cd, text) in enumerate(chunks):
            caps.append(
                f'<div class="cap clip" id="cap{sid}-{k}" data-start="{vs + ct:.2f}" '
                f'data-duration="{cd:.2f}" data-track-index="1">'
                f"<span>{escape(text)}</span></div>"
            )
        t += d
    (root / "index.html").write_text(index_html(scenes, audio, t))
    (root / "compositions/captions.html").write_text(captions_html(caps, t))
    (root / "assets/marcas.txt").write_text("\n".join(revision) + "\n")
    print(f"{len(VO)} escenas, {t:.1f}s ({int(t // 60)}:{t % 60:04.1f})")
    continuidad(order, designed)


if __name__ == "__main__":
    sys.modules.setdefault("montaje", sys.modules[__name__])
    main()
