"""Report rules: valuation, low stock, negative stock, movements, turnover, dashboard.

Reports only read data. Every number comes from the stock_level and
stock_movement tables, so each figure can be traced back to its movements.
"""

from datetime import date, datetime, timedelta, timezone

from app.errors import DomainError
from app.reports.turnover import calculate
from app.repositories.report_repo import ReportRepo


def parse_date(value, label):
    if not value:
        raise DomainError(f"{label} is required (YYYY-MM-DD).")
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise DomainError(f"{label} must be a date in YYYY-MM-DD format.")


def _bound(day):
    """Start of a day as an ISO timestamp, matching the format the services write."""
    return f"{day.isoformat()}T00:00:00+00:00"


class ReportService:
    def __init__(self, conn):
        self.repo = ReportRepo(conn)

    # Valuation -------------------------------------------------------------

    def valuation(self, location_id=None):
        """Value of each item at each location: quantity x unit cost.

        Negative quantities reduce the total, so the total matches the books.
        """
        rows = []
        total = 0
        for r in self.repo.active_item_location_grid(location_id):
            value = r["quantity"] * r["unit_cost_cents"]
            total += value
            rows.append({
                "item_id": r["item_id"],
                "sku": r["sku"],
                "name": r["name"],
                "category": r["category"],
                "location": r["location"],
                "quantity": r["quantity"],
                "unit_cost_cents": r["unit_cost_cents"],
                "value_cents": value,
            })
        return {"rows": rows, "total_value_cents": total}

    # Low and negative stock -------------------------------------------------

    def low_stock(self):
        """Item-location pairs with stock above zero but at or below reorder level.

        Zero stock is reported separately as "out", and negative stock as "negative".
        """
        return [
            r for r in self.repo.active_item_location_grid()
            if 0 < r["quantity"] <= r["reorder_level"]
        ]

    def negative_stock(self):
        return [r for r in self.repo.active_item_location_grid() if r["quantity"] < 0]

    # Movement history -------------------------------------------------------

    def movement_history(self, item_id=None, start=None, end=None, location_id=None):
        lower = upper = None
        if start or end:
            start_day = parse_date(start, "Start date") if start else None
            end_day = parse_date(end, "End date") if end else None
            if start_day and end_day and end_day < start_day:
                raise DomainError("End date must be on or after the start date.")
            if start_day:
                lower = _bound(start_day)
            if end_day:
                upper = _bound(end_day + timedelta(days=1))
        return self.repo.movements(item_id=item_id, lower=lower, upper=upper,
                                   location_id=location_id)

    # Turnover ----------------------------------------------------------------

    def turnover(self, start, end, location_id=None):
        """Turnover for every active item over the period [start, end], inclusive."""
        start_day = parse_date(start, "Start date")
        end_day = parse_date(end, "End date")
        if end_day < start_day:
            raise DomainError("End date must be on or after the start date.")

        period_days = (end_day - start_day).days + 1
        period_start = _bound(start_day)
        period_end = _bound(end_day + timedelta(days=1))

        opening = self.repo.movement_totals(upper=period_start, location_id=location_id)
        closing = self.repo.movement_totals(upper=period_end, location_id=location_id)
        sold = self.repo.movement_totals(lower=period_start, upper=period_end,
                                         location_id=location_id,
                                         movement_type="OUT", negate=True)

        # One entry per item, even when it is stocked in several locations.
        items = {}
        for r in self.repo.active_item_location_grid(location_id):
            items.setdefault(r["item_id"], {"item_id": r["item_id"],
                                            "sku": r["sku"], "name": r["name"]})

        result = []
        for item_id, entry in items.items():
            figures = calculate(
                units_sold=sold.get(item_id, 0),
                opening=opening.get(item_id, 0),
                closing=closing.get(item_id, 0),
                period_days=period_days,
            )
            result.append({**entry, **figures})
        result.sort(key=lambda row: row["sku"])
        return {
            "start": start_day.isoformat(),
            "end": end_day.isoformat(),
            "period_days": period_days,
            "location_id": location_id,
            "rows": result,
        }

    # Dashboard ---------------------------------------------------------------

    def dashboard(self, as_of=None, days=30):
        """Totals, chart data, and alerts. The turnover window ends on as_of."""
        # Movements are stored in UTC, so "today" is the UTC date too.
        as_of = as_of or datetime.now(timezone.utc).date()
        grid = self.repo.active_item_location_grid()

        items_by_id = {}
        for r in grid:
            items_by_id.setdefault(r["item_id"], r["name"])

        locations = []
        for r in grid:
            if r["location"] not in locations:
                locations.append(r["location"])

        # Chart: quantity per item, one series per location.
        item_ids = list(items_by_id)
        quantity = {(r["item_id"], r["location"]): r["quantity"] for r in grid}
        chart = {
            "labels": [items_by_id[i] for i in item_ids],
            "series": [
                {
                    "location": loc,
                    "data": [quantity.get((i, loc), 0) for i in item_ids],
                }
                for loc in locations
            ],
        }

        low = self.low_stock()
        negative = self.negative_stock()
        out = [r for r in grid if r["quantity"] == 0]
        total_value = sum(r["quantity"] * r["unit_cost_cents"] for r in grid)

        # Slow movers: the items with the most days of stock on hand.
        # Items with no sales have no ratio (None) and count as slowest.
        window = self.turnover(
            (as_of - timedelta(days=days - 1)).isoformat(), as_of.isoformat())
        def slowness(row):
            return float("inf") if row["days_of_stock"] is None else row["days_of_stock"]
        slow = sorted(window["rows"], key=slowness, reverse=True)[:10]

        return {
            "as_of": as_of.isoformat(),
            "window_days": days,
            "totals": {
                "active_items": len(items_by_id),
                "total_units": sum(r["quantity"] for r in grid),
                "total_value_cents": total_value,
                "low_stock_count": len(low),
                "out_count": len(out),
                "negative_count": len(negative),
            },
            "chart_stock_by_location": chart,
            "chart_slow_movers": [
                {"sku": r["sku"], "name": r["name"], "days_of_stock": r["days_of_stock"],
                 "units_sold": r["units_sold"]}
                for r in slow
            ],
            "alerts_negative": negative,
            "low_stock": low,
        }
