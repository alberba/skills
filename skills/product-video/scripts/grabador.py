"""Graba tomas web con cursor y marcas sincronizadas con la locución.

Uso: uv run --no-project --with playwright python <SKILL_DIR>/scripts/grabador.py
     <proyecto> [--antes] [--sin-difuminar] [NN ...]

Contrato de escenas.py y configuración: references/grabar.md.
Cada toma deja assets/clips/NN.mp4 y NN.json; --antes usa NN-antes.
"""

import base64
import importlib.util
import inspect
import json
import os
import re
import shutil
import subprocess
import sys
import time
from collections.abc import Callable, Sequence
from pathlib import Path
from types import ModuleType
from urllib.parse import urlsplit

from comun import HERE, TAIL, credenciales, escenas, firma_voz, locucion, norm, proyecto
from playwright.sync_api import (
    Browser,
    BrowserContext,
    Locator,
    Page,
    Route,
    sync_playwright,
)

VIEW = {"width": 1477, "height": 831}
DPR = 1.3  # 1477x831 CSS px -> 1920x1080 de vídeo
BASE = "http://localhost:8000"
DIFUMINAR = True  # `--sin-difuminar` lo apaga (según el brief)
CSS = (HERE / "pagina.css").read_text()  # modos y cursor
CONFIG = None  # módulo escenas.py del proyecto
INIT = (HERE / "pagina.js").read_text()  # lo que se inyecta en cada página
MOVIL = {
    "viewport": {"width": 390, "height": 764},
    "device_scale_factor": 2,
    "is_mobile": True,
    "has_touch": True,
}
FOCO_MIN = 0.03  # un foco de menos de este tanto de pantalla es una etiqueta suelta
Target = str | Locator  # selector CSS o elemento de Playwright

def permitir_escritura(method: str, url: str, base: str, allowed: Sequence[str]) -> bool:
    """Solo las rutas de escritura explícitas del mismo origen salen al servidor."""
    if method in ("GET", "HEAD", "OPTIONS"):
        return True
    target, origin = urlsplit(url), urlsplit(base)
    return (target.scheme, target.netloc) == (origin.scheme, origin.netloc) and any(
        re.fullmatch(pattern, target.path) for pattern in allowed
    )


def bloquear(route: Route) -> None:
    allowed = getattr(CONFIG, "ALLOW_WRITES", ())
    if permitir_escritura(route.request.method, route.request.url, BASE, allowed):
        route.continue_()
        return
    # La ruta puede contener datos personales: el diagnóstico omite URL y cuerpo.
    print(f"      bloqueado {route.request.method}: escritura no autorizada")
    route.abort("blockedbyclient")


