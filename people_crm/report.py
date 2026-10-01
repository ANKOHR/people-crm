"""Reports expose input provenance and refuse unmeasured savings claims."""
import json


def render(result, format):
    if format == "json":
        return json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    lines = ["# People CRM report", "", result["provenance_banner"], "", f"As of: {result['as_of']}", "", "## Computed counts", ""]
    lines.extend(f"- {key}: {value}" for key, value in result["counts"].items())
    lines += ["", "No time or money saved is reported: unmeasured, no measured baseline supplied.", "", "## Record evidence", ""]
    for p in result["people"]:
        lines.append(f"- {p['id']} | {p['name']} | {p['follow_up_status']} | last interaction: {p['last_interaction']} | follow-up: {p['follow_up']} | context: {p['context']} | synthetic: {str(p['synthetic']).lower()}")
    lines += ["", "## Input files", ""]
    lines.extend(f"- {source['file']}: SHA-256 {source['sha256']}" for source in result["sources"])
    return "\n".join(lines) + "\n"
