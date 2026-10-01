import pytest
from people_crm.core import compute, InputError


def person(**changes):
    return {"id": "one", "name": "Henry", "context": "School", "last_interaction": "2026-09-20", "follow_up": "2026-09-29", "synthetic": False, **changes}


@pytest.mark.parametrize("change", [{"amount": -1}, {"last_interaction": "2026-10-01"}, {"name": "x" * 10001}, {"synthetic": "true"}, {"follow_up": "bad"}, {"name": "a\u2014b"}])
def test_rejects_adversarial_values(change):
    with pytest.raises(InputError, match="SchemaError"):
        compute([person(**change)], "2026-09-30")


def test_duplicate_ids():
    with pytest.raises(InputError, match="duplicate"):
        compute([person(), person()], "2026-09-30")


def test_handles_unicode_and_long_inputs():
    result = compute([person(name="Zoë 李", context="C:\\Users\\henry\\" + "é" * 9000)], "2026-09-30")
    assert result["people"][0]["name"] == "Zoë 李"


def test_hand_written_five_records():
    records = [person(id=str(i), follow_up=due, last_interaction=None if i == 4 else "2026-09-20") for i, due in enumerate(["2026-09-29", "2026-09-30", "2026-10-01", None, None])]
    assert compute(records, "2026-09-30")["counts"] == {"total": 5, "overdue": 1, "due_today": 1, "upcoming": 1, "unscheduled": 2, "no_interaction": 1}