class H:
    """Acciones visibles y marcas, con el reloj de la grabación."""

    def __init__(
        self, page: Page, t0: float, words: Sequence[dict] = (), lead: float = 0.0
    ) -> None:
        self.page = page
        self.lead = lead
        self.t0 = t0
        self.marks = []
        self.mouse = (VIEW["width"] / 2, VIEW["height"] / 2)
        self.words = list(words)
        self.wi = 0  # las palabras se buscan hacia delante: el guion se lee en orden
        self.cue = None
        self.drift = []
        self.small = []
        self.scroll_max = 0
        self.continued = False  # la toma sigue donde acabó otra (CONTINUA)

    # --- Sincronía con la voz

    def at(self, word: str, ahead: float = 0.0) -> None:
        """Espera a que la locución diga `word` (menos `ahead` segundos)."""
        key = norm(word)
        # La misma palabra que la última espera (at() y luego show()): no avanza.
        start = (
            self.wi - 1
            if self.wi and norm(self.words[self.wi - 1]["text"]).startswith(key)
            else self.wi
        )
        for i in range(start, len(self.words)):
            if norm(self.words[i]["text"]).startswith(key):
                self.wi = i + 1
                when = self.lead + self.words[i]["start"]
                self.cue = (word, when)
                rest = when - ahead - self.now()
                if rest > 0:
                    self.pause(rest)
                return
        msg = f"«{word}» no está en la locución"
        raise ValueError(msg)

    def point(
        self,
        name: str,
        target: Target,
        word: str,
        within: str | None = None,
        dur: float = 0.6,
    ) -> None:
        """Lleva el cursor al elemento y lo marca justo cuando se nombra."""
        self.at(word, ahead=dur + 0.1)
        self.move(target, dur)
        self.mark(name, target, within=within)

    def show(
        self, name: str, target: Target, word: str, within: str | None = None
    ) -> None:
        """Marca el elemento cuando se nombra, sin mover el cursor."""
        self.at(word, ahead=0.1)
        self.mark(name, target, within=within)

    def now(self) -> float:
        return time.monotonic() - self.t0

    def pause(self, s: float) -> None:
        self.page.wait_for_timeout(int(s * 1000))

    # --- Elementos

    def modes(self, *names: str) -> None:
        self.page.evaluate(
            "m => { sessionStorage.setItem('rec-modes', JSON.stringify(m));"
            " const html = document.documentElement;"
            " html.className = ''; html.classList.add(...m); }",
            list(names),
        )

    def loc(self, target: Target) -> Locator:
        if isinstance(target, str):
            return self.page.locator(target).locator("visible=true").first
        return target

    def text(self, t: str, *, exact: bool = False) -> Locator:
        """El primer elemento visible con ese texto: la web repite menús ocultos."""
        return self.page.get_by_text(t, exact=exact).locator("visible=true").first

    def _rect(self, js: str, target: Target, arg: object = None) -> list[int]:
        b = self.loc(target).evaluate(js, arg)
        return [round(v * DPR) for v in (b["x"], b["y"], b["width"], b["height"])]

    def box(self, target: Target) -> list[int]:
        b = self.loc(target).bounding_box()
        return [round(v * DPR) for v in (b["x"], b["y"], b["width"], b["height"])]

    def block_box(self, target: Target, levels: int) -> list[int]:
        """Caja del bloque visual que contiene al elemento (tarjeta, fila, panel):
        sube `levels` contenedores con borde, fondo o sombra propios."""
        return self._rect(
            """(el, n) => {
          const visual = e => {
            const s = getComputedStyle(e);
            const parent = getComputedStyle(e.parentElement || e).backgroundColor;
            return parseFloat(s.borderTopWidth) > 0 || s.boxShadow !== 'none'
              || (s.backgroundColor !== 'rgba(0, 0, 0, 0)'
                  && s.backgroundColor !== parent);
          };
          let cur = el, found = 0;
          for (let e = el.parentElement; e && e !== document.body && found < n;
               e = e.parentElement) {
            const r = e.getBoundingClientRect();
            if (r.width > innerWidth * 0.92 || r.height > innerHeight * 0.6) break;
            if (visual(e)) { cur = e; found++; }
          }
          const r = cur.getBoundingClientRect();
          return {x: r.x, y: r.y, width: r.width, height: r.height};
        }""",
            target,
            levels,
        )

    def within_box(self, target: Target, sel: str) -> list[int]:
        return self._rect(
            """(el, sel) => {
          const r = (el.closest(sel) || el).getBoundingClientRect();
          return {x: r.x, y: r.y, width: r.width, height: r.height}; }""",
            target,
            sel,
        )

    def mark(
        self,
        name: str,
        target: Target | list[Target],
        hold: float = 0.0,
        block: int = 0,
        within: str | None = None,
    ) -> None:
        """Marca un elemento: la cámara llega a él y el foco lo enmarca. «zoom»
        solo acerca la cámara, sin foco. `within` enmarca el contenedor más
        cercano que case con ese selector (tarjeta, fila, grupo de campos); una
        lista de elementos enmarca la caja que los reúne."""
        if isinstance(target, list):  # varios elementos: la caja que los reúne
            boxes = [self.box(t) for t in target]
            x0, y0 = min(b[0] for b in boxes), min(b[1] for b in boxes)
            x1 = max(b[0] + b[2] for b in boxes)
            y1 = max(b[1] + b[3] for b in boxes)
            box = [x0, y0, x1 - x0, y1 - y0]
        elif within:
            box = self.within_box(target, within)
        else:
            box = self.block_box(target, block) if block else self.box(target)
        mark = {"t": round(self.now(), 2), "name": name, "box": box}
        if name != "zoom" and box[2] * box[3] < FOCO_MIN * 1920 * 1080:
            self.small.append(name)
        if self.cue and name != "zoom":
            mark["cue"] = self.cue[0]
            self.drift.append((name, self.cue[0], round(mark["t"] - self.cue[1], 2)))
            self.cue = None
        self.marks.append(mark)
        self.scroll_max = max(self.scroll_max, self.scroll_y())
        if hold:
            self.pause(hold)

    # --- Gestos

    def goto(self, path: str) -> None:
        if self.now() < 0.3 and (self.continued or self.page.url == BASE + path):
            return  # la escena ya arranca en esta página
        self.page.goto(BASE + path)
        self.loaded()

    def loaded(self) -> None:
        for _ in range(3):
            try:
                self.page.wait_for_load_state("networkidle")
                self.page.evaluate("document.fonts.ready")
                return
            except Exception:
                self.page.wait_for_timeout(300)

    def move(self, target: Target, dur: float = 0.6) -> None:
        b = self.loc(target).bounding_box()
        x, y = b["x"] + min(b["width"] / 2, 60), b["y"] + b["height"] / 2
        x0, y0 = self.mouse
        t0 = time.monotonic()
        # Por reloj: cada paso cuesta lo suyo y no debe alargar el gesto.
        while True:
            k = min(1.0, (time.monotonic() - t0) / dur)
            e = k * k * k * (k * (6 * k - 15) + 10)  # inercia suave
            self.page.mouse.move(x0 + (x - x0) * e, y0 + (y - y0) * e)
            if k >= 1:
                break
            self.page.wait_for_timeout(16)
        self.mouse = (x, y)

    def click(self, target: Target, dur: float = 0.6) -> None:
        self.move(target, dur)
        self.pause(0.15)
        self.page.mouse.down()
        self.pause(0.08)
        self.page.mouse.up()

    def type(self, target: Target, text: str, delay: int = 85) -> None:
        self.click(target)
        self.page.keyboard.type(text, delay=delay)

    def scroll(self, px: int, dur: float = 0.9) -> None:
        self.page.evaluate(f"window.scrollBy({{top: {px}, behavior: 'smooth'}})")
        self.pause(dur)
        self.scroll_max = max(self.scroll_max, self.scroll_y())

    def scroll_y(self) -> int:
        return round(self.page.evaluate("window.scrollY"))

    def top(self) -> None:
        self.page.evaluate("window.scrollTo({top: 0})")

    def submit(self) -> None:
        with self.page.expect_navigation():
            self.page.keyboard.press("Enter")
        self.loaded()


