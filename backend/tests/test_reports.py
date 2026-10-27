"""Step 3 tests: reports, turnover formulas, and dashboard totals.

Run from the backend folder:  python -m unittest discover -s tests -v
"""

import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db import connect, init_db  # noqa: E402
from app.errors import DomainError, OverIssueWarning  # noqa: E402
from app.reports.turnover import calculate  # noqa: E402
from app.services.catalog_service import CatalogService  # noqa: E402
from app.services.report_service import ReportService  # noqa: E402
from app.services.stock_service import StockService  # noqa: E402


class TurnoverFormulaTests(unittest.TestCase):
    """The pure formulas, checked against worked numbers."""

    def test_glass_bottle_example_from_plan(self):
        # 60 sold in 30 days, average stock 120: turnover 0.5, 60 days on hand.
        result = calculate(units_sold=60, opening=120, closing=120, period_days=30)
        self.assertEqual(result["average_stock"], 120)
        self.assertEqual(result["turnover"], 0.5)
        self.assertEqual(result["days_of_stock"], 60.0)

    def test_zero_average_stock_gives_none_not_an_error(self):
        result = calculate(units_sold=5, opening=0, closing=0, period_days=30)
        self.assertIsNone(result["turnover"])
        self.assertIsNone(result["days_of_stock"])

    def test_nothing_sold_gives_none_for_days(self):
        result = calculate(units_sold=0, opening=50, closing=50, period_days=30)
        self.assertEqual(result["turnover"], 0)
        self.assertIsNone(result["days_of_stock"])

    def test_average_uses_opening_and_closing(self):
        result = calculate(units_sold=10, opening=100, closing=50, period_days=10)
        self.assertEqual(result["average_stock"], 75)
        self.assertEqual(result["turnover"], 0.13)


class ReportTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.conn = connect(self.tmp.name)
        init_db(self.conn)
        self.catalog = CatalogService(self.conn)
        self.stock = StockService(self.conn)
        self.reports = ReportService(self.conn)

        cat = self.catalog.create_category("Bottles")["id"]
        self.warehouse = self.catalog.create_location("Main Warehouse")["id"]
        self.showroom = self.catalog.create_location("Showroom")["id"]
        self.glass = self.catalog.create_item(
            "BTL-GLS-002", "Glass bottle 500ml", cat, 390, 60)["id"]
        self.travel = self.catalog.create_item(
            "CUP-TRV-003", "Travel mug 400ml", cat, 675, 30)["id"]

        # Movements are stored in UTC, so the tests use the UTC date too.
        self.today = datetime.now(timezone.utc).date()

    def tearDown(self):
        self.conn.close()
        os.unlink(self.tmp.name)

    def day(self, offset):
        return (self.today + timedelta(days=offset)).isoformat()


class ValuationAndStockReportTests(ReportTestCase):
    def test_valuation_is_quantity_times_cost(self):
        self.stock.receive_stock(self.glass, self.warehouse, 10, "Delivery")
        report = self.reports.valuation()
        row = next(r for r in report["rows"] if r["sku"] == "BTL-GLS-002"
                   and r["location"] == "Main Warehouse")
        self.assertEqual(row["value_cents"], 3900)
        self.assertEqual(report["total_value_cents"], 3900)

    def test_low_stock_is_above_zero_and_at_or_below_reorder(self):
        self.stock.receive_stock(self.travel, self.warehouse, 25, "Delivery")  # reorder 30
        self.stock.receive_stock(self.glass, self.warehouse, 120, "Delivery")  # reorder 60
        low = self.reports.low_stock()
        skus = {(r["sku"], r["location"]) for r in low}
        self.assertIn(("CUP-TRV-003", "Main Warehouse"), skus)
        self.assertNotIn(("BTL-GLS-002", "Main Warehouse"), skus)

    def test_zero_stock_is_not_low(self):
        # Out of stock is shown in the dashboard "out" count, not as low.
        self.stock.receive_stock(self.travel, self.warehouse, 5, "Delivery")
        self.stock.issue_stock(self.travel, self.warehouse, 5, "Sale")
        self.assertEqual(self.reports.low_stock(), [])

    def test_negative_stock_lists_over_issued_level(self):
        self.stock.receive_stock(self.glass, self.showroom, 20, "Delivery")
        self.stock.issue_stock(self.glass, self.showroom, 50, "Sale", confirm=True)
        negative = self.reports.negative_stock()
        self.assertEqual(len(negative), 1)
        self.assertEqual(negative[0]["quantity"], -30)

    def test_negative_stock_clears_after_correction(self):
        self.stock.receive_stock(self.glass, self.showroom, 20, "Delivery")
        self.stock.issue_stock(self.glass, self.showroom, 50, "Sale", confirm=True)
        self.stock.adjust_stock(self.glass, self.showroom, 30, "Stock count")
        self.assertEqual(self.reports.negative_stock(), [])


