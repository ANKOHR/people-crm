"""Pure validation and computation. No inferred relationships or savings."""
from datetime import date


class InputError(ValueError):
    """A named input failure suitable for display without a traceback."""


def parse_date(value, field):
    try:
        if not isinstance(value, str) or len(value) != 10:
            raise ValueError()
        return date.fromisoformat(value)
    except ValueError:
        raise InputError(f"SchemaError: {field}: expected YYYY-MM-DD") from None


def validate(records, as_of):
    cutoff = parse_date(as_of, "as_of")
    seen = set()
    allowed = {"id", "name", "context", "last_interaction", "follow_up", "synthetic"}
    for record in records:
        if not isinstance(record, dict):
            raise InputError("SchemaError: record: expected object")
        unknown = set(record) - allowed
        missing = allowed - set(record)
        if unknown or missing:
            raise InputError(f"SchemaError: fields: unknown={sorted(unknown)}, missing={sorted(missing)}")
        for field in ("id", "name", "context"):
            value = record[field]
            if not isinstance(value, str) or not value.strip() or len(value) > 10000:
                raise InputError(f"SchemaError: {field}: expected nonempty text up to 10000 characters")
            if any(ord(c) < 32 for c in value) or "\u2014" in value:
                raise InputError(f"SchemaError: {field}: control characters and em dash forbidden")
        if type(record["synthetic"]) is not bool:
            raise InputError("SchemaError: synthetic: expected boolean")
        if record["id"] in seen:
            raise InputError(f"SchemaError: id: duplicate {record['id']}")
        seen.add(record["id"])
        for field in ("last_interaction", "follow_up"):
            if record[field] is not None:
                parsed = parse_date(record[field], field)
                if field == "last_interaction" and parsed > cutoff:
                    raise InputError("SchemaError: last_interaction: future date relative to as_of")
    return records


def compute(records, as_of):
    validate(records, as_of)
    people = []
    for record in sorted(records, key=lambda r: r["id"]):
        due = record["follow_up"]
        status = "unscheduled" if due is None else "overdue" if due < as_of else "due_today" if due == as_of else "upcoming"
        people.append({**record, "follow_up_status": status})
    ids = {status: [p["id"] for p in people if p["follow_up_status"] == status]
           for status in ("overdue", "due_today", "upcoming", "unscheduled")}
    ids["no_interaction"] = [p["id"] for p in people if p["last_interaction"] is None]
    return {"as_of": as_of, "counts": {"total": len(people), **{k: len(v) for k, v in ids.items()}},
            "case_ids": ids, "people": people,
            "savings": {"status": "unmeasured", "time_saved": None, "money_saved": None}}
