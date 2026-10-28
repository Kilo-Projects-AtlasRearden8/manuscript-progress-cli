# Manuscript Progress CLI

A local-first command-line tool for authors to track manuscript word count,
chapter progress, and writing streaks. Data stays on your machine in a JSON
file, and you can export sessions to CSV whenever you like.

Built by Dylan Asdale for **Asdale Dynamics, LLC** — beginner-friendly AI
education, books and guides, and practical tools the LLC can publish or sell.
No cloud, no API keys, no personal data.

## What it does

- `init` — start a new manuscript with an optional target word count
- `add` — log a writing session (chapter, words, optional date/title)
- `status` — see total words, per-chapter progress, current streak, and longest streak
- `export` — dump all sessions to a CSV file

## Install

Python 3.8+ is required. No external dependencies — only the standard library.

```bash
git clone <this-repo>
cd manuscript-progress-cli
```

No installation needed; run the module directly:

```bash
python3 manuscript_cli.py --help
```

## Usage

Initialize a manuscript:

```bash
python3 manuscript_cli.py init "The Massive AI Manual" --target 80000
```

This creates `manuscript.json` in the current folder. Use `--file` to store it
elsewhere.

Log a writing session:

```bash
python3 manuscript_cli.py add 1 1200
python3 manuscript_cli.py add 2 900 --date 2026-10-27 --title "Chapter Two"
```

Check progress:

```bash
python3 manuscript_cli.py status
```

Export to CSV:

```bash
python3 manuscript_cli.py export sessions.csv
```

## Storage

All data lives in a local JSON file (`manuscript.json` by default). Nothing is
sent anywhere. Back it up by copying the file.

## Tests

Run the test suite (totals and date math):

```bash
python3 -m unittest discover -s tests
```

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See `LICENSE`.

## About

Created by Dylan Asdale, registered nurse turned AI author and founder of
Asdale Dynamics, LLC (Indiana, formed Oct 2026). Asdale Dynamics publishes
beginner-friendly AI education, books and guides, and practical open-source
tools. Learn more at dylanasdale.github.io.
