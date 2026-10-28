# STATUS

## What was built

`manuscript-progress-cli` — a local-first Python CLI for authors to track
manuscript word count, chapter progress, and writing streaks.

Commands:
- `init [title] [--target N]` — create a new manuscript (writes `manuscript.json`)
- `add <chapter> <words> [--date YYYY-MM-DD] [--title "..."]` — log a writing session
- `status` — total words, target progress, per-chapter totals, current streak, longest streak
- `export [file.csv]` — export all sessions to CSV

Storage: a single local JSON file (`manuscript.json` by default). No cloud, no API
keys, no personal data, no network access. Standard library only (Python 3.8+).

Tests: `tests/test_manuscript.py` — 12 tests covering totals (overall, per-chapter,
empty, target progress) and date math (current streak, longest streak, gaps,
single day, no sessions, storage round-trip).

Files:
- `manuscript_cli.py` — CLI implementation
- `tests/test_manuscript.py` — unittest suite
- `LICENSE` — MIT, Copyright (c) 2026 Asdale Dynamics, LLC
- `README.md` — usage docs, credits Asdale Dynamics, LLC
- `.gitignore` — Python defaults plus local data files
- `STATUS.md` — this file

Built for Dylan Asdale / Asdale Dynamics, LLC (Indiana, formed Oct 2026) —
beginner-friendly AI education, books, guides, and practical open-source tools.
Credited in README and LICENSE.

## How to run

```bash
cd manuscript-progress-cli
python3 manuscript_cli.py init "My Book" --target 80000
python3 manuscript_cli.py add 1 1200 --date 2026-10-25 --title "Opening"
python3 manuscript_cli.py add 2 900 --date 2026-10-26
python3 manuscript_cli.py status
python3 manuscript_cli.py export sessions.csv
python3 -m unittest discover -s tests
```

## Verification results

- `python3 -m unittest discover -s tests`: 12 tests, OK
- CLI smoke test: init, add (3 sessions across 2 chapters), status, and CSV export
  all ran successfully; output matched expectations (2700 words, 3.4% of 80k target,
  longest streak 3 days: 2026-10-25..2026-10-27)
- `python3 -m py_compile manuscript_cli.py tests/test_manuscript.py`: clean

## Known gaps

- Streak math is anchored to an explicit date (default: today); no multi-user or
  sync support (by design, local-first only).
- Chapter sort handles numeric names numerically; other names sort lexically.
- No editing or deleting of existing sessions; sessions are append-only.
- No config file; storage path set via `--file` per invocation.
