#!/usr/bin/env python3
"""manuscript_cli.py

Local-first CLI for authors to track manuscript word count, chapter progress,
and writing streaks. Stores data in a local JSON file and exports CSV.

No cloud, no keys, no personal data.
Copyright (c) 2026 Asdale Dynamics, LLC
"""

import argparse
import csv
import json
import os
import sys
from datetime import date, datetime, timedelta

DEFAULT_STORAGE = "manuscript.json"


def today_iso():
    return date.today().isoformat()


def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


def empty_manuscript(title="Untitled Manuscript", target_word_count=None):
    return {
        "manuscript": {
            "title": title,
            "target_word_count": target_word_count,
            "created": today_iso(),
        },
        "sessions": [],
    }


def load_data(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def save_data(path, data):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def init_manuscript(path, title, target_word_count):
    if os.path.exists(path):
        print(f"Error: {path} already exists.")
        return 1
    data = empty_manuscript(title, target_word_count)
    save_data(path, data)
    print(f"Initialized manuscript '{title}' at {path}")
    if target_word_count:
        print(f"Target word count: {target_word_count}")
    return 0


def add_session(path, chapter, words, date_iso, title=None):
    data = load_data(path)
    if data is None:
        print(f"Error: no manuscript at {path}. Run 'init' first.")
        return 1
    try:
        parse_date(date_iso)
    except ValueError:
        print(f"Error: invalid date '{date_iso}'. Use YYYY-MM-DD.")
        return 1
    session = {
        "date": date_iso,
        "chapter": str(chapter),
        "words": int(words),
        "title": title or f"Chapter {chapter}",
        "created": today_iso(),
    }
    data["sessions"].append(session)
    save_data(path, data)
    print(f"Added {words} words to chapter {chapter} on {date_iso}.")
    return 0


def sessions_by_date(data):
    by_date = {}
    for session in data["sessions"]:
        by_date.setdefault(session["date"], []).append(session)
    return by_date


def totals(data):
    total = 0
    by_chapter = {}
    for session in data["sessions"]:
        words = int(session["words"])
        total += words
        chapter = str(session["chapter"])
        by_chapter[chapter] = by_chapter.get(chapter, 0) + words
    return total, by_chapter


def current_streak(data, as_of=None):
    """Consecutive writing days counting back from as_of (defaults to today).

    Returns (length, dates) where dates are the streak days in ISO format.
    """
    if as_of is None:
        cursor = date.today()
    elif isinstance(as_of, str):
        cursor = parse_date(as_of)
    else:
        cursor = as_of
    by_date = sessions_by_date(data)
    if not by_date:
        return 0, []
    date_set = {parse_date(d) for d in by_date}
    length = 0
    while cursor in date_set:
        length += 1
        cursor -= timedelta(days=1)
    streak_dates = [(cursor + timedelta(days=i + 1)).isoformat() for i in range(length)]
    return length, streak_dates


def longest_streak(data):
    """Longest run of consecutive days with at least one session."""
    by_date = sessions_by_date(data)
    if not by_date:
        return 0, []
    day_objs = sorted(parse_date(d) for d in by_date)
    best_len = 0
    best_dates = []
    cur_len = 0
    cur_start = None
    prev = None
    for day in day_objs:
        if prev is not None and day == prev + timedelta(days=1):
            cur_len += 1
        else:
            cur_len = 1
            cur_start = day
        if cur_len > best_len:
            best_len = cur_len
            best_dates = [(cur_start + timedelta(days=i)).isoformat() for i in range(cur_len)]
        prev = day
    return best_len, best_dates


def chapter_sort_key(chapter):
    try:
        return (0, int(chapter))
    except (TypeError, ValueError):
        return (1, chapter)


def cmd_status(args):
    data = load_data(args.file)
    if data is None:
        print(f"Error: no manuscript at {args.file}. Run 'init' first.")
        return 1
    total, by_chapter = totals(data)
    cur_len, cur_dates = current_streak(data)
    long_len, long_dates = longest_streak(data)
    meta = data["manuscript"]
    target = meta.get("target_word_count")
    pct = (total / target * 100) if target else 0.0
    print(f"Manuscript: {meta.get('title', 'Untitled Manuscript')}")
    if target:
        print(f"Total words: {total} / {target} ({pct:.1f}%)")
    else:
        print(f"Total words: {total}")
    print(f"Chapters written: {len(by_chapter)}")
    for chapter in sorted(by_chapter, key=chapter_sort_key):
        print(f"  Chapter {chapter}: {by_chapter[chapter]} words")
    print(f"Current streak: {cur_len} day(s)" + (f" ({', '.join(cur_dates)})" if cur_dates else ""))
    print(f"Longest streak: {long_len} day(s)" + (f" ({', '.join(long_dates)})" if long_dates else ""))
    return 0


def cmd_export(args):
    data = load_data(args.file)
    if data is None:
        print(f"Error: no manuscript at {args.file}. Run 'init' first.")
        return 1
    output = args.output or "manuscript_export.csv"
    with open(output, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["date", "chapter", "words", "title", "created"])
        for session in data["sessions"]:
            writer.writerow([
                session.get("date", ""),
                session.get("chapter", ""),
                session.get("words", ""),
                session.get("title", ""),
                session.get("created", ""),
            ])
    print(f"Exported {len(data['sessions'])} session(s) to {output}")
    return 0


def cmd_list(args):
    data = load_data(args.file)
    if data is None:
        print(f"Error: no manuscript at {args.file}. Run 'init' first.")
        return 1
    sessions = sorted(data["sessions"], key=lambda s: s.get("date", ""), reverse=True)
    if not sessions:
        print("No writing sessions logged yet.")
        return 0
    total = 0
    print("Writing sessions (newest first):")
    print()
    for session in sessions:
        words = int(session.get("words", 0))
        total += words
        print(f"  {session.get('date', '')}  |  Chapter {session.get('chapter', '')}  |  {words} words  |  {session.get('title', '')}")
    print()
    print(f"Total logged: {total} word(s) across {len(sessions)} session(s).")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        description="Track manuscript word count, chapter progress, and writing streaks (local JSON storage)."
    )
    parser.add_argument(
        "--file", default=DEFAULT_STORAGE, help=f"JSON storage file (default: {DEFAULT_STORAGE})"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Initialize a new manuscript")
    p_init.add_argument("title", nargs="?", default="Untitled Manuscript", help="Manuscript title")
    p_init.add_argument("--target", type=int, default=None, help="Target word count")
    p_init.set_defaults(func=lambda args: init_manuscript(args.file, args.title, args.target))

    p_add = sub.add_parser("add", help="Add a writing session")
    p_add.add_argument("chapter", help="Chapter number or name")
    p_add.add_argument("words", type=int, help="Words written in the session")
    p_add.add_argument("--date", default=today_iso(), help="Session date YYYY-MM-DD (default: today)")
    p_add.add_argument("--title", default=None, help="Chapter title")
    p_add.set_defaults(func=lambda args: add_session(args.file, args.chapter, args.words, args.date, args.title))

    p_status = sub.add_parser("status", help="Show totals, chapter progress, and streaks")
    p_status.set_defaults(func=cmd_status)

    p_export = sub.add_parser("export", help="Export sessions to CSV")
    p_export.add_argument("output", nargs="?", default=None, help="Output CSV file (default: manuscript_export.csv)")
    p_export.set_defaults(func=cmd_export)

    p_list = sub.add_parser("list", help="List all logged writing sessions")
    p_list.set_defaults(func=cmd_list)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
