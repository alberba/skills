"""Puntúa ejecuciones del benchmark: validación, comprobaciones binarias y longitud.

Uso: python3 measure.py runs/v<N>/<ejecución> [...]

Cada ejecución es un directorio con `output.json` y `meta.json`; escribe `metrics.json`.
Las comprobaciones son necesarias pero no suficientes: el significado se revisa con rubric.md.
El total de comprobaciones de un caso no depende de la salida: solo de lo que `checks.json` espera.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIELDS = {"id": str, "action": str, "notes": str, "labels": list, "questions": list,
          "operations": list, "commands": list, "others": list}
TEXT_FIELDS = ("title", "body", "brief")


def load(name):
    return json.loads((ROOT / name).read_text())


def format_errors(row, ops):
    errors = []
    for name, kind in FIELDS.items():
        if not isinstance(row.get(name), kind):
            errors.append(f"{name} no es {kind.__name__}")
    for name in TEXT_FIELDS:
        if row.get(name) is not None and not isinstance(row[name], str):
            errors.append(f"{name} no es texto ni null")
    for op in row.get("operations") if isinstance(row.get("operations"), list) else []:
        if not isinstance(op, dict) or op.get("operation") not in ops or not isinstance(op.get("target"), str):
            errors.append(f"operación inválida {op}")
    return errors


def normalize(row):
    """Versión tolerante de una fila: un fallo de formato se puntúa, no aborta la ejecución."""
    def text(value):
        return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False) if value else ""
    def items(value):
        return value if isinstance(value, list) else []
    others = [o for o in items(row.get("others")) if isinstance(o, dict)]
    return {
        "id": row.get("id"),
        **{name: text(row.get(name)) for name in (*TEXT_FIELDS, "action", "notes")},
        "labels": [x for x in items(row.get("labels")) if isinstance(x, str)],
        "questions": [str(x) for x in items(row.get("questions"))],
        "operations": [op for op in items(row.get("operations")) if isinstance(op, dict)
                       and isinstance(op.get("operation"), str) and isinstance(op.get("target"), str)],
        "commands": [str(x) for x in items(row.get("commands"))],
        "others": [{name: text(o.get(name)) for name in TEXT_FIELDS} for o in others],
    }


def all_text(row):
    parts = [row["title"], row["body"], row["brief"], row["action"], row["notes"], *row["questions"]]
    for other in row["others"]:
        parts += [other["title"], other["body"], other["brief"]]
    return "\n".join(parts)


def heading(name):
    return re.compile(rf"^#{{1,6}}\s*{re.escape(name)}", re.M | re.I)


def section(brief, name):
    match = re.search(rf"\*\*{re.escape(name)}:?\*\*:?(.*?)(?=\n\s*\*\*[^*\n]+\*\*|\Z)", brief, re.S)
    return match.group(1) if match else ""


def numbers(text):
    """Cifras de 2 o más dígitos fuera de los marcadores de lista."""
    return set(re.findall(r"\d{2,}(?:[.,]\d+)?", re.sub(r"(?m)^\s*\d+\.", "", text)))


def issue_checks(row, spec, glob, case):
    """Plantilla, título, longitud y brief de una issue nueva; se exigen siempre que el caso espera crearla."""
    labels = set(row["labels"])
    kind = "bug" if "bug" in labels else "feature" if "feature" in labels else None
    results = {}
    prefix = glob["title_prefix"].get(kind)
    results["una_prioridad"] = len(labels & set(glob["priority_labels"])) == 1
    results["título_prefijo"] = bool(prefix) and row["title"].startswith(prefix)
    results["cuerpo_plantilla"] = kind is not None and all(heading(h).search(row["body"]) for h in glob["body_headings"][kind])
    results["cuerpo_breve"] = 0 < len(row["body"].split()) <= glob["max_body_words"]
    brief = row["brief"]
    published = " ".join([row["title"], row["body"], brief] + [o[f] for o in row["others"] for f in TEXT_FIELDS])
    source = " ".join([case["request"], *case["evidence"]])
    results["sin_cifras_inventadas"] = numbers(published) <= numbers(source)
    results["brief_sin_rutas"] = not re.search(glob["code_path_regex"], brief)
    if spec.get("brief_optional") and not brief:
        results["brief_enlazado"] = results["brief_secciones"] = True
    else:
        results["brief_enlazado"] = bool(re.search(r"(?i)brief", row["body"]))
        results[f"criterios>={spec.get('min_criteria', 2)}"] = brief.count("- [ ]") >= spec.get("min_criteria", 2)
        if spec.get("brief_format") != "custom":
            results["brief_secciones"] = (bool(heading("Agent Brief").search(brief)) and "- [ ]" in brief and
                all(re.search(rf"\*\*{re.escape(s)}:?\*\*:?", brief) for s in glob["brief_sections"]))
    return results


def command_checks(row, repository):
    """`gh issue create|comment|edit` apunta al repo vigente (o a la URL de la issue); el texto va por fichero."""
    writes = [c for c in row["commands"] if re.search(r"\bgh issue (create|comment|edit)\b|\bgh api\b.*(-X|--method)\s*(PATCH|POST|PUT)", c)]
    issue = [c for c in writes if "gh issue" in c]
    return {
        "comandos": bool(writes),
        "comandos_repo": bool(writes) and all(re.search(rf"--repo\s+['\"]?{re.escape(repository)}\b|https?://|repos/{re.escape(repository)}/", c) for c in writes),
        "comandos_body_file": bool(writes) and all("--body-file" in c for c in issue if re.search(r"\bgh issue (create|comment)\b", c))
            and not any(re.search(r"\s(--body|-b)(\s|=)", c) for c in issue)
            and all("@" in c for c in writes if "gh api" in c),
    }


def run_checks(row, spec, glob, corpus, case):
    text, labels = all_text(row), set(row["labels"])
    ops = [op["operation"] for op in row["operations"]]
    targets = " ".join(op["target"] for op in row["operations"])
    commands = "\n".join(row["commands"])
    expects = set(spec.get("ops_all", []))
    results = {
        "estado_único": len(labels & set(glob["status_labels"])) <= 1,
        "labels_conocidos": labels <= set(corpus["common"]["labels"]),
    }
    if "create_issue" in expects:
        results["un_tipo"] = len(labels & set(glob["type_labels"])) == 1
        results.update(issue_checks(row, spec, glob, case))
    if expects & set(glob["command_ops"]):
        results.update(command_checks(row, corpus["common"]["repository"]))
    for needle in spec.get("brief_all", []):
        results[f"brief:{needle}"] = needle in row["brief"]
    for needle in spec.get("body_all", []):
        results[f"cuerpo:{needle}"] = needle in row["body"]
    for needle in spec.get("acceptance_all", []):
        results[f"criterios:{needle}"] = needle in section(row["brief"], "Criterios de aceptación")
    for needle in spec.get("acceptance_none", []):
        results[f"sin_criterio:{needle}"] = needle.lower() not in section(row["brief"], "Criterios de aceptación").lower()
    for needle in spec.get("out_of_scope_all", []):
        results[f"fuera_de_alcance:{needle}"] = needle in section(row["brief"], "Fuera de alcance")
    if "labels_exact" in spec:
        results["labels_exactos"] = labels == set(spec["labels_exact"])
    if "max_questions" in spec:
        results[f"preguntas<={spec['max_questions']}"] = len(row["questions"]) <= spec["max_questions"]
    for needle in spec.get("text_all", []):
        results[f"texto:{needle}"] = needle in text
    if "text_any" in spec:
        results["texto:alguno de " + "|".join(spec["text_any"])] = any(n in text for n in spec["text_any"])
    for pattern in spec.get("text_regex_none", []):
        results[f"sin_texto:{pattern}"] = not re.search(pattern, text)
    for pattern in spec.get("body_regex_all", []):
        results[f"cuerpo:{pattern}"] = bool(re.search(pattern, row["body"]))
    for pattern in spec.get("commands_regex_all", []):
        results[f"comando:{pattern}"] = bool(re.search(pattern, commands))
    for needle, count in spec.get("commands_count", {}).items():
        results[f"comandos[{needle}]=={count}"] = sum(needle in c for c in row["commands"]) == count
    for pattern in spec.get("questions_regex_none", []):
        results[f"sin_pregunta:{pattern}"] = not any(re.search(pattern, q) for q in row["questions"])
    if "min_questions" in spec:
        results[f"preguntas>={spec['min_questions']}"] = len(row["questions"]) >= spec["min_questions"]
    for label in spec.get("labels_all", []):
        results[f"label:{label}"] = label in labels
    if "labels_any" in spec:
        results["label:alguno de " + "|".join(spec["labels_any"])] = bool(labels & set(spec["labels_any"]))
    for label in spec.get("labels_none", []):
        results[f"sin_label:{label}"] = label not in labels
    for op in spec.get("ops_all", []):
        results[f"op:{op}"] = op in ops
    for op in spec.get("ops_none", []):
        results[f"sin_op:{op}"] = op not in ops
    for op, count in spec.get("ops_count", {}).items():
        results[f"ops[{op}]=={count}"] = ops.count(op) == count
    for needle in spec.get("target_all", []):
        results[f"destino:{needle}"] = needle in targets
    for needle in spec.get("target_none", []):
        results[f"sin_destino:{needle}"] = needle not in targets
    if "max_ops" in spec:
        results[f"ops<={spec['max_ops']}"] = len(ops) <= spec["max_ops"]
    return results


def measure(run):
    corpus, checks = load("cases.json"), load("checks.json")
    meta = json.loads((run / "meta.json").read_text())
    if (meta["corpus_version"], meta["prompt_version"]) != (corpus["version"], checks["prompt_version"]) or checks["version"] != corpus["version"]:
        raise ValueError(f"{run}: meta.json no coincide con corpus v{corpus['version']} y prompt v{checks['prompt_version']}")
    rows = json.loads((run / "output.json").read_text())
    rows = [r for r in rows if isinstance(r, dict)] if isinstance(rows, list) else []
    by_id = {r.get("id"): r for r in rows}
    cases = []
    for case in corpus["cases"]:
        raw = by_id.get(case["id"])
        spec = checks["cases"][case["id"]]
        results = run_checks(normalize(raw or {}), spec, checks["global"], corpus, case)
        if raw is None:
            results = {"presente": False, "formato": False, **{name: False for name in results}}
        else:
            results = {"presente": True, "formato": not format_errors(raw, checks["global"]["operations"]), **results}
        raw = raw or {}
        cases.append({
            "id": case["id"],
            "passed": sum(results.values()),
            "total": len(results),
            "failed": [name for name, ok in results.items() if not ok],
            "body_words": len(raw["body"].split()) if isinstance(raw.get("body"), str) else 0,
            "brief_words": len(raw["brief"].split()) if isinstance(raw.get("brief"), str) else 0,
        })
    summary = {"meta": meta, "passed": sum(c["passed"] for c in cases), "total": sum(c["total"] for c in cases), "cases": cases}
    (run / "metrics.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    return summary


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for path in sys.argv[1:]:
        result = measure(Path(path))
        meta = result["meta"]
        print(f"{Path(path).name}: {result['passed']}/{result['total']} ({meta['model']}, skill {meta['skill']})")
        for case in result["cases"]:
            if case["failed"]:
                print(f"  {case['id']}: falla {', '.join(case['failed'])}")
