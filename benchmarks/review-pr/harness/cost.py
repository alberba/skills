"""Coste, tiempo, peticiones y herramientas de cada ejecución, desde su transcripción JSONL.

    python3 cost.py etiqueta=ruta.jsonl [etiqueta=ruta.jsonl ...]

Tarifa por defecto: Sonnet 5.5 ($/M tokens). Para otro modelo, --precios entrada,salida,escritura,lectura.
"""

import argparse
import json
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("--precios", default="2,10,2.5,0.2")
parser.add_argument("runs", nargs="+")
args = parser.parse_args()
p_in, p_out, p_write, p_read = (float(x) for x in args.precios.split(","))

print("run\tmodelo\t$\tmin\tpeticiones\therramientas")
for run in args.runs:
    label, path = run.split("=", 1)
    usage_by_message, models, timestamps, tools = {}, set(), [], 0
    with open(path) as f:
        for line in f:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ts := event.get("timestamp"):
                timestamps.append(datetime.fromisoformat(ts.replace("Z", "+00:00")))
            if event.get("type") != "assistant":
                continue
            message = event.get("message") or {}
            if model := message.get("model"):
                models.add(model)
            # Una respuesta llega en varios eventos con el mismo id: se cuenta una vez.
            if message_id := message.get("id"):
                usage_by_message[message_id] = message.get("usage") or {}
            tools += sum(
                1
                for block in message.get("content") or []
                if isinstance(block, dict) and block.get("type") == "tool_use"
            )

    def total(key):
        return sum(u.get(key, 0) for u in usage_by_message.values())

    cost = (
        total("input_tokens") * p_in
        + total("output_tokens") * p_out
        + total("cache_creation_input_tokens") * p_write
        + total("cache_read_input_tokens") * p_read
    ) / 1e6
    minutes = (max(timestamps) - min(timestamps)).total_seconds() / 60 if timestamps else 0
    print(f"{label}\t{','.join(sorted(models))}\t{cost:.2f}\t{minutes:.1f}\t{len(usage_by_message)}\t{tools}")
