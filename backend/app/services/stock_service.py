"""Stock business rules: receive, issue (with over-issue warning), adjust.

Every change writes the stock level and a movement row in one transaction,
so the two cannot drift apart.
"""

from datetime import datetime, timezone

from app.db import transaction
from app.errors import DomainError, NotFoundError, OverIssueWarning
from app.repositories.catalog_repo import CatalogRepo
from app.repositories.stock_repo import StockRepo


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class StockService:
    def __init__(self, conn):
        self.conn = conn
        self.catalog = CatalogRepo(conn)
        self.stock = StockRepo(conn)

    # ---- validation helpers -------------------------------------------------

    def _require_active_item(self, item_id):
        item = self.catalog.find_item(item_id)
        if item is None:
            raise NotFoundError(f"Item {item_id} not found.")
        if not item["is_active"]:
            raise DomainError(f"Item {item['sku']} is inactive.")
        return item

    def _require_location(self, location_id):
        if self.catalog.find_location(location_id) is None:
            raise NotFoundError(f"Location {location_id} not found.")

    @staticmethod
    def _require_positive_qty(qty):
        if not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
            raise DomainError("Quantity must be a positive whole number.")

    @staticmethod
    def _require_reason(reason):
        if not reason or not str(reason).strip():
            raise DomainError("A reason is required.")
        return str(reason).strip()

    # ---- public operations --------------------------------------------------

    def get_quantity(self, item_id, location_id):
        return self.stock.get_quantity(item_id, location_id)

    def receive_stock(self, item_id, location_id, qty, reason):
        """Stock-in (IN). Always allowed."""
        self._require_active_item(item_id)
        self._require_location(location_id)
        self._require_positive_qty(qty)
        reason = self._require_reason(reason)

        with transaction(self.conn):
            self.stock.add_to_level(item_id, location_id, qty)
            self.stock.insert_movement(
                item_id, location_id, "IN", qty, reason,
                over_issue=False, created_at=_now())
        return self.get_quantity(item_id, location_id)

    def issue_stock(self, item_id, location_id, qty, reason, confirm=False):
        """Stock-out (OUT).

        If the result would be negative and confirm is False, raise
        OverIssueWarning and write nothing. If confirm is True, record the
        movement with over_issue=True; the level may go negative.
        """
        self._require_active_item(item_id)
        self._require_location(location_id)
        self._require_positive_qty(qty)
        reason = self._require_reason(reason)

        available = self.get_quantity(item_id, location_id)
        over = (available - qty) < 0
        if over and not confirm:
            raise OverIssueWarning(available=max(available, 0), requested=qty)

        with transaction(self.conn):
            self.stock.add_to_level(item_id, location_id, -qty)
            self.stock.insert_movement(
                item_id, location_id, "OUT", -qty, reason,
                over_issue=over, created_at=_now())
        return self.get_quantity(item_id, location_id)

    def adjust_stock(self, item_id, location_id, delta, reason):
        """Adjustment (ADJUST). Positive or negative; used for stock counts
        and for correcting negative levels."""
        self._require_active_item(item_id)
        self._require_location(location_id)
        if not isinstance(delta, int) or isinstance(delta, bool) or delta == 0:
            raise DomainError("Adjustment must be a non-zero whole number.")
        reason = self._require_reason(reason)

        with transaction(self.conn):
            self.stock.add_to_level(item_id, location_id, delta)
            self.stock.insert_movement(
                item_id, location_id, "ADJUST", delta, reason,
                over_issue=False, created_at=_now())
        return self.get_quantity(item_id, location_id)

    def check_consistency(self, item_id, location_id):
        """Return (level, movement_sum). Equal when the books agree."""
        level = self.get_quantity(item_id, location_id)
        total = self.stock.sum_movements(item_id, location_id)
        return level, total

    def history(self, item_id=None, limit=200):
        return self.stock.list_movements(item_id=item_id, limit=limit)

    def levels_for_item(self, item_id):
        return self.stock.levels_for_item(item_id)
