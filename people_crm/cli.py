"""Local file CLI. Example: pc fixtures --out demo; pc run --input demo."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
import sys

from .core import InputError, compute
from .fixtures import generate
from .report import render


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InputError(f"ParseError: {path.name}: line {exc.lineno}: {exc.msg}") from None


def load(directory):
    directory = Path(directory)
    if not directory.is_dir():
        raise InputError(f"MissingInput: {directory}: use pc fixtures --out <dir> or supply an input directory")
    files = sorted(p for p in directory.iterdir() if p.is_file())
    unexpected = [p.name for p in files if p.name not in {"manifest.json", "people.jsonl", "expectations.json"}]
    if unexpected:
        raise InputError(f"SchemaError: unsupported input files: {unexpected}")
    if not files:
        return compute([], "1970-01-01"), []
    if not (directory / "manifest.json").exists() or not (directory / "people.jsonl").exists():
        raise InputError("MissingInput: manifest.json and people.jsonl required; see pc run --help")
    manifest = read_json(directory / "manifest.json")
    if not isinstance(manifest, dict) or set(manifest) != {"as_of", "synthetic", "description"} or type(manifest.get("synthetic")) is not bool or not isinstance(manifest.get("description"), str):
        raise InputError("SchemaError: manifest.json: fields must be as_of, synthetic, description")
    records = []
    for number, line in enumerate((directory / "people.jsonl").read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise InputError(f"ParseError: people.jsonl: line {number}: {exc.msg}") from None
        try:
            compute([record], manifest["as_of"])
        except InputError as exc:
            raise InputError(f"{exc}: people.jsonl: line {number}") from None
        records.append(record)
    try:
        result = compute(records, manifest["as_of"])
    except InputError as exc:
        raise InputError(f"{exc}: people.jsonl") from None
    if manifest["synthetic"] != all(r["synthetic"] for r in records):
        raise InputError("SchemaError: manifest.json: synthetic must match whether all records are synthetic")
    sources = [{"file": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in files if p.name != "expectations.json"]
    return result, sources


def workflow(directory):
    result, sources = load(directory)
    synthetic = sum(p["synthetic"] for p in result["people"])
    real = len(result["people"]) - synthetic
    result["provenance_banner"] = f"Data provenance: {synthetic} synthetic fixture records; {real} real records declared by the input author (Henry's own manually entered data when supplied by Henry). Identity and truth are not independently verified."
    if not result["people"]:
        result["provenance_banner"] += " Empty input; 1970-01-01 is a fixed placeholder as_of, not an observation date."
    result["sources"] = sources
    return result


def atomic_write(path, content):
    path = Path(path)
    temporary = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(content)
        os.replace(temporary, path)
    except OSError as exc:
        raise InputError(f"WriteError: {path}: {exc.strerror}") from None
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def parser():
    root = argparse.ArgumentParser(description="People CRM: deterministic local context tracking, no estimates.")
    sub = root.add_subparsers(dest="command", required=True)
    fixture = sub.add_parser("fixtures", help="Generate 200 labelled synthetic records", epilog="Example: pc fixtures --out demo")
    fixture.add_argument("--out", required=True)
    run = sub.add_parser("run", help="Compute context and follow-up report", epilog="Example: pc run --input demo")
    run.add_argument("--input", required=True)
    run.add_argument("--state", default=".people-crm/result.json")
    report = sub.add_parser("report", help="Render a computed report", epilog="Example: pc report --format md")
    report.add_argument("--format", choices=("md", "json"), default="md")
    report.add_argument("--state", default=".people-crm/result.json")
    report.add_argument("--out", help="Atomically write instead of printing")
    due = sub.add_parser("followups", help="Show explicit overdue and due-today follow-ups", epilog="Example: pc followups --input demo")
    due.add_argument("--input", required=True)
    person = sub.add_parser("person", help="Show all recorded context for an exact person ID", epilog="Example: pc person --input demo --id p001")
    person.add_argument("--input", required=True)
    person.add_argument("--id", required=True)
    return root


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    args = parser().parse_args(argv)
    try:
        if args.command == "fixtures":
            generate(args.out)
            print("Generated 200 synthetic records. No measured savings.")
        elif args.command == "run":
            result = workflow(args.input)
            atomic_write(args.state, render(result, "json"))
            print(result["provenance_banner"])
            print(f"Computed {result['counts']['total']} records; saved {args.state}. Savings unmeasured.")
        elif args.command == "report":
            content = render(read_json(Path(args.state)), args.format)
            if args.out:
                atomic_write(args.out, content)
            else:
                print(content, end="")
        else:
            result = workflow(args.input)
            if args.command == "followups":
                result["people"] = [p for p in result["people"] if p["follow_up_status"] in ("overdue", "due_today")]
            else:
                result["people"] = [p for p in result["people"] if p["id"] == args.id]
                if not result["people"]:
                    raise InputError(f"MissingPerson: id {args.id}")
            print(render(result, "json"), end="")
        return 0
    except (InputError, OSError, UnicodeError, KeyError, TypeError) as exc:
        label = str(exc) if isinstance(exc, InputError) else f"FileError: {exc}"
        print(label, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
