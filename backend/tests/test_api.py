"""Step 2 API tests: item create, deactivate, and the stock warning over HTTP.

Run from the backend folder:  python -m unittest discover -s tests -v
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app  # noqa: E402


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.app = create_app(self.tmp.name)
        self.client = self.app.test_client()
        self.cat = self.client.post("/api/categories", json={"name": "Cups"}).get_json()
        self.loc = self.client.post("/api/locations", json={"name": "Showroom"}).get_json()

    def tearDown(self):
        self.app.config["DB"].close()
        os.unlink(self.tmp.name)

    def new_item(self, sku="CUP-CER-004", **overrides):
        body = {
            "sku": sku,
            "name": "Espresso cup 90ml",
            "category_id": self.cat["id"],
            "unit_cost_cents": 250,
            "reorder_level": 100,
        }
        body.update(overrides)
        return self.client.post("/api/items", json=body)


class ItemApiTests(ApiTestCase):
    def test_create_item_returns_201_with_cents(self):
        r = self.new_item()
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.get_json()["unit_cost_cents"], 250)
        self.assertEqual(r.get_json()["sku"], "CUP-CER-004")

    def test_duplicate_sku_returns_409(self):
        self.new_item()
        r = self.new_item(sku="cup-cer-004")
        self.assertEqual(r.status_code, 409)
        self.assertIn("already exists", r.get_json()["message"])

    def test_negative_cost_returns_400(self):
        r = self.new_item(unit_cost_cents=-1)
        self.assertEqual(r.status_code, 400)

    def test_unknown_category_returns_404(self):
        r = self.new_item(category_id=999)
        self.assertEqual(r.status_code, 404)

    def test_deactivate_hides_item_from_list_and_keeps_it(self):
        item = self.new_item().get_json()
        r = self.client.post(f"/api/items/{item['id']}/deactivate")
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.get_json()["is_active"])
        listed = self.client.get("/api/items").get_json()
        self.assertEqual(listed, [])
        # The item still exists and can be fetched by id.
        self.assertEqual(self.client.get(f"/api/items/{item['id']}").status_code, 200)

    def test_inactive_item_rejects_stock(self):
        item = self.new_item().get_json()
        self.client.post(f"/api/items/{item['id']}/deactivate")
        r = self.client.post("/api/stock/receive", json={
            "item_id": item["id"], "location_id": self.loc["id"],
            "quantity": 5, "reason": "Delivery"})
        self.assertEqual(r.status_code, 400)


class StockApiTests(ApiTestCase):
    def test_over_issue_warning_then_confirm_over_http(self):
        item = self.new_item().get_json()
        base = {"item_id": item["id"], "location_id": self.loc["id"]}
        self.client.post("/api/stock/receive", json={**base, "quantity": 20, "reason": "Delivery"})

        warn = self.client.post("/api/stock/issue", json={**base, "quantity": 50, "reason": "Sale"})
        self.assertEqual(warn.status_code, 409)
        self.assertTrue(warn.get_json()["warning"])
        self.assertEqual(warn.get_json()["available"], 20)

        ok = self.client.post("/api/stock/issue", json={
            **base, "quantity": 50, "reason": "Sale", "confirm": True})
        self.assertEqual(ok.status_code, 201)
        self.assertEqual(ok.get_json()["quantity"], -30)

    def test_zero_quantity_returns_400(self):
        item = self.new_item().get_json()
        r = self.client.post("/api/stock/receive", json={
            "item_id": item["id"], "location_id": self.loc["id"],
            "quantity": 0, "reason": "x"})
        self.assertEqual(r.status_code, 400)


if __name__ == "__main__":
    unittest.main()
