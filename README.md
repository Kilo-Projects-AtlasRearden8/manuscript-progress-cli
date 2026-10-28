# Manuscript Progress CLI

A friendly, local-first command-line tool for authors to track manuscript word
count, chapter progress, and writing streaks. Everything stays on your own
computer in a simple JSON file, and you can export your sessions to CSV
whenever you like.

Built by Dylan Asdale for **Asdale Dynamics, LLC** — beginner-friendly AI
education, books and guides, and practical tools the LLC can publish or sell.
No cloud, no API keys, no personal data, no accounts required.

## Who this is for

Writers working on a book, guide, or manuscript who want a dead-simple way to
see how much they've written, which chapters are coming along, and how many
days in a row they've shown up to write. If you prefer tools that stay on your
machine and never phone home, this is for you.

## What it does

| Command | What it does |
|---------|--------------|
| `init` | Start a new manuscript, with an optional target word count |
| `add` | Log a writing session (chapter, how many words, optional date and title) |
| `status` | See total words, progress toward your target, per-chapter totals, current streak, and longest streak |
| `list` | Show every writing session you've logged, newest first |
| `export` | Save all your sessions to a CSV file (great for spreadsheets or backups) |

## Install

Python 3.8 or newer is all you need. There are no external packages to install
— just the standard library that comes with Python.

```bash
git clone <this-repo>
cd manuscript-progress-cli
```

No installation step required. Run the tool directly:

```bash
python3 manuscript_cli.py --help
```

## Usage, step by step

**1. Start a new manuscript**

```bash
python3 manuscript_cli.py init "The Massive AI Manual" --target 80000
```

This creates a `manuscript.json` file in your current folder. The `--target`
is optional — set it if you have a word-count goal in mind.

**2. Log a writing session**

```bash
python3 manuscript_cli.py add 1 1200 --date 2026-10-25 --title "Opening"
python3 manuscript_cli.py add 2 900 --date 2026-10-26
```

- `1` and `2` are your chapter numbers (or names).
- `1200` and `900` are the words you wrote.
- `--date` is optional and defaults to today. Use `YYYY-MM-DD` format.
- `--title` is optional and gives the chapter a friendly name.

**3. Check your progress**

```bash
python3 manuscript_cli.py status
```

You'll see your total words, how far you are toward your target, how many
chapters you've touched, your current writing streak, and your longest streak.

**4. See all your sessions**

```bash
python3 manuscript_cli.py list
```

**5. Export to CSV**

```bash
python3 manuscript_cli.py export sessions.csv
```

Open `sessions.csv` in Excel, Google Sheets, or any spreadsheet app.

## Where your data lives

All data is stored in a local JSON file (`manuscript.json` by default). Nothing
is sent anywhere, ever. Back it up by copying the file somewhere safe. Use
`--file` if you'd rather store it elsewhere:

```bash
python3 manuscript_cli.py --file /path/to/my-manuscript.json status
```

## Tests

Run the test suite (totals and date math):

```bash
python3 -m unittest discover -s tests
```

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See `LICENSE`.

## About

Created by Dylan Asdale, a registered nurse turned AI author and founder of
Asdale Dynamics, LLC (Indiana, formed October 2026). Asdale Dynamics publishes
beginner-friendly AI education, books and guides, and practical open-source
tools — explained plainly, step by step, never condescending. Learn more at
dylanasdale.github.io.
