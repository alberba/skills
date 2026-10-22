"""Regresiones del kit con artefactos locales; no llama a servicios de pago."""
import base64
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[2] / "skills/product-video/scripts"
sys.path.insert(0, str(SCRIPTS))
import comun
import montaje
import voz
import grabador
from playwright.sync_api import sync_playwright


def frame(sid, text="Organiza proyectos."):
    return (f"## Frame {sid} — Escena {sid}\n"
            f"- src: compositions/frames/{sid}.html\n"
            f'- voiceover: "{text}"\n')


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "hyperframes.json").write_text("{}")
        (self.root / "assets/vo").mkdir(parents=True)

    def plan(self, text):
        (self.root / "STORYBOARD.md").write_text(text)
        return comun.escenas(self.root)

    def audio(self, sid="33", text="Organiza proyectos."):
        return {sid: {"text": text, "duration_s": 1.2,
                      "path": f"assets/vo/{sid}.mp3", "provider": "fixture",
                      "speed": 1, "words": [{"text": "Organiza", "start": 0, "end": .5},
                                               {"text": "proyectos.", "start": .6, "end": 1.1}]}}

    def test_storyboard_order_preserves_late_added_intro(self):
        self.assertEqual(list(self.plan(frame(33) + frame(4) + frame(35))), ["33", "04", "35"])

    def test_rejects_ambiguous_and_unsafe_storyboards(self):
        for text in ("", frame(1) + frame(1), frame(1).replace("compositions/frames/1.html", "../outside.html"),
                     frame(1).replace('- voiceover: "Organiza proyectos."', ""),
                     frame(1) + "## Frame 2 - malformed heading\n", frame(1) + "- lead: -1\n"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.plan(text)

    def test_voice_identity_invalidates_take(self):
        vo = self.audio()["33"]
        expected = comun.firma_voz(vo, .35)
        for changed in ({**vo, "speed": .95}, {**vo, "provider": "another-voice"},
                        {**vo, "duration_s": 2}, {**vo, "words": [dict(vo["words"][0], end=.8)]}):
            self.assertNotEqual(expected, comun.firma_voz(changed, .35))
        self.assertNotEqual(expected, comun.firma_voz(vo, 1.5))

    def test_mount_missing_audio_fails_before_deleting_outputs(self):
        self.plan(frame(33) + frame(4))
        (self.root / "assets/vo/vo.json").write_text(json.dumps(self.audio()))
        target = self.root / "compositions/frames/keep.html"
        target.parent.mkdir(parents=True)
        target.write_text("previous preview")
        (self.root / "diseno.py").write_text('ESCENAS = {"33": lambda sid: (1, "intro")}')
        with patch.object(sys, "argv", ["montaje.py", str(self.root)]), self.assertRaises(ValueError):
            montaje.main()
        self.assertEqual(target.read_text(), "previous preview")

    def test_mount_includes_every_approved_frame_in_document_order(self):
        self.plan(frame(33) + frame(4) + frame(35))
        vo = self.audio("33") | self.audio("04") | self.audio("35")
        (self.root / "assets/vo/vo.json").write_text(json.dumps(vo))
        (self.root / "diseno.py").write_text(
            'import montaje as m\nESCENAS = {sid: (lambda sid: m.title(sid, "PROYECTOS", '
            '["Organiza"], "Comparte")) for sid in ("33", "04", "35")}')
        with patch.object(sys, "argv", ["montaje.py", str(self.root)]), contextlib.redirect_stdout(io.StringIO()):
            montaje.main()
        html = (self.root / "index.html").read_text()
        self.assertLess(html.index('id="h33"'), html.index('id="h04"'))
        self.assertLess(html.index('id="h04"'), html.index('id="h35"'))
        self.assertTrue((self.root / "compositions/frames/33.html").exists())
        self.assertIn("Organiza proyectos.", (self.root / "compositions/captions.html").read_text())

    def test_rejects_stale_clip(self):
        self.plan(frame(33))
        montaje.ROOT, montaje.PLAN, montaje.VO = self.root, comun.escenas(self.root), self.audio()
        clips = self.root / "assets/clips"
        clips.mkdir()
        (clips / "33.json").write_text(json.dumps({"voz": "outdated"}))
        with self.assertRaises(SystemExit):
            montaje.clip("33")

    def test_uses_project_brand_without_inherited_creator(self):
        self.plan(frame(33))
        montaje.ROOT, montaje.PLAN, montaje.VO = self.root, comun.escenas(self.root), self.audio()
        brand = self.root / "assets/marca"
        brand.mkdir()
        (brand / "product.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        self.assertEqual(montaje.logo("product"), "assets/marca/product.svg")
        _, html = montaje.closing("33", "Organiza", "Organiza", "missing-credit-word", "fixture.jpg")
        self.assertIn("assets/marca/product.svg", html)
        self.assertNotIn("DESARROLLADO POR", html)
        self.assertNotIn('id="s33-by"', html)
        with self.assertRaises(FileNotFoundError):
            montaje.logo("unconfigured")

    def test_voice_cache_and_speed_use_no_additional_provider_calls(self):
        self.plan(frame(33))
        raw = self.root / "fixture.mp3"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "lavfi", "-i", "sine=duration=1.2",
                        "-y", str(raw)], check=True)
        calls = []

        def convert(**kwargs):
            calls.append(kwargs)
            return SimpleNamespace(audio_base_64=base64.b64encode(raw.read_bytes()), alignment=SimpleNamespace(
                characters=list("Organiza proyectos."),
                character_start_times_seconds=[i * .05 for i in range(19)],
                character_end_times_seconds=[i * .05 + .04 for i in range(19)]))

        sdk = SimpleNamespace(ElevenLabs=lambda **kwargs: SimpleNamespace(
            text_to_speech=SimpleNamespace(convert_with_timestamps=convert)))
        def run(speed="1", language="es"):
            args = ["voz.py", str(self.root), "--voz", "fixture", "--modelo", "fixture",
                    "--velocidad", speed, "--idioma", language]
            with patch.object(sys, "argv", args), contextlib.redirect_stdout(io.StringIO()):
                voz.main()
            return comun.locucion(self.root)["33"]

        with patch.dict(sys.modules, {"elevenlabs.client": sdk}), patch.dict(os.environ, {"ELEVENLABS_API_KEY": "fixture"}):
            first = run()
            run()
            slower = run("0.5")
            self.assertEqual(len(calls), 1)
            self.assertGreater(slower["duration_s"], first["duration_s"] * 1.8)
            self.assertEqual(slower["words"][1]["start"], first["words"][1]["start"] * 2)
            run("1", "en")
            self.assertEqual(len(calls), 2)

    def test_invalid_speed_stops_before_provider(self):
        with patch.object(sys, "argv", ["voz.py", str(self.root), "--voz", "fixture", "--modelo", "fixture", "--velocidad", "0"]):
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                voz.main()