# --- Sesión, fuera de plano -------------------------------------------------------


def abrir(
    browser: Browser, root: Path, extra_css: str = "", **context: object
) -> tuple[BrowserContext, Page]:
    """Página aislada con filtros de red, CSS de privacidad y cursor."""
    state = root / ".sesion.json"  # sesión temporal: se borra al terminar el vídeo
    opts = {"viewport": VIEW, "device_scale_factor": DPR, "service_workers": "block", **context}
    if state.exists():
        opts["storage_state"] = str(state)
    ctx = browser.new_context(**opts)
    ctx.route("**/*", bloquear)
    css = CSS + extra_css
    ctx.add_init_script(INIT.replace("__CSS__", json.dumps(css)))
    page = ctx.new_page()
    return ctx, page


def css_extra(mod: ModuleType) -> str:
    """El `CSS` de `escenas.py` y, salvo con `--sin-difuminar`, su `DIFUMINAR`."""
    css = getattr(mod, "CSS", "")
    return css + (getattr(mod, "DIFUMINAR", "") if DIFUMINAR else "")


# --- Grabación ----------------------------------------------------------------------


def primera_ruta(sid: str, fn: Callable) -> str:
    """Ruta del primer `h.goto("...")` de la escena, que se carga antes de grabar.
    Se lee del código, así que tiene que ir literal."""
    source = inspect.getsource(fn)
    call = source.find("h.goto(")
    if call < 0:
        return "/"
    first = re.compile(r"""h\.goto\((["'])([^"']+)\1\)""").match(source, call)
    if not first:
        msg = f'{sid}: el primer h.goto debe llevar la ruta literal, h.goto("/ruta/")'
        raise ValueError(msg)
    return first.group(2)


