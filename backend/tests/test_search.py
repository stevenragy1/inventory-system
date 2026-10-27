"""Step 4 tests: search and filter rules.

Run from the backend folder:  python -m unittest discover -s tests -v
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db import connect, init_db  # noqa: E402
from app.errors import DomainError  # noqa: E402
from app.services.catalog_service import CatalogService  # noqa: E402
from app.services.search_service import SearchService, status_for  # noqa: E402
from app.services.stock_service import StockService  # noqa: E402


class SearchTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.conn = connect(self.tmp.name)
        init_db(self.conn)
        catalog = CatalogService(self.conn)
        self.stock = StockService(self.conn)
        self.search = SearchService(self.conn)

        cups = catalog.create_category("Cups")["id"]
        bottles = catalog.create_category("Bottles")["id"]
        self.warehouse = catalog.create_location("Main Warehouse")["id"]
        self.showroom = catalog.create_location("Showroom")["id"]

        self.ceramic = catalog.create_item("CUP-CER-001", "White ceramic cup 250ml", cups, 250, 100)["id"]
        self.travel = catalog.create_item("CUP-TRV-003", "Travel mug 400ml", cups, 675, 30)["id"]
        self.glass = catalog.create_item("BTL-GLS-002", "Glass bottle 500ml", bottles, 390, 60)["id"]
        self.steel = catalog.create_item("BTL-STL-001", "Steel water bottle 750ml", bottles, 820, 50)["id"]

        # Ceramic: healthy at warehouse. Travel: low at warehouse.
        # Glass: negative at showroom. Steel: out (never stocked).
        self.stock.receive_stock(self.ceramic, self.warehouse, 400, "Delivery")
        self.stock.receive_stock(self.travel, self.warehouse, 25, "Delivery")
        self.stock.receive_stock(self.glass, self.warehouse, 120, "Delivery")
        self.stock.receive_stock(self.glass, self.showroom, 20, "Delivery")
        self.stock.issue_stock(self.glass, self.showroom, 50, "Sale", confirm=True)

        self.catalog = catalog
        self.cups = cups
        self.bottles = bottles

    def tearDown(self):
        self.conn.close()
        os.unlink(self.tmp.name)

    def skus(self, results):
        return [r["sku"] for r in results]


class StatusRuleTests(unittest.TestCase):
    def test_status_rule(self):
        self.assertEqual(status_for(-1, 10), "negative")
        self.assertEqual(status_for(0, 10), "out")
        self.assertEqual(status_for(10, 10), "low")
        self.assertEqual(status_for(5, 10), "low")
        self.assertEqual(status_for(11, 10), "in_stock")


class SearchTests(SearchTestCase):
    def test_no_filters_returns_all_active_items(self):
        self.assertEqual(len(self.search.search()), 4)

    def test_text_matches_sku_or_name_case_insensitively(self):
        self.assertEqual(self.skus(self.search.search(q="gls")), ["BTL-GLS-002"])
        self.assertEqual(self.skus(self.search.search(q="TRAVEL")), ["CUP-TRV-003"])
        self.assertEqual(self.skus(self.search.search(q="water bottle")), ["BTL-STL-001"])

    def test_blank_text_is_ignored(self):
        self.assertEqual(len(self.search.search(q="   ")), 4)

    def test_category_filter(self):
        cups = self.search.search(category_id=self.cups)
        self.assertEqual(sorted(self.skus(cups)), ["CUP-CER-001", "CUP-TRV-003"])

    def test_status_filter_without_location_uses_total(self):
        self.assertEqual(self.skus(self.search.search(status="negative")), ["BTL-GLS-002"])
        self.assertEqual(self.skus(self.search.search(status="out")), ["BTL-STL-001"])
        self.assertEqual(self.skus(self.search.search(status="low")), ["CUP-TRV-003"])
        self.assertEqual(self.skus(self.search.search(status="in_stock")), ["CUP-CER-001"])

    def test_status_with_location_uses_that_location_only(self):
        # Glass bottles: warehouse 120 (in stock), showroom -30 (negative).
        warehouse = self.search.search(q="gls", location_id=self.warehouse)[0]
        showroom = self.search.search(q="gls", location_id=self.showroom)[0]
        self.assertEqual(warehouse["status"], "in_stock")
        self.assertEqual(showroom["status"], "negative")
        self.assertEqual(showroom["scope_quantity"], -30)

    def test_location_with_no_stock_row_counts_as_zero(self):
        # Steel bottles have no stock at the showroom, so they are out there.
        result = self.search.search(q="steel", location_id=self.showroom)[0]
        self.assertEqual(result["scope_quantity"], 0)
        self.assertEqual(result["status"], "out")

    def test_filters_combine(self):
        results = self.search.search(category_id=self.bottles, status="negative")
        self.assertEqual(self.skus(results), ["BTL-GLS-002"])

    def test_no_match_returns_empty_list(self):
        self.assertEqual(self.search.search(q="nothing-like-this"), [])

    def test_each_result_lists_levels_per_location(self):
        glass = self.search.search(q="gls")[0]
        quantities = {l["location"]: l["quantity"] for l in glass["levels"]}
        self.assertEqual(quantities, {"Main Warehouse": 120, "Showroom": -30})
        self.assertEqual(glass["total"], 90)

    def test_unknown_status_is_rejected(self):
        with self.assertRaises(DomainError):
            self.search.search(status="bogus")

    def test_deactivated_items_are_not_found(self):
        self.catalog.deactivate_item(self.travel)
        self.assertEqual(self.search.search(q="travel"), [])


if __name__ == "__main__":
    unittest.main()
