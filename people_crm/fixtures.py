"""Labelled fixtures with literal, independently planted expectations. No randomness."""
import json
from pathlib import Path


def generate(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    records = []
    for i in range(1, 201):
        due = "2026-09-29" if i <= 40 else "2026-09-30" if i <= 60 else "2026-10-15" if i <= 100 else None
        records.append({"id": f"p{i:03}", "name": f"Fixture Person {i}",
                        "context": f"Synthetic school or outreach contact {i}",
                        "last_interaction": None if i > 170 else "2026-09-20",
                        "follow_up": due, "synthetic": True})
    write_json(out / "manifest.json", {"synthetic": True, "as_of": "2026-09-30", "description": "Synthetic fixture, no real people"})
    (out / "people.jsonl").write_text("# Synthetic fixture: no real people\n" + "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records), encoding="utf-8")
    # Hand-counted partitions: 1..40 overdue, 41..60 today, 61..100 upcoming,
    # 101..200 unscheduled; 171..200 have no interaction. These overlap only as documented.
    write_json(out / "expectations.json", {"synthetic": True, "counts": {"total": 200, "overdue": 40, "due_today": 20, "upcoming": 40, "unscheduled": 100, "no_interaction": 30},
        "case_ids": {"overdue": [f"p{i:03}" for i in range(1, 41)], "due_today": [f"p{i:03}" for i in range(41, 61)], "upcoming": [f"p{i:03}" for i in range(61, 101)], "unscheduled": [f"p{i:03}" for i in range(101, 201)], "no_interaction": [f"p{i:03}" for i in range(171, 201)]}})


def write_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