def informe(h: H, lead: float) -> None:
    """Desfase de cada marca, `lead` sugerido y focos que no enmarcan un bloque."""
    for mark_name, word, d in h.drift:
        flag = "  <-- tarde" if d > 0.25 else ""
        print(f"      {mark_name:<28} «{word}» {d:+.2f}s{flag}")
    late = max((d for *_, d in h.drift), default=0)
    if late > 0.25:
        print(f"      lead sugerido: {lead + late + 0.1:.1f} (ahora {lead})")
    for mark_name in h.small:
        print(f"      foco pequeño en «{mark_name}»: enmarca el bloque (within/block)")


def modos_por_defecto(who: str) -> list[str]:
    modes = list(getattr(CONFIG, "MODES", ()))
    return modes + (["no-pointer"] if who == "mobile" else [])


def continuacion(root: Path, mod: ModuleType, sid: str, suffix: str = "") -> dict | None:
    """Dónde acabó la toma de la que `CONTINUA` dice que sigue ésta."""
    prev = getattr(mod, "CONTINUA", {}).get(sid)
    if not prev:
        return None
    c = json.loads((root / "assets/clips" / f"{prev}{suffix}.json").read_text())
    return {"url": c["url_fin"], "scroll": c["scroll_fin"]}


def record(
    browser: Browser,
    root: Path,
    mod: ModuleType,
    sid: str,
    scene: dict,
    vo: dict,
    suffix: str = "",
) -> None:
    fn, who, *rest = mod.SCENES[sid]
    lead = scene["lead"]
    target = vo["duration_s"] + lead + TAIL
    mobile = who == "mobile"
    ctx, page = abrir(browser, root, css_extra(mod), **(MOVIL if mobile else {}))
    setup = getattr(mod, "setup", None)
    if setup:
        setup(page, BASE, who)
    else:
        page.goto(BASE + "/")
    prep = getattr(mod, "PREP", {}).get(sid)
    if prep:
        prep(page, BASE)
    modes = rest[0] if rest else modos_por_defecto(who)
    page.evaluate("m => sessionStorage.setItem('rec-modes', JSON.stringify(m))", modes)
    page.goto("about:blank")

    clips = root / "assets" / "clips"
    name = f"{sid}{suffix}"
    work = clips / f"{name}.frames"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    frames = []
    cdp = ctx.new_cdp_session(page)

    def on_frame(ev: dict) -> None:
        path = work / f"{len(frames):05d}.jpg"
        path.write_bytes(base64.b64decode(ev["data"]))
        frames.append((ev["metadata"]["timestamp"], path))
        try:
            cdp.send("Page.screencastFrameAck", {"sessionId": ev["sessionId"]})
        except Exception:
            pass

    cdp.on("Page.screencastFrame", on_frame)
    # La primera página carga antes de grabar: la escena arranca con la web quieta.
    h = H(page, 0, vo.get("words", ()), lead)
    start = continuacion(root, mod, sid, suffix)
    page.goto(BASE + (start["url"] if start else primera_ruta(sid, fn)))
    h.loaded()
    h.continued = bool(start)
    if start:
        page.evaluate(f"window.scrollTo({{top: {start['scroll']}}})")
        page.wait_for_timeout(300)
    url0, scroll0 = page.url, h.scroll_y()
    size = (780, 1528) if mobile else (1920, 1080)
    cdp.send(
        "Page.startScreencast",
        {"format": "jpeg", "quality": 92, "maxWidth": size[0], "maxHeight": size[1]},
    )
    wall0 = time.time()
    h.t0 = time.monotonic()
    page.set_default_timeout(6000)
    try:
        fn(h)
    except Exception:
        page.screenshot(path=str(clips / f"{name}-error.png"))
        ctx.close()
        raise
    if target > h.now():
        h.pause(target - h.now())
    duration = h.now()
    url1, scroll1 = page.url.removeprefix(BASE), h.scroll_y()
    cdp.send("Page.stopScreencast")
    page.wait_for_timeout(200)
    ctx.close()
    if not frames:
        msg = "la captura no devolvió fotogramas; repite la toma"
        raise RuntimeError(msg)

    # Fotogramas con su marca de tiempo -> vídeo a 30 fps constantes.
    lines = ["ffconcat version 1.0"]
    for i, (stamp, path) in enumerate(frames):
        nxt = frames[i + 1][0] if i + 1 < len(frames) else wall0 + duration
        start = stamp if i else wall0
        lines += [f"file '{path.name}'", f"duration {max(nxt - start, 0.001):.4f}"]
    lines.append(f"file '{frames[-1][1].name}'")
    (work / "frames.ffconcat").write_text("\n".join(lines))
    encode = ["-vf", f"scale={size[0]}:{size[1]}:flags=lanczos,fps=30,format=yuv420p"]
    encode += ["-c:v", "libx264", "-crf", "16", "-preset", "medium"]
    subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0"]
        + ["-i", str(work / "frames.ffconcat"), *encode, "-t", f"{duration:.3f}"]
        + ["-movflags", "+faststart", str(clips / f"{name}.mp4")],
        check=True,
    )
    shutil.rmtree(work)
    (clips / f"{name}.json").write_text(
        json.dumps(
            {
                "duration": round(duration, 2),
                "target": round(target, 2),
                "voz": firma_voz(vo, lead),
                "marks": h.marks,
                "url_inicio": url0.removeprefix(BASE),
                "url_fin": url1,
                "scroll_inicio": scroll0,
                "scroll_fin": scroll1,
                "scroll_max": max(h.scroll_max, scroll1),
            },
            ensure_ascii=False,
            indent=1,
        )
    )
    print(
        f"{name}: {duration:5.2f}s (objetivo {target:5.2f}s), "
        f"{len(frames)} fotogramas, {len(h.marks)} marcas"
    )
    informe(h, lead)


