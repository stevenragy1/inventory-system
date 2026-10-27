"""Load demo data for the cups and bottles company.

Uses the service layer, so the movement history matches the stock levels.
Run from the backend folder:  python seed.py
Re-running resets the database file first.
"""

import os

from app import create_app
from app.errors import OverIssueWarning
from app.services.catalog_service import CatalogService
from app.services.stock_service import StockService

DB_PATH = os.environ.get(
    "INVENTORY_DB",
    os.path.join(os.path.dirname(__file__), "..", "data", "inventory.db"),
)


def seed(db_path=DB_PATH):
    if os.path.exists(db_path):
        os.remove(db_path)
    app = create_app(db_path)
    conn = app.config["DB"]
    catalog = CatalogService(conn)
    stock = StockService(conn)

    cups = catalog.create_category("Cups")["id"]
    bottles = catalog.create_category("Bottles")["id"]
    warehouse = catalog.create_location("Main Warehouse")["id"]
    showroom = catalog.create_location("Showroom")["id"]

    items = {
        "CUP-CER-001": catalog.create_item("CUP-CER-001", "White ceramic cup 250ml", cups, 250, 100)["id"],
        "CUP-PAP-002": catalog.create_item("CUP-PAP-002", "Paper coffee cup 8oz (pack of 50)", cups, 400, 40)["id"],
        "CUP-TRV-003": catalog.create_item("CUP-TRV-003", "Travel mug 400ml", cups, 675, 30)["id"],
        "BTL-STL-001": catalog.create_item("BTL-STL-001", "Steel water bottle 750ml", bottles, 820, 50)["id"],
        "BTL-GLS-002": catalog.create_item("BTL-GLS-002", "Glass bottle 500ml", bottles, 390, 60)["id"],
        "BTL-WTR-003": catalog.create_item("BTL-WTR-003", "Plastic water bottle 1L", bottles, 110, 200)["id"],
    }

    # Opening deliveries to the warehouse.
    stock.receive_stock(items["CUP-CER-001"], warehouse, 400, "Supplier delivery #101")
    stock.receive_stock(items["CUP-PAP-002"], warehouse, 80, "Supplier delivery #102")
    stock.receive_stock(items["CUP-TRV-003"], warehouse, 25, "Supplier delivery #103")
    stock.receive_stock(items["BTL-GLS-002"], warehouse, 150, "Supplier delivery #104")
    stock.receive_stock(items["BTL-WTR-003"], warehouse, 500, "Supplier delivery #105")
    stock.receive_stock(items["BTL-STL-001"], showroom, 15, "Initial shop stock")
    stock.receive_stock(items["CUP-CER-001"], showroom, 60, "Initial shop stock")
    stock.receive_stock(items["CUP-TRV-003"], showroom, 10, "Initial shop stock")
    stock.receive_stock(items["BTL-GLS-002"], showroom, 20, "Initial shop stock")

    # Move glass bottles from the warehouse to the shop floor.
    stock.issue_stock(items["BTL-GLS-002"], warehouse, 30, "Transfer to showroom")
    stock.receive_stock(items["BTL-GLS-002"], showroom, 30, "Transfer from warehouse")

    # Over-issue: the showroom holds 50 glass bottles; a sale of 80 shows the
    # warning first, then is confirmed, leaving the showroom at -30.
    try:
        stock.issue_stock(items["BTL-GLS-002"], showroom, 80, "Customer sale #2281")
    except OverIssueWarning:
        stock.issue_stock(items["BTL-GLS-002"], showroom, 80, "Customer sale #2281", confirm=True)

    print("Seed complete:", db_path)
    print("Items:", len(items), "| Locations: 2 | Categories: 2")


if __name__ == "__main__":
    seed()
