"""SQL for reports. Read-only: nothing here writes data."""


class ReportRepo:
    def __init__(self, conn):
        self.conn = conn

    def active_item_location_grid(self, location_id=None):
        """One row per active item and location, with its current quantity.

        Locations with no stock row count as zero.
        """
        sql = """
            SELECT i.id AS item_id, i.sku, i.name, i.category_id,
                   c.name AS category,
                   i.unit_cost_cents, i.reorder_level,
                   l.id AS location_id, l.name AS location,
                   COALESCE(s.quantity, 0) AS quantity
            FROM item i
            JOIN category c ON c.id = i.category_id
            CROSS JOIN location l
            LEFT JOIN stock_level s
                   ON s.item_id = i.id AND s.location_id = l.id
            WHERE i.is_active = 1
        """
        params = []
        if location_id is not None:
            sql += " AND l.id = ?"
            params.append(location_id)
        sql += " ORDER BY i.sku, l.name"
        return [dict(r) for r in self.conn.execute(sql, params)]

    def movement_totals(self, lower=None, upper=None, location_id=None,
                        movement_type=None, negate=False):
        """Sum quantity_change per item for movements with lower <= created_at < upper.

        Bounds are ISO timestamp strings in the same format the services write.
        negate=True returns positive numbers for OUT (units sold).
        """
        expr = "-SUM(quantity_change)" if negate else "SUM(quantity_change)"
        sql = f"SELECT item_id, {expr} AS total FROM stock_movement WHERE 1 = 1"
        params = []
        if lower is not None:
            sql += " AND created_at >= ?"
            params.append(lower)
        if upper is not None:
            sql += " AND created_at < ?"
            params.append(upper)
        if location_id is not None:
            sql += " AND location_id = ?"
            params.append(location_id)
        if movement_type is not None:
            sql += " AND movement_type = ?"
            params.append(movement_type)
        sql += " GROUP BY item_id"
        return {r["item_id"]: r["total"] or 0 for r in self.conn.execute(sql, params)}

    def movements(self, item_id=None, lower=None, upper=None, location_id=None, limit=500):
        sql = """SELECT m.id, m.item_id, i.sku, i.name AS item_name,
                        m.location_id, l.name AS location, m.movement_type,
                        m.quantity_change, m.reason, m.over_issue, m.created_at
                 FROM stock_movement m
                 JOIN item i ON i.id = m.item_id
                 JOIN location l ON l.id = m.location_id
                 WHERE 1 = 1"""
        params = []
        if item_id is not None:
            sql += " AND m.item_id = ?"
            params.append(item_id)
        if lower is not None:
            sql += " AND m.created_at >= ?"
            params.append(lower)
        if upper is not None:
            sql += " AND m.created_at < ?"
            params.append(upper)
        if location_id is not None:
            sql += " AND m.location_id = ?"
            params.append(location_id)
        sql += " ORDER BY m.id DESC LIMIT ?"
        params.append(limit)
        return [dict(r) for r in self.conn.execute(sql, params)]
