# Local acceptance evidence

Measured on 2026-10-01 on this Windows machine with Python 3.12.10 and pytest 8.3.5. CPU only; no external network calls, models or GPU workloads.

- `python -m pytest -q`: 25 passed in 0.38 seconds.
- Installed `pc.exe` end-to-end demo, three subprocesses: 0.709325 seconds measured with `time.perf_counter`, including fixture generation, run and Markdown report rendering.
- Fixture computed counts: total 200, overdue 40, due today 20, upcoming 40, unscheduled 100, no recorded interaction 30.
- Tests assert equality of every planted case ID against independent expectations. False positives: zero on this synthetic fixture. Missed planted cases: zero on this synthetic fixture.
- Changing p001's date to null gives overdue 39 and unscheduled 101. Expectations are never read by the engine.
- Repeated run outputs are byte-identical. All five installed subcommand help pages exit successfully.
- Source, tests and Markdown documentation scanned for forbidden em dash: none found.

This is measured synthetic acceptance evidence. It does not measure actual time saved, real-world data accuracy, daily use, revenue or willingness to pay. Savings are unmeasured. Real trial results are not shipped. The two-week verdict is pending real use, as described in README.md.
