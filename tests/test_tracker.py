import os
import sys
import tempfile
import unittest
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tracker import add_item, check, load, remove_item, status_of, parse_date


class TestTracker(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.tmp.close()
        os.unlink(self.tmp.name)  # start with no file
        self.path = self.tmp.name

    def tearDown(self):
        if os.path.exists(self.path):
            os.unlink(self.path)

    def test_status_windows(self):
        today = date(2026, 10, 24)
        self.assertEqual(status_of(date(2026, 10, 1), today), "expired")
        self.assertEqual(status_of(date(2026, 11, 10), today), "expiring-soon")
        self.assertEqual(status_of(date(2026, 12, 20), today), "watch")
        self.assertEqual(status_of(date(2027, 6, 1), today), "ok")

    def test_add_list_remove(self):
        add_item(self.path, "Paracetamol 500mg", "2027-03-01", qty=20)
        self.assertEqual(len(load(self.path)), 1)
        with self.assertRaises(ValueError):
            add_item(self.path, "paracetamol 500mg", "2027-03-01")  # duplicate, case-insensitive
        remove_item(self.path, "Paracetamol 500mg")
        self.assertEqual(load(self.path), [])
        with self.assertRaises(ValueError):
            remove_item(self.path, "Missing")

    def test_check_groups(self):
        add_item(self.path, "Old Syrup", "2026-09-01")
        add_item(self.path, "Soon Tabs", "2026-11-01")
        add_item(self.path, "Fine Caps", "2027-12-01")
        report = check(self.path, today=date(2026, 10, 24))
        g = report["groups"]
        self.assertEqual([i["name"] for i in g["expired"]], ["Old Syrup"])
        self.assertEqual([i["name"] for i in g["expiring-soon"]], ["Soon Tabs"])
        self.assertEqual([i["name"] for i in g["ok"]], ["Fine Caps"])

    def test_bad_date_rejected(self):
        with self.assertRaises(ValueError):
            add_item(self.path, "Bad", "not-a-date")

    def test_bad_storage_rejected(self):
        with self.assertRaises(ValueError):
            add_item(self.path, "Bad", "2027-01-01", storage="freezer-room")


if __name__ == "__main__":
    unittest.main()
