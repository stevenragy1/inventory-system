"""Step 2 tests: stock management rules and data accuracy.

Run from the backend folder:  python -m unittest discover -s tests -v
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db import connect, init_db  # noqa: E402
from app.errors import DomainError, NotFoundError, OverIssueWarning  # noqa: E402
from app.services.catalog_service import CatalogService  # noqa: E402
from app.services.stock_service import StockService  # noqa: E402


class StockTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.conn = connect(self.tmp.name)
        init_db(self.conn)
        self.catalog = CatalogService(self.conn)
        self.stock = StockService(self.conn)

        cat = self.catalog.create_category("Bottles")
        self.warehouse = self.catalog.create_location("Main Warehouse")["id"]
        self.showroom = self.catalog.create_location("Showroom")["id"]
        self.bottle = self.catalog.create_item(
            "BTL-GLS-002", "Glass bottle 500ml", cat["id"], 390, 60)["id"]

    def tearDown(self):
        self.conn.close()
        os.unlink(self.tmp.name)


class CatalogTests(StockTestCase):
    def test_sku_is_unique_and_stored_upper_case(self):
        item = self.catalog.get_item(self.bottle)
        self.assertEqual(item["sku"], "BTL-GLS-002")
        from app.errors import DuplicateError
        with self.assertRaises(DuplicateError):
            self.catalog.create_item("btl-gls-002", "Dup", item["category_id"], 1, 1)

    def test_deactivated_item_cannot_take_stock(self):
        self.catalog.deactivate_item(self.bottle)
        with self.assertRaises(DomainError):
            self.stock.receive_stock(self.bottle, self.warehouse, 5, "Delivery")

    def test_unknown_location_is_rejected(self):
        with self.assertRaises(NotFoundError):
            self.stock.receive_stock(self.bottle, 999, 5, "Delivery")


class StockInTests(StockTestCase):
    def test_receive_increases_level_and_logs_movement(self):
        qty = self.stock.receive_stock(self.bottle, self.warehouse, 120, "Supplier #118")
        self.assertEqual(qty, 120)
        history = self.stock.history(self.bottle)
        self.assertEqual(history[0]["movement_type"], "IN")
        self.assertEqual(history[0]["quantity_change"], 120)
        self.assertEqual(history[0]["over_issue"], 0)

    def test_receive_rejects_zero_or_negative_quantity(self):
        for bad in (0, -5):
            with self.assertRaises(DomainError):
                self.stock.receive_stock(self.bottle, self.warehouse, bad, "x")

    def test_reason_is_required(self):
        with self.assertRaises(DomainError):
            self.stock.receive_stock(self.bottle, self.warehouse, 5, "   ")


class StockOutTests(StockTestCase):
    def setUp(self):
        super().setUp()
        self.stock.receive_stock(self.bottle, self.showroom, 20, "Delivery")

    def test_issue_within_stock_needs_no_confirmation(self):
        qty = self.stock.issue_stock(self.bottle, self.showroom, 15, "Sale")
        self.assertEqual(qty, 5)
        self.assertEqual(self.stock.history(self.bottle)[0]["over_issue"], 0)

    def test_over_issue_warns_and_writes_nothing(self):
        before = len(self.stock.history(self.bottle))
        with self.assertRaises(OverIssueWarning) as ctx:
            self.stock.issue_stock(self.bottle, self.showroom, 50, "Sale")
        self.assertEqual(ctx.exception.available, 20)
        self.assertEqual(ctx.exception.requested, 50)
        self.assertEqual(self.stock.get_quantity(self.bottle, self.showroom), 20)
        self.assertEqual(len(self.stock.history(self.bottle)), before)

    def test_confirmed_over_issue_goes_negative_and_is_flagged(self):
        qty = self.stock.issue_stock(self.bottle, self.showroom, 50, "Sale", confirm=True)
        self.assertEqual(qty, -30)
        latest = self.stock.history(self.bottle)[0]
        self.assertEqual(latest["movement_type"], "OUT")
        self.assertEqual(latest["quantity_change"], -50)
        self.assertEqual(latest["over_issue"], 1)

    def test_issue_exactly_to_zero_is_not_over_issue(self):
        qty = self.stock.issue_stock(self.bottle, self.showroom, 20, "Sale")
        self.assertEqual(qty, 0)
        self.assertEqual(self.stock.history(self.bottle)[0]["over_issue"], 0)


class AdjustmentTests(StockTestCase):
    def test_correction_clears_negative_level(self):
        self.stock.issue_stock(self.bottle, self.showroom, 30, "Sale", confirm=True)
        self.assertEqual(self.stock.get_quantity(self.bottle, self.showroom), -30)
        qty = self.stock.adjust_stock(self.bottle, self.showroom, 30, "Stock count")
        self.assertEqual(qty, 0)
        latest = self.stock.history(self.bottle)[0]
        self.assertEqual(latest["movement_type"], "ADJUST")
        self.assertEqual(latest["over_issue"], 0)

    def test_adjustment_rejects_zero(self):
        with self.assertRaises(DomainError):
            self.stock.adjust_stock(self.bottle, self.showroom, 0, "Count")


class AccuracyTests(StockTestCase):
    """Data accuracy: level must always equal the sum of movements."""

    def test_level_equals_sum_of_movements_through_mixed_activity(self):
        self.stock.receive_stock(self.bottle, self.warehouse, 300, "Delivery")
        self.stock.issue_stock(self.bottle, self.warehouse, 80, "Transfer")
        self.stock.receive_stock(self.bottle, self.showroom, 80, "Transfer in")
        self.stock.issue_stock(self.bottle, self.showroom, 95, "Sale", confirm=True)
        self.stock.adjust_stock(self.bottle, self.showroom, 15, "Count")
        self.stock.adjust_stock(self.bottle, self.warehouse, -4, "Breakage")

        for loc in (self.warehouse, self.showroom):
            level, total = self.stock.check_consistency(self.bottle, loc)
            self.assertEqual(level, total, f"mismatch at location {loc}")

        self.assertEqual(self.stock.get_quantity(self.bottle, self.warehouse), 216)
        self.assertEqual(self.stock.get_quantity(self.bottle, self.showroom), 0)

    def test_failed_warning_leaves_books_unchanged(self):
        self.stock.receive_stock(self.bottle, self.showroom, 10, "Delivery")
        with self.assertRaises(OverIssueWarning):
            self.stock.issue_stock(self.bottle, self.showroom, 99, "Sale")
        level, total = self.stock.check_consistency(self.bottle, self.showroom)
        self.assertEqual(level, total)
        self.assertEqual(level, 10)


if __name__ == "__main__":
    unittest.main()
