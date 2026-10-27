"""Step 5 tests: data accuracy.

These tests check the books independently of the service code:
- a long, repeatable run of random stock changes
- every level equals the sum of its movements
- reports agree with raw SQL calculations
- the over-issue flag matches the running balance
- the database itself refuses malformed movements

Run from the backend folder:  python -m unittest discover -s tests -v
"""

import os
import random
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db import connect, init_db  # noqa: E402
from app.errors import DomainError, OverIssueWarning  # noqa: E402
from app.services.catalog_service import CatalogService  # noqa: E402
from app.services.report_service import ReportService  # noqa: E402
from app.services.search_service import SearchService  # noqa: E402
from app.services.stock_service import StockService  # noqa: E402


class BooksTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.conn = connect(self.tmp.name)
        init_db(self.conn)
        self.catalog = CatalogService(self.conn)
        self.stock = StockService(self.conn)
        self.reports = ReportService(self.conn)
        self.search = SearchService(self.conn)

        cat = self.catalog.create_category("Cups")["id"]
        self.locations = [
            self.catalog.create_location("Main Warehouse")["id"],
            self.catalog.create_location("Showroom")["id"],
        ]
        self.items = [
            self.catalog.create_item("CUP-CER-001", "White ceramic cup", cat, 250, 100)["id"],
            self.catalog.create_item("CUP-TRV-003", "Travel mug", cat, 675, 30)["id"],
            self.catalog.create_item("CUP-PAP-002", "Paper cup", cat, 400, 40)["id"],
        ]

    def tearDown(self):
        self.conn.close()
        os.unlink(self.tmp.name)

    def movement_count(self):
        return self.conn.execute("SELECT COUNT(*) FROM stock_movement").fetchone()[0]

    def assert_books_balance(self):
        """Every level equals the sum of its movements, for every item and location."""
        for item in self.items:
            for loc in self.locations:
                level, total = self.stock.check_consistency(item, loc)
                self.assertEqual(
                    level, total,
                    f"item {item} location {loc}: level {level} != movements {total}")

    def assert_reports_match_raw_sql(self):
        """Reports must agree with calculations done directly in SQL."""
        raw_value = self.conn.execute(
            """SELECT COALESCE(SUM(s.quantity * i.unit_cost_cents), 0)
               FROM stock_level s JOIN item i ON i.id = s.item_id
               WHERE i.is_active = 1""").fetchone()[0]
        self.assertEqual(self.reports.valuation()["total_value_cents"], raw_value)

        raw_units = self.conn.execute(
            """SELECT COALESCE(SUM(s.quantity), 0)
               FROM stock_level s JOIN item i ON i.id = s.item_id
               WHERE i.is_active = 1""").fetchone()[0]
        dash = self.reports.dashboard()
        self.assertEqual(dash["totals"]["total_units"], raw_units)

        raw_negative = self.conn.execute(
            """SELECT COUNT(*) FROM stock_level s JOIN item i ON i.id = s.item_id
               WHERE i.is_active = 1 AND s.quantity < 0""").fetchone()[0]
        self.assertEqual(dash["totals"]["negative_count"], raw_negative)
        self.assertEqual(len(self.reports.negative_stock()), raw_negative)

    def assert_over_issue_flags_are_correct(self):
        """Replay each level's movements in order. An OUT is flagged exactly
        when the balance after it is below zero; no other type is flagged."""
        rows = self.conn.execute(
            """SELECT item_id, location_id, movement_type, quantity_change, over_issue
               FROM stock_movement ORDER BY id""").fetchall()
        balance = {}
        for r in rows:
            key = (r["item_id"], r["location_id"])
            balance[key] = balance.get(key, 0) + r["quantity_change"]
            if r["movement_type"] == "OUT":
                self.assertEqual(bool(r["over_issue"]), balance[key] < 0)
            else:
                self.assertEqual(r["over_issue"], 0)

    def assert_turnover_is_consistent(self):
        """For a window covering all movements: opening is zero, closing equals
        the level, and units sold equals the OUT movements."""
        today = datetime.now(timezone.utc).date()
        start = (today - timedelta(days=1)).isoformat()
        end = (today + timedelta(days=1)).isoformat()
        report = self.reports.turnover(start, end)
        for row in report["rows"]:
            item_total = sum(self.stock.get_quantity(row["item_id"], loc)
                             for loc in self.locations)
            self.assertEqual(row["opening_stock"], 0)
            self.assertEqual(row["closing_stock"], item_total)
            raw_out = -self.conn.execute(
                """SELECT COALESCE(SUM(quantity_change), 0) FROM stock_movement
                   WHERE item_id = ? AND movement_type = 'OUT'""",
                (row["item_id"],)).fetchone()[0]
            self.assertEqual(row["units_sold"], raw_out)


