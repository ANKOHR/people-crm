import json
from people_crm.cli import workflow
from people_crm.report import render


def test_report_matches_ground_truth_exact(fixture_dir):
    report = json.loads(render(workflow(fixture_dir), "json"))
    expected = json.loads((fixture_dir / "expectations.json").read_text())
    assert report["counts"] == expected["counts"]
    assert sum(report["counts"][k] for k in ("overdue", "due_today", "upcoming", "unscheduled")) == 200


def test_report_zero_false_positives(fixture_dir):
    result = workflow(fixture_dir)
    expected = json.loads((fixture_dir / "expectations.json").read_text())
    for key in expected["case_ids"]:
        assert set(result["case_ids"][key]) == set(expected["case_ids"][key])


def test_report_carries_provenance_banner(fixture_dir):
    for fmt in ("md", "json"):
        output = render(workflow(fixture_dir), fmt)
        assert "Data provenance:" in output
        assert "200 synthetic fixture records; 0 real records" in output


def test_hypothetical_figures_labelled(fixture_dir):
    result = workflow(fixture_dir)
    assert result["savings"] == {"status": "unmeasured", "time_saved": None, "money_saved": None}
    assert "unmeasured" in render(result, "md")


def test_no_em_dashes_in_outputs(fixture_dir):
    for fmt in ("md", "json"):
        assert "\u2014" not in render(workflow(fixture_dir), fmt)
