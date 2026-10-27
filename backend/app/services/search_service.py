"""Search and filter rules for items.

Status uses the same rule as the reports:
- negative: quantity below zero
- out: quantity is zero
- low: above zero and at or below the reorder level
- in_stock: above the reorder level

When a location is chosen, status is judged on that location's quantity.
Otherwise it is judged on the total across all locations, except that any
negative level makes the item negative.
"""

from app.errors import DomainError
from app.repositories.report_repo import ReportRepo

STATUSES = ("in_stock", "low", "out", "negative")


def status_for(quantity, reorder_level):
    if quantity < 0:
        return "negative"
    if quantity == 0:
        return "out"
    if quantity <= reorder_level:
        return "low"
    return "in_stock"


class SearchService:
    def __init__(self, conn):
        self.repo = ReportRepo(conn)

    def search(self, q=None, category_id=None, location_id=None, status=None):
        if status is not None and status != "" and status not in STATUSES:
            raise DomainError(
                f"Status must be one of: {', '.join(STATUSES)}.")
        text = (q or "").strip().lower()

        # Group the item-location grid into one entry per item.
        items = {}
        for r in self.repo.active_item_location_grid():
            entry = items.setdefault(r["item_id"], {
                "item_id": r["item_id"],
                "sku": r["sku"],
                "name": r["name"],
                "category_id": r["category_id"],
                "category": r["category"],
                "unit_cost_cents": r["unit_cost_cents"],
                "reorder_level": r["reorder_level"],
                "levels": [],
                "total": 0,
            })
            entry["levels"].append({
                "location_id": r["location_id"],
                "location": r["location"],
                "quantity": r["quantity"],
            })
            entry["total"] += r["quantity"]

        results = []
        for entry in items.values():
            if text and text not in entry["sku"].lower() and text not in entry["name"].lower():
                continue
            if category_id is not None and entry["category_id"] != category_id:
                continue

            if location_id is not None:
                level = next((l for l in entry["levels"] if l["location_id"] == location_id), None)
                scope_qty = level["quantity"] if level else 0
                item_status = status_for(scope_qty, entry["reorder_level"])
            else:
                scope_qty = entry["total"]
                # Any negative level makes the item negative, so "negative" finds
                # every level that needs a correction, as the dashboard alert does.
                if any(l["quantity"] < 0 for l in entry["levels"]):
                    item_status = "negative"
                else:
                    item_status = status_for(scope_qty, entry["reorder_level"])
            if status and item_status != status:
                continue

            results.append({
                **{k: v for k, v in entry.items() if k != "levels"},
                "levels": sorted(entry["levels"], key=lambda l: l["location"]),
                "scope_quantity": scope_qty,
                "status": item_status,
            })

        results.sort(key=lambda r: r["sku"])
        return results