def cargar(root: Path) -> ModuleType:
    """Importa `<proyecto>/escenas.py` (que puede hacer `import grabador`)."""
    global BASE, CONFIG
    credenciales(root)
    spec = importlib.util.spec_from_file_location("escenas", root / "escenas.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    BASE = (os.environ.get("BASE_URL") or getattr(mod, "BASE_URL", BASE)).rstrip("/")
    CONFIG = mod
    if not hasattr(mod, "DIFUMINAR"):
        raise ValueError("Define DIFUMINAR en escenas.py: CSS de privacidad, o vacío con datos sintéticos")
    return mod


def main() -> None:
    global DIFUMINAR
    root = proyecto(sys.argv[1])
    antes = "--antes" in sys.argv
    DIFUMINAR = "--sin-difuminar" not in sys.argv
    if antes:
        os.environ["VERSION"] = "antes"  # lo lee escenas.py
    mod = cargar(root)
    plan, vo = escenas(root), locucion(root)
    ids = [a for a in sys.argv[2:] if not a.startswith("--")] or list(mod.SCENES)
    (root / "assets" / "clips").mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        failed = []
        for sid in ids:
            try:
                record(
                    browser,
                    root,
                    mod,
                    sid,
                    plan[sid],
                    vo[sid],
                    "-antes" if antes else "",
                )
            except Exception as e:  # una escena rota no para las demás
                failed.append(sid)
                print(f"{sid}: ERROR {type(e).__name__}; revisa la captura local")
        browser.close()
        if failed:
            sys.exit("Tomas fallidas: " + ", ".join(failed))


if __name__ == "__main__":
    sys.modules.setdefault("grabador", sys.modules[__name__])
    main()