class MovementHistoryTests(ReportTestCase):
    def test_date_filter_includes_todays_movements(self):
        self.stock.receive_stock(self.glass, self.warehouse, 5, "Delivery")
        today_only = self.reports.movement_history(
            item_id=self.glass, start=self.day(0), end=self.day(0))
        self.assertEqual(len(today_only), 1)

    def test_date_filter_excludes_other_periods(self):
        self.stock.receive_stock(self.glass, self.warehouse, 5, "Delivery")
        past = self.reports.movement_history(start="2000-01-01", end="2000-01-31")
        self.assertEqual(past, [])

    def test_end_before_start_is_rejected(self):
        with self.assertRaises(DomainError):
            self.reports.movement_history(start=self.day(0), end=self.day(-1))

    def test_bad_date_format_is_rejected(self):
        with self.assertRaises(DomainError):
            self.reports.movement_history(start="24/10/2026", end=self.day(0))


class TurnoverReportTests(ReportTestCase):
    def test_sales_today_give_expected_turnover(self):
        # Received 120 today, sold 60 today. Opening 0, closing 60, average 30.
        # Turnover = 60 / 30 = 2.0; days on hand = 1 / 2.0 = 0.5.
        self.stock.receive_stock(self.glass, self.warehouse, 120, "Delivery")
        self.stock.issue_stock(self.glass, self.warehouse, 60, "Sale")
        report = self.reports.turnover(self.day(0), self.day(0))
        row = next(r for r in report["rows"] if r["sku"] == "BTL-GLS-002")
        self.assertEqual(row["units_sold"], 60)
        self.assertEqual(row["turnover"], 2.0)
        self.assertEqual(row["days_of_stock"], 0.5)

    def test_adjustments_are_not_counted_as_sales(self):
        self.stock.receive_stock(self.glass, self.warehouse, 10, "Delivery")
        self.stock.adjust_stock(self.glass, self.warehouse, -4, "Breakage")
        report = self.reports.turnover(self.day(0), self.day(0))
        row = next(r for r in report["rows"] if r["sku"] == "BTL-GLS-002")
        self.assertEqual(row["units_sold"], 0)

    def test_opening_stock_carries_into_a_later_period(self):
        # Stock received before the period is the opening balance, not a sale.
        self.stock.receive_stock(self.glass, self.warehouse, 40, "Delivery")
        report = self.reports.turnover(self.day(1), self.day(2))
        row = next(r for r in report["rows"] if r["sku"] == "BTL-GLS-002")
        self.assertEqual(row["opening_stock"], 40)
        self.assertEqual(row["closing_stock"], 40)
        self.assertEqual(row["units_sold"], 0)
        self.assertIsNone(row["days_of_stock"])

    def test_zero_stock_item_reports_none_not_error(self):
        report = self.reports.turnover(self.day(0), self.day(0))
        row = next(r for r in report["rows"] if r["sku"] == "BTL-GLS-002")
        self.assertIsNone(row["turnover"])
        self.assertIsNone(row["days_of_stock"])

    def test_end_before_start_is_rejected(self):
        with self.assertRaises(DomainError):
            self.reports.turnover(self.day(0), self.day(-1))


class DashboardTests(ReportTestCase):
    def test_totals_count_low_out_and_negative(self):
        self.stock.receive_stock(self.travel, self.warehouse, 25, "Delivery")  # low
        self.stock.receive_stock(self.glass, self.showroom, 20, "Delivery")
        self.stock.issue_stock(self.glass, self.showroom, 50, "Sale", confirm=True)  # negative
        dash = self.reports.dashboard(as_of=self.today)
        totals = dash["totals"]
        self.assertEqual(totals["active_items"], 2)
        self.assertEqual(totals["low_stock_count"], 1)
        self.assertEqual(totals["negative_count"], 1)
        self.assertEqual(len(dash["alerts_negative"]), 1)

    def test_chart_has_one_series_per_location(self):
        self.stock.receive_stock(self.glass, self.warehouse, 120, "Delivery")
        chart = self.reports.dashboard(as_of=self.today)["chart_stock_by_location"]
        self.assertEqual({s["location"] for s in chart["series"]},
                         {"Main Warehouse", "Showroom"})
        for series in chart["series"]:
            self.assertEqual(len(series["data"]), len(chart["labels"]))

    def test_slow_movers_put_items_with_no_sales_first(self):
        self.stock.receive_stock(self.glass, self.warehouse, 120, "Delivery")
        self.stock.issue_stock(self.glass, self.warehouse, 60, "Sale")
        slow = self.reports.dashboard(as_of=self.today)["chart_slow_movers"]
        # The travel mug has no sales (days None -> treated as slowest), so it comes first.
        self.assertEqual(slow[0]["sku"], "CUP-TRV-003")

    def test_invalid_date_is_rejected(self):
        with self.assertRaises(DomainError):
            self.reports.turnover("2026-13-01", self.day(0))


class OverIssueStillWarnsTests(ReportTestCase):
    def test_reports_do_not_change_stock(self):
        self.stock.receive_stock(self.glass, self.warehouse, 10, "Delivery")
        before = self.stock.get_quantity(self.glass, self.warehouse)
        self.reports.dashboard(as_of=self.today)
        self.reports.turnover(self.day(0), self.day(0))
        self.assertEqual(self.stock.get_quantity(self.glass, self.warehouse), before)
        with self.assertRaises(OverIssueWarning):
            self.stock.issue_stock(self.glass, self.warehouse, 99, "Sale")


if __name__ == "__main__":
    unittest.main()
