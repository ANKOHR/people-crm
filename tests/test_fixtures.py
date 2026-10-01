import json
from people_crm.cli import workflow


def test_fixtures_labelled_synthetic(fixture_dir):
    assert (fixture_dir / "people.jsonl").read_text().startswith("# Synthetic")
    for name in ("manifest.json", "expectations.json"):
        assert json.loads((fixture_dir / name).read_text())["synthetic"] is True
    assert all(p["synthetic"] for p in workflow(fixture_dir)["people"])


def test_fixture_ground_truth_matches_hand_computed(fixture_dir):
    expected = json.loads((fixture_dir / "expectations.json").read_text())
    actual = workflow(fixture_dir)
    assert actual["counts"] == expected["counts"]
    assert actual["case_ids"] == expected["case_ids"]


def test_corrupt_ground_truth_changes_computed_report(fixture_dir):
    path = fixture_dir / "people.jsonl"
    lines = path.read_text().splitlines()
    record = json.loads(lines[1])
    record["follow_up"] = None
    lines[1] = json.dumps(record)
    path.write_text("\n".join(lines) + "\n")
    result = workflow(fixture_dir)
    assert result["counts"]["overdue"] == 39
    assert result["counts"]["unscheduled"] == 101
    assert "p001" not in result["case_ids"]["overdue"]
