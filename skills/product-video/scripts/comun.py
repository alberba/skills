"""Lo que comparten voz.py, grabador.py y montaje.py: proyecto, guion y claves.

Un proyecto es una carpeta de HyperFrames (`videos/<proyecto>/`, con
`hyperframes.json`) cuyo STORYBOARD.md tiene un bloque por escena:

    ## Frame 27 — Promociones
    - src: compositions/frames/27-promociones.html
    - voiceover: "Creas promociones con fecha de inicio y de fin, …"
    - section: Promociones      (opcional: texto de la barra de la ventana)
    - lead: 1.5                 (opcional: segundos antes de que hable la voz)

El STORYBOARD es la única fuente del texto, del `lead` y de la sección: el
grabador y el montaje leen lo mismo, así que la voz, el vídeo y la cámara
cuadran sin copiar números entre archivos.
"""

import hashlib
import json
import math
import os
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEAD, TAIL = 0.35, 0.75  # silencio antes de la voz y después, en cada escena


def norm(t: str) -> str:
    """Palabra sin tildes, mayúsculas ni puntuación, para casar con la locución.
    ElevenLabs pega los signos a la palabra: «¿Sabes», «pedido?», «"tarifa"»."""
    t = unicodedata.normalize("NFD", t.lower())
    return re.sub(
        r"[^a-z0-9ñ]", "", "".join(c for c in t if unicodedata.category(c) != "Mn")
    )


def proyecto(arg: str) -> Path:
    root = Path(arg).resolve()
    if not (root / "hyperframes.json").exists():
        sys.exit(f"{root} no es un proyecto de HyperFrames (falta hyperframes.json)")
    return root


def escenas(root: Path) -> dict[str, dict]:
    """{id: {title, src, voiceover, section, lead}} en el orden del STORYBOARD."""
    text = (root / "STORYBOARD.md").read_text()
    out = {}
    for m in re.finditer(
        r"^## Frame (\d+) — (.+?)\n(.*?)(?=^## |\Z)", text, re.S | re.M
    ):
        sid, body = f"{int(m.group(1)):02d}", m.group(3)

        def field(name: str, body: str = body) -> str | None:
            f = re.search(rf"^- {name}: (.+)$", body, re.M)
            return f.group(1).strip() if f else None

        if sid in out:
            raise ValueError(f"Frame duplicado: {sid}")
        src = field("src")
        path = Path(src or "")
        if (not src or path.is_absolute() or ".." in path.parts
                or path.parts[:2] != ("compositions", "frames") or path.suffix != ".html"):
            raise ValueError(f"{sid}: src debe estar dentro de compositions/frames/ y acabar en .html")
        if any(v["src"] == src for v in out.values()):
            raise ValueError(f"src duplicado: {src}")
        voice = field("voiceover")
        if not voice or not voice.strip('" '):
            raise ValueError(f"{sid}: este kit requiere voiceover en cada frame")
        lead = float(field("lead") or LEAD)
        if not math.isfinite(lead) or lead < 0:
            raise ValueError(f"{sid}: lead debe ser finito y no negativo")
        out[sid] = {
            "title": m.group(2).strip(),
            "src": field("src"),
            "voiceover": voice.strip('"') if voice else None,
            "section": field("section"),
            "lead": lead,
        }
    if len(out) != len(re.findall(r"^## Frame\b", text, re.M)):
        raise ValueError("Hay un encabezado Frame no válido: usa ## Frame N — Título")
    if not out:
        raise ValueError("STORYBOARD.md no contiene frames válidos")
    return out


def locucion(root: Path) -> dict[str, dict]:
    return json.loads((root / "assets" / "vo" / "vo.json").read_text())


def firma_voz(vo: dict, lead: float) -> str:
    """Huella de lo que fija el tiempo de una toma: las palabras de la voz y el
    `lead`. El grabador la guarda en el JSON de la toma y el montaje la compara:
    una toma grabada con otra voz (texto o velocidad) no se monta."""
    data = {
        "words": vo.get("words", []), "lead": lead,
        "provider": vo.get("provider"), "speed": vo.get("speed"),
        "duration_s": vo.get("duration_s"), "text": vo.get("text"),
    }
    return hashlib.sha1(json.dumps(data).encode()).hexdigest()[:10]


def credenciales(root: Path) -> None:
    """Variables del entorno o, si faltan, de `<proyecto>/.env.local` (fuera de
    git según la configuración del repo). `CLAVE=valor` o `export CLAVE=valor`, una por
    línea; el entorno manda."""
    path = root / ".env.local"
    if path.exists():
        for line in path.read_text().splitlines():
            m = re.match(r"\s*(?:export\s+)?([A-Z_][A-Z0-9_]*)=(.*)$", line)
            if m:
                os.environ.setdefault(m.group(1), m.group(2).strip().strip("'\""))
