#!/usr/bin/env python3
"""Captura el Chromecast después de enviar teclas opcionales del mando."""

import argparse
import os
import pathlib
import subprocess
import time

p = argparse.ArgumentParser()
p.add_argument("output")
p.add_argument("keys", nargs="*")
a = p.parse_args()
serial = os.environ.get("TV_SERIAL")
if not serial:
    p.error("Indica TV_SERIAL con la IP y puerto ADB actuales")
base = ["adb", "-s", serial]
for key in a.keys:
    subprocess.run(base + ["shell", "input", "keyevent", key], check=True, timeout=15)
    time.sleep(0.4)
time.sleep(1)
r = subprocess.run(
    base + ["exec-out", "screencap", "-p"], check=True, capture_output=True, timeout=20
)
if not r.stdout.startswith(b"\x89PNG\r\n\x1a\n"):
    raise SystemExit("La aplicación no permitió capturar una imagen PNG válida")
path = pathlib.Path(a.output)
path.parent.mkdir(parents=True, exist_ok=True)
path.write_bytes(r.stdout)
print(path)
