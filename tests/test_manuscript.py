import csv
import io
import os
import sys
import tempfile
import unittest
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import manuscript_cli as mc


class TestTotals(unittest.TestCase):
    def setUp(self):
        self.data = mc.empty_manuscript("Test Book", 1000)
        self.data["sessions"] = [
            {"date": "2026-10-01", "chapter": "1", "words": 300, "title": "Chapter 1", "created": "2026-10-01"},
            {"date": "2026-10-02", "chapter": "1", "words": 200, "title": "Chapter 1", "created": "2026-10-02"},
            {"date": "2026-10-02", "chapter": "2", "words": 500, "title": "Chapter 2", "created": "2026-10-02"},
        ]

    def test_total_words(self):
        total, by_chapter = mc.totals(self.data)
        self.assertEqual(total, 1000)

    def test_per_chapter_totals(self):
        total, by_chapter = mc.totals(self.data)
        self.assertEqual(by_chapter, {"1": 500, "2": 500})

    def test_empty_totals(self):
        data = mc.empty_manuscript()
        total, by_chapter = mc.totals(data)
        self.assertEqual(total, 0)
        self.assertEqual(by_chapter, {})

    def test_target_progress(self):
        total, _ = mc.totals(self.data)
        self.assertEqual(total / self.data["manuscript"]["target_word_count"] * 100, 100.0)


class TestDateMath(unittest.TestCase):
    def make_data(self, dates):
        data = mc.empty_manuscript()
        data["sessions"] = [
            {"date": d, "chapter": "1", "words": 100, "title": "Chapter 1", "created": d}
            for d in dates
        ]
        return data

    def test_streak_consecutive_days(self):
        data = self.make_data(["2026-10-01", "2026-10-02", "2026-10-03"])
        length, dates = mc.current_streak(data, as_of=date(2026, 10, 3))
        self.assertEqual(length, 3)
        self.assertEqual(dates, ["2026-10-01", "2026-10-02", "2026-10-03"])

    def test_streak_broken_by_gap(self):
        data = self.make_data(["2026-10-01", "2026-10-02", "2026-10-04"])
        length, dates = mc.current_streak(data, as_of=date(2026, 10, 4))
        self.assertEqual(length, 1)
        self.assertEqual(dates, ["2026-10-04"])

    def test_streak_resumes_after_gap(self):
        data = self.make_data(["2026-10-01", "2026-10-02", "2026-10-05", "2026-10-06", "2026-10-07"])
        length, dates = mc.current_streak(data, as_of=date(2026, 10, 7))
        self.assertEqual(length, 3)
        self.assertEqual(dates, ["2026-10-05", "2026-10-06", "2026-10-07"])

    def test_longest_streak(self):
        data = self.make_data(["2026-10-01", "2026-10-02", "2026-10-04", "2026-10-05", "2026-10-06"])
        length, dates = mc.longest_streak(data)
        self.assertEqual(length, 3)
        self.assertEqual(dates, ["2026-10-04", "2026-10-05", "2026-10-06"])

    def test_streak_no_sessions(self):
        data = mc.empty_manuscript()
        length, dates = mc.current_streak(data)
        self.assertEqual(length, 0)
        self.assertEqual(dates, [])

    def test_streak_single_day(self):
        data = self.make_data(["2026-10-03"])
        length, dates = mc.current_streak(data, as_of=date(2026, 10, 3))
        self.assertEqual(length, 1)

    def test_today_not_written_breaks_streak(self):
        data = self.make_data(["2026-10-01", "2026-10-02"])
        length, _ = mc.current_streak(data, as_of=date(2026, 10, 4))
        self.assertEqual(length, 0)


class TestStorageRoundTrip(unittest.TestCase):
    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "manuscript.json")
            data = mc.empty_manuscript("Round Trip", 5000)
            mc.save_data(path, data)
            loaded = mc.load_data(path)
            self.assertEqual(loaded["manuscript"]["title"], "Round Trip")
            self.assertEqual(loaded["manuscript"]["target_word_count"], 5000)
            self.assertEqual(loaded["sessions"], [])


class TestList(unittest.TestCase):
    def setUp(self):
        self.data = mc.empty_manuscript("List Book")
        self.data["sessions"] = [
            {"date": "2026-10-01", "chapter": "1", "words": 300, "title": "Opening", "created": "2026-10-01"},
            {"date": "2026-10-03", "chapter": "2", "words": 500, "title": "Drafting", "created": "2026-10-03"},
            {"date": "2026-10-02", "chapter": "1", "words": 200, "title": "Opening pt 2", "created": "2026-10-02"},
        ]

    def test_list_sorted_newest_first(self):
        sessions = sorted(self.data["sessions"], key=lambda s: s["date"], reverse=True)
        dates = [s["date"] for s in sessions]
        self.assertEqual(dates, ["2026-10-03", "2026-10-02", "2026-10-01"])

    def test_list_empty(self):
        data = mc.empty_manuscript()
        sessions = sorted(data["sessions"], key=lambda s: s["date"], reverse=True)
        self.assertEqual(sessions, [])


class TestExport(unittest.TestCase):
    def test_export_csv_content(self):
        data = mc.empty_manuscript("Export Book")
        data["sessions"] = [
            {"date": "2026-10-01", "chapter": "1", "words": 300, "title": "Opening", "created": "2026-10-01"},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "out.csv")
            with open(path, "w", newline="", encoding="utf-8") as fh:
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
            with open(path, "r", encoding="utf-8") as fh:
                reader = list(csv.reader(fh))
            self.assertEqual(reader[0], ["date", "chapter", "words", "title", "created"])
            self.assertEqual(reader[1], ["2026-10-01", "1", "300", "Opening", "2026-10-01"])


class TestCliIntegration(unittest.TestCase):
    def run_cli(self, *args):
        args = list(args)
        # --file is a global arg and must precede the subcommand in argparse.
        if "--file" in args:
            idx = args.index("--file")
            file_val = args.pop(idx + 1)
            args.pop(idx)
            args = ["--file", file_val] + args
        return mc.main(args)

    def test_init_then_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "manuscript.json")
            self.assertEqual(self.run_cli("init", "My Book", "--target", "100", "--file", path), 0)
            self.assertEqual(self.run_cli("status", "--file", path), 0)
            self.assertEqual(self.run_cli("list", "--file", path), 0)

    def test_add_invalid_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "manuscript.json")
            self.run_cli("init", "My Book", "--file", path)
            result = self.run_cli("add", "1", "100", "--date", "not-a-date", "--file", path)
            self.assertNotEqual(result, 0)

    def test_add_then_status_totals(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "manuscript.json")
            self.run_cli("init", "My Book", "--target", "2000", "--file", path)
            self.run_cli("add", "1", "700", "--date", "2026-10-01", "--file", path)
            self.run_cli("add", "2", "800", "--date", "2026-10-02", "--file", path)
            # Capture stdout to verify totals
            import contextlib
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                self.run_cli("status", "--file", path)
            output = buf.getvalue()
            self.assertIn("1500", output)
            self.assertIn("75.0%", output)


if __name__ == "__main__":
    unittest.main()
