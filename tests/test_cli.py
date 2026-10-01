import json
import time
from people_crm.cli import main, workflow
from people_crm.report import render


def test_run_completes_on_fixture(fixture_dir, tmp_path):
    start = time.perf_counter()
    assert main(["run", "--input", str(fixture_dir), "--state", str(tmp_path / "state.json")]) == 0
    assert main(["report", "--state", str(tmp_path / "state.json")]) == 0
    assert time.perf_counter() - start < 5


def test_empty_input_renders_without_traceback(tmp_path):
    result = workflow(tmp_path)
    assert all(value == 0 for value in result["counts"].values())
    assert "Empty input" in render(result, "md")


def test_malformed_input_named_error(fixture_dir, capsys):
    (fixture_dir / "people.jsonl").write_text("# Synthetic\n{bad\n")
    assert main(["run", "--input", str(fixture_dir)]) == 2
    assert "ParseError: people.jsonl: line 2" in capsys.readouterr().err


def test_determinism_byte_identical(fixture_dir, tmp_path):
    path = tmp_path / "state.json"
    args = ["run", "--input", str(fixture_dir), "--state", str(path)]
    assert main(args) == 0
    first = path.read_bytes()
    assert main(args) == 0
    assert path.read_bytes() == first
    assert render(workflow(fixture_dir), "md") == render(workflow(fixture_dir), "md")


def test_cli_smoke_all_subcommands(tmp_path, capsys):
    inputs = tmp_path / "inputs"
    state = tmp_path / "state.json"
    for args in (["fixtures", "--out", str(inputs)], ["run", "--input", str(inputs), "--state", str(state)], ["report", "--state", str(state), "--format", "json"], ["followups", "--input", str(inputs)], ["person", "--input", str(inputs), "--id", "p001"]):
        assert main(args) == 0
    assert "synthetic" in capsys.readouterr().out


def test_missing_input_named_error(tmp_path, capsys):
    assert main(["run", "--input", str(tmp_path / "missing")]) == 2
    assert "MissingInput" in capsys.readouterr().err


def test_schema_error_names_field(fixture_dir, capsys):
    path = fixture_dir / "people.jsonl"
    path.write_text('{"amount": -1}\n')
    assert main(["run", "--input", str(fixture_dir)]) == 2
    assert "amount" in capsys.readouterr().err


def test_report_write_failure_no_partial_files(fixture_dir, tmp_path, capsys):
    state = tmp_path / "state.json"
    assert main(["run", "--input", str(fixture_dir), "--state", str(state)]) == 0
    target = tmp_path / "target"
    target.mkdir()
    before = set(tmp_path.iterdir())
    assert main(["report", "--state", str(state), "--out", str(target)]) == 2
    assert "WriteError" in capsys.readouterr().err
    assert set(tmp_path.iterdir()) == before