class RandomActivityTests(BooksTestCase):
    def test_long_random_run_keeps_books_balanced(self):
        rng = random.Random(20261027)  # fixed seed, so every run is the same
        accepted = warned = refused = 0

        for step in range(400):
            item = rng.choice(self.items)
            loc = rng.choice(self.locations)
            qty = rng.randint(1, 40)
            roll = rng.random()
            before = self.movement_count()

            try:
                if roll < 0.40:
                    self.stock.receive_stock(item, loc, qty, "Delivery")
                elif roll < 0.85:
                    self.stock.issue_stock(item, loc, qty, "Sale")
                elif roll < 0.95:
                    delta = rng.choice([qty, -qty])
                    self.stock.adjust_stock(item, loc, delta, "Stock count")
                else:
                    # Sometimes confirm an over-issue, as a user would after the warning.
                    self.stock.issue_stock(item, loc, qty, "Sale", confirm=True)
                accepted += 1
            except OverIssueWarning:
                # A warning must write nothing.
                warned += 1
                self.assertEqual(self.movement_count(), before)
                if rng.random() < 0.5:
                    self.stock.issue_stock(item, loc, qty, "Sale", confirm=True)
                    accepted += 1
            except DomainError:
                refused += 1
                self.assertEqual(self.movement_count(), before)

            if step % 50 == 49:
                self.assert_books_balance()

        self.assert_books_balance()
        self.assert_reports_match_raw_sql()
        self.assert_over_issue_flags_are_correct()
        self.assert_turnover_is_consistent()

        # The run must exercise the interesting paths, or the test proves little.
        self.assertGreater(accepted, 200)
        self.assertGreater(warned, 0)

    def test_search_totals_match_stock_levels(self):
        rng = random.Random(7)
        for _ in range(120):
            item = rng.choice(self.items)
            loc = rng.choice(self.locations)
            if rng.random() < 0.6:
                self.stock.receive_stock(item, loc, rng.randint(1, 30), "Delivery")
            else:
                try:
                    self.stock.issue_stock(item, loc, rng.randint(1, 30), "Sale")
                except OverIssueWarning:
                    pass
        for row in self.search.search():
            for level in row["levels"]:
                self.assertEqual(
                    level["quantity"],
                    self.stock.get_quantity(row["item_id"], level["location_id"]))
            self.assertEqual(row["total"], sum(l["quantity"] for l in row["levels"]))


class DatabaseGuardTests(BooksTestCase):
    """The database refuses malformed movements, even if the service is bypassed."""

    def insert_raw(self, movement_type, change, over_issue=0):
        self.conn.execute(
            """INSERT INTO stock_movement
               (item_id, location_id, movement_type, quantity_change, reason,
                over_issue, created_at)
               VALUES (?, ?, ?, ?, 'raw', ?, '2026-01-01T00:00:00+00:00')""",
            (self.items[0], self.locations[0], movement_type, change, over_issue))

    def test_zero_change_is_refused(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.insert_raw("ADJUST", 0)

    def test_in_must_be_positive(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.insert_raw("IN", -5)

    def test_out_must_be_negative(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.insert_raw("OUT", 5)

    def test_unknown_movement_type_is_refused(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.insert_raw("TRANSFER", 5)

    def test_duplicate_sku_is_refused_by_database(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                """INSERT INTO item (sku, name, category_id, unit_cost_cents, reorder_level)
                   VALUES ('CUP-CER-001', 'dup', 1, 1, 1)""")


if __name__ == "__main__":
    unittest.main()
