"""Locución de cada escena con ElevenLabs, con el tiempo de cada palabra.

  uv run --no-project --with elevenlabs \\
    python <SKILL_DIR>/scripts/voz.py videos/<proyecto> [--escuchar]

Lee los `voiceover` del STORYBOARD.md y ELEVENLABS_API_KEY (ver
comun.credenciales). Escribe assets/vo/NN.mp3 y assets/vo/vo.json
({id: {path, duration_s, text, words}}): el grabador espera a esas palabras y
los subtítulos caen con ellas. Solo regenera las frases que cambian, así que
repetir no gasta créditos. `--escuchar` deja además locucion-completa.mp3 con
todas las frases seguidas, para que el desarrollador la oiga entera.

Los tiempos llegan del proveedor junto al audio, sin una transcripción posterior.
"""

import argparse
import base64
import json
import os
import subprocess
import tempfile
from pathlib import Path

from comun import credenciales, escenas, proyecto

GAP = 0.6  # silencio entre frases en locucion-completa.mp3


def words_from(alignment: object) -> list[dict]:
    """Agrupa la alineación por caracteres en palabras con su inicio y fin."""
    words, cur, start, end = [], "", None, None
    for ch, s, e in zip(
        alignment.characters,
        alignment.character_start_times_seconds,
        alignment.character_end_times_seconds,
        strict=True,
    ):
        if ch.isspace():
            if cur:
                words.append(
                    {"text": cur, "start": round(start, 3), "end": round(end, 3)}
                )
            cur, start = "", None
            continue
        if start is None:
            start = s
        cur += ch
        end = e
    if cur:
        words.append({"text": cur, "start": round(start, 3), "end": round(end, 3)})
    return words


def duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration"]
        + ["-of", "csv=p=0", str(path)],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(out.stdout.strip())


def escuchar(root: Path, meta: dict[str, dict]) -> None:
    """Todas las frases seguidas, con una pausa corta entre ellas."""
    out = root / "locucion-completa.mp3"
    with tempfile.TemporaryDirectory() as tmp:
        gap = Path(tmp) / "gap.mp3"
        silence = ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(GAP)]
        subprocess.run(
            ["ffmpeg", "-loglevel", "error", "-y", *silence, "-q:a", "4", str(gap)],
            check=True,
        )
        lst = Path(tmp) / "list.txt"
        lst.write_text(
            "".join(
                f"file '{root / meta[sid]['path']}'\nfile '{gap}'\n" for sid in meta
            )
        )
        subprocess.run(
            ["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0"]
            + ["-i", str(lst), "-ar", "44100", "-ac", "1", "-b:a", "128k", str(out)],
            check=True,
        )
    print("para escuchar:", out)


def estirar(raw: Path, path: Path, speed: float) -> None:
    """`path` = `raw` a `speed` veces su velocidad, sin cambiar el tono (atempo).

    ElevenLabs `eleven_v4_turbo` ignora el ajuste `speed` de la voz, y
    `multilingual_v2`, que sí lo admite, cambia el timbre: se ralentiza el audio ya
    generado, sin gastar créditos."""
    cmd = ["ffmpeg", "-loglevel", "error", "-y", "-i", str(raw)]
    if speed != 1.0:
        cmd += ["-filter:a", f"atempo={speed}"]
    subprocess.run([*cmd, "-b:a", "128k", str(path)], check=True)


def adoptable(old: dict, raw: Path, path: Path, text: str, provider: str) -> bool:
    """Una frase de un `vo.json` anterior a `--velocidad` (sin `raw_words`) que no
    ha cambiado: su audio ya es el crudo y sus `words`, las crudas. Adoptarla
    evita volver a pedirla a ElevenLabs."""
    return (
        "raw_words" not in old
        and old.get("provider") == provider
        and old.get("text") == text
        and path.exists()
        and not raw.exists()
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("proyecto")
    ap.add_argument("--voz", help="id de voz autorizado en tu cuenta")
    ap.add_argument("--modelo", help="modelo de ElevenLabs con alineación")
    ap.add_argument("--idioma", default="es")
    ap.add_argument(
        "--velocidad",
        type=float,
        default=1.0,
        help="velocidad de habla (0,5 a 2; 0,95 = un 5 %% más lenta), sin créditos",
    )
    ap.add_argument("--escuchar", action="store_true")
    args = ap.parse_args()
    root = proyecto(args.proyecto)
    credenciales(root)
    args.voz = args.voz or os.environ.get("ELEVENLABS_VOICE_ID")
    args.modelo = args.modelo or os.environ.get("ELEVENLABS_MODEL_ID")
    if not args.voz or not args.modelo:
        ap.error("indica --voz y --modelo, o ELEVENLABS_VOICE_ID y ELEVENLABS_MODEL_ID")
    if not 0.5 <= args.velocidad <= 2:
        ap.error("--velocidad debe estar entre 0.5 y 2")
    provider = f"elevenlabs:{args.voz}:{args.modelo}:{args.idioma}"
    from elevenlabs.client import ElevenLabs

    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    out = root / "assets" / "vo"
    out.mkdir(parents=True, exist_ok=True)
    meta_path = out / "vo.json"
    old_meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    meta = {}
    for sid, scene in escenas(root).items():
        text = scene["voiceover"]
        if not text:
            continue
        raw, path = out / f"{sid}.raw.mp3", out / f"{sid}.mp3"  # raw = sin estirar
        old = old_meta.get(sid, {})
        if adoptable(old, raw, path, text, provider):
            path.rename(raw)  # grabada antes de `--velocidad`: es el audio sin estirar
            old = {**old, "raw_words": old["words"]}
        if (
            old.get("provider") != provider
            or old.get("text") != text
            or not raw.exists()
            or "raw_words" not in old
        ):
            res = client.text_to_speech.convert_with_timestamps(
                voice_id=args.voz,
                text=text,
                model_id=args.modelo,
                language_code=args.idioma,
                output_format="mp3_44100_128",
            )
            raw.write_bytes(base64.b64decode(res.audio_base_64))
            raw_words = words_from(res.alignment)
        else:
            raw_words = old["raw_words"]
        estirar(raw, path, args.velocidad)
        words = [
            {
                "text": w["text"],
                "start": round(w["start"] / args.velocidad, 3),
                "end": round(w["end"] / args.velocidad, 3),
            }
            for w in raw_words
        ]
        seconds = duration(path)
        meta[sid] = {
            "path": f"assets/vo/{sid}.mp3",
            "duration_s": round(seconds, 3),
            "text": text,
            "words": words,
            "raw_words": raw_words,
            "provider": provider,
            "speed": args.velocidad,
        }
        print(sid, f"{seconds:5.2f}s", text[:60])
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    print("total", round(sum(v["duration_s"] for v in meta.values()), 1), "s")
    if args.escuchar:
        escuchar(root, meta)


if __name__ == "__main__":
    main()
