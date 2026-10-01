# People CRM

People CRM maintains explicitly entered context about people and lists scheduled follow-ups. It runs locally on CPU with Python's standard library. It makes no network calls and uses no language models, database servers, or GPU packages.

Hypothesis: explicit dates, record evidence and deterministic rules provide a trustworthy personal context tool. The acceptance target is exact agreement with planted ground truth on 200 synthetic records, zero false positives, and a complete demo in under five seconds. Synthetic accuracy does not establish accuracy of Henry's real entries or actual usefulness.

## Quickstart

Python 3.10 or newer, with setuptools and pytest already available locally:

```powershell
python -m pip install --no-index --no-deps --no-build-isolation -e .
python -m pytest -q
pc fixtures --out demo
pc run --input demo
pc report --format md
```

The equivalent module entry point is `python -m people_crm.cli`. No dependency downloads are needed. If `pc` is not found after a user install, add the Scripts directory printed by pip to your session PATH, or use the module entry point. Results default to `.people-crm/result.json` relative to the working directory. Use `--state` to keep distinct runs separate. The last successful run remains available if a subsequent run fails. Generated demo and state files are ignored by git.

## Input format

An input directory contains `manifest.json` and `people.jsonl`. An optional `expectations.json` is fixture-only ground truth and is never used in calculations. Other files are rejected, including CSV and YAML: this version deliberately supports JSON and JSONL only. Keep outputs outside the input directory.

Real input manifest, entered by Henry:

```json
{"as_of":"2026-09-30","synthetic":false,"description":"My manually entered contacts"}
```

Each nonblank, noncomment JSONL line is one person. Lines beginning with `#` are comments. All six fields below are required; unknown fields are errors.

```json
{"id":"example-1","name":"Example contact","context":"Illustrative example, replace with your own context","last_interaction":"2026-09-20","follow_up":"2026-10-02","synthetic":true}
```

The example record is illustrative and synthetic. For Henry's real entries set each record's `synthetic` to `false`. The manifest's synthetic flag is true exactly when every record is synthetic; mixed inputs have a false manifest flag and reports count both kinds independently. A nonempty manifest with no records uses true under this rule.

IDs are unique, exact and case sensitive. Text must be nonblank, at most 10,000 characters, and contain no control characters or em dash. Unicode and literal Windows paths are supported; JSON backslashes must be escaped. Dates use strict `YYYY-MM-DD`. `last_interaction` and `follow_up` allow null. An interaction later than `as_of` is rejected. Future follow-ups are allowed and classified as upcoming. Invalid dates, duplicate IDs, extreme text and unknown fields such as negative monetary amounts produce named schema errors rather than silently dropping data. No money field exists in this domain model.

An entirely empty directory computes zero counts. Its fixed placeholder date is 1970-01-01 and explicitly labelled in the banner. Missing directories produce `MissingInput` with a usage hint. Malformed JSON produces `ParseError` naming file and line. JSONL schema failures identify field, file and line; cross-record duplicate errors identify the file and ID. File encoding must be UTF-8. `WriteError` names failed report output; atomic replacement prevents partial report files and preserves an existing destination on failure.

## Commands

```powershell
pc fixtures --out demo
pc run --input demo --state .people-crm/demo.json
pc report --state .people-crm/demo.json --format json --out report.json
pc report --state .people-crm/demo.json --format md
pc followups --input demo
pc person --input demo --id p001
```

Every command supports `--help` with an example. `followups` returns only explicitly overdue or due-today records. `person` retrieves recorded context by exact ID; missing IDs produce `MissingPerson`. Their JSON counts and case IDs describe the whole input, while the people list is the requested view. `report` renders the last saved computation, so rerun after editing inputs. Reports include the input file hashes used in that computation.

Overdue means `follow_up < as_of`; due today means equality; upcoming means greater; unscheduled means null. These four counts partition the total. No interaction means `last_interaction` is null and overlaps the scheduling categories. It does not mean Henry has never met the person. IDs, dates, context and synthetic flags are included in report evidence.

## Architecture

```text
manifest.json + people.jsonl
             |
     cli.load: parse and validate
             |
     core.compute: pure date rules and counts
             |
     deterministic result + provenance + SHA-256 sources
             |
     atomic local state -> report.render -> Markdown or JSON

fixtures.generate -> labelled records + independent expectations
pytest -> core, CLI, fixtures, reports, adversarial checks
```

Record order is canonical by ID. Dates come from the manifest, never the clock. There is no random generator, so no random seed is needed. Identical input bytes and arguments produce byte-identical saved results and reports on repeated runs. No timestamps or absolute machine paths enter saved reports. Output destination messages naturally reflect the explicit arguments.

## Honesty boundary and fixtures

This tool computes from supplied records. It does not discover relationships, predict responses, infer priorities, verify identities, or estimate time or money saved. Savings remain null and labelled unmeasured on every report. No hypothetical savings are displayed. Real flags are the author's declarations, not independent verification. Reports explicitly identify synthetic and declared real record counts.

Fixtures contain 200 fictional people, labelled synthetic in every record and manifest. JSONL has a synthetic header comment; JSON does not support comments, so JSON fixture files contain a `synthetic: true` field and the manifest carries a description. Hand-computed expectations describe the planted ranges: IDs 1 to 40 overdue, 41 to 60 due today, 61 to 100 upcoming, 101 to 200 unscheduled, and 171 to 200 without interaction. Tests check every case ID, counts and reconciliation. A mutation test changes a planted date and verifies changed counts, proving the report is computed. Expectations never feed the engine.

The shipped `examples/five` directory is a hand-written five-record synthetic input: run `pc run --input examples/five` followed by `pc report --format md`. Its counts are total 5, overdue 1, due today 1, upcoming 1, unscheduled 2 and no interaction 1. The five-record hand-written core test establishes these rules independently. Empty input, malformed input, schema drift, duplicates, future interactions, long Unicode context and write failures are also tested.

## Two-week improvement hook and verdict

Start the evidence window only when Henry begins real use. Keep real trial data and results private and outside the shipped repo. For 14 days record dates used and hand-check the follow-up classification of an explicit sample against entered dates. Metric: wrong classifications divided by classifications checked. Record numerator, denominator and sampling method; zero samples means unmeasured, not zero error. Optionally measure elapsed task time against the same manually performed baseline before claiming time savings.

If error exceeds 10 percent, fix the largest measured cause and repeat the check or kill the project with a written reason. If Henry does not use it during the window, record that finding and kill it. No improvement based on real usage has yet been claimed.

Verdict: pending the two-week real-use evidence window. Record the final date, evidence and reason privately: expand if it earns daily use or revenue; integrate if it substantially overlaps a sibling tool; commercialise if a buyer would pay as-is; maintain as portfolio evidence otherwise; kill if unused or unable to meet acceptance criteria. The local synthetic acceptance evidence is in `EVIDENCE.md`, and domain lessons are in `LESSONS.md`. Public publishing is a separate verification step and is not performed by this build.