class BrowserTests(unittest.TestCase):
    def test_same_origin_allowlist_is_not_an_external_write_permission(self):
        base = "http://localhost:3000"
        allowed = (r"/api/auth/login",)
        self.assertTrue(grabador.permitir_escritura("POST", base + "/api/auth/login", base, allowed))
        for url in (base + "/api/orders", "https://external.invalid/api/auth/login", base + "/api/auth/login/extra"):
            self.assertFalse(grabador.permitir_escritura("POST", url, base, allowed))
        self.assertFalse(grabador.permitir_escritura("DELETE", base + "/api/orders", base, ()))

    def test_records_portable_scene_to_real_mp4(self):
        with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
            root = Path(tmp)
            (root / "assets/clips").mkdir(parents=True)
            (root / "escenas.py").write_text(
                'BASE_URL = "http://127.0.0.1:1"\nDIFUMINAR = ""\n'
                'def s01(h):\n'
                '    h.page.set_content("<h1>Proyectos</h1>")\n'
                '    h.show("Proyectos", h.text("Proyectos"), "Proyectos")\n'
                'SCENES = {"01": (s01, "desktop")}\n')
            mod = grabador.cargar(root)
            class Handler(BaseHTTPRequestHandler):
                def log_message(self, *_):
                    pass
                def do_GET(self):
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"<html><body><h1>Proyectos</h1></body></html>")
            server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            self.addCleanup(server.server_close)
            self.addCleanup(server.shutdown)
            browser = p.chromium.launch()
            scene = {"lead": .1}
            audio = {"duration_s": .3, "words": [{"text": "Proyectos", "start": 0, "end": .3}]}
            with patch.object(grabador, "BASE", f"http://127.0.0.1:{server.server_port}"), contextlib.redirect_stdout(io.StringIO()):
                grabador.record(browser, root, mod, "01", scene, audio)
            browser.close()
            clip = root / "assets/clips/01.mp4"
            out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0",
                                           "-show_entries", "stream=width,height", "-of", "json", str(clip)])
            self.assertEqual(json.loads(out)["streams"][0], {"width": 1920, "height": 1080})
            metadata = json.loads((root / "assets/clips/01.json").read_text())
            self.assertEqual(metadata["voz"], comun.firma_voz(audio, .1))
            self.assertEqual(metadata["marks"][0]["name"], "Proyectos")
            (root / "hyperframes.json").write_text("{}")
            (root / "STORYBOARD.md").write_text(frame(1, "Proyectos"))
            (root / "assets/vo").mkdir()
            (root / "assets/vo/vo.json").write_text(json.dumps({"01": audio}))
            (root / "escenas.py").write_text(
                f'BASE_URL = "http://127.0.0.1:{server.server_port}"\nDIFUMINAR = ""\n'
                'def broken(h):\n    raise ValueError("fixture failure")\n'
                'SCENES = {"01": (broken, "desktop")}\n')
            failed = subprocess.run([sys.executable, str(SCRIPTS / "grabador.py"), str(root)],
                                    capture_output=True, text=True,
                                    env={**os.environ, "BASE_URL": f"http://127.0.0.1:{server.server_port}"})
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("Tomas fallidas: 01", failed.stderr)
            self.assertTrue((root / "assets/clips/01-error.png").exists())

    def test_browser_masks_dynamic_elements_and_blocks_real_write(self):
        writes = []
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'<html><body><div class="private">synthetic</div></body></html>')
            def do_POST(self):
                writes.append(self.path)
                self.send_response(204)
                self.end_headers()

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
            root = Path(tmp)
            browser = p.chromium.launch()
            config = SimpleNamespace(ALLOW_WRITES=(r"/login",), DIFUMINAR=".private {filter:blur(12px)}")
            with patch.multiple(grabador, CONFIG=config, BASE=f"http://127.0.0.1:{server.server_port}", DIFUMINAR=True):
                ctx, page = grabador.abrir(browser, root, grabador.css_extra(config))
                page.goto(grabador.BASE)
                self.assertEqual(page.locator(".private").evaluate("e => getComputedStyle(e).filter"), "blur(12px)")
                page.evaluate("document.body.insertAdjacentHTML('beforeend', '<div class=private>dynamic</div>')")
                self.assertEqual(page.locator(".private").last.evaluate("e => getComputedStyle(e).filter"), "blur(12px)")
                outcome = page.evaluate("fetch('/orders', {method:'POST'}).then(()=>'sent').catch(()=>'blocked')")
                self.assertEqual(outcome, "blocked")
                page.evaluate("fetch('/login', {method:'POST'})")
                self.assertEqual(writes, ["/login"])
                self.assertEqual(grabador.css_extra(config), config.DIFUMINAR)
                with patch.object(grabador, "DIFUMINAR", False):
                    self.assertEqual(grabador.css_extra(config), "")
                ctx.close()
            browser.close()


if __name__ == "__main__":
    unittest.main()
