"""SQL access for stock levels and movements. No business rules here."""


class StockRepo:
    def __init__(self, conn):
        self.conn = conn

    def get_quantity(self, item_id, location_id):
        row = self.conn.execute(
            "SELECT quantity FROM stock_level WHERE item_id = ? AND location_id = ?",
            (item_id, location_id),
        ).fetchone()
        return row["quantity"] if row else 0

    def add_to_level(self, item_id, location_id, delta):
        """Add delta to the level, creating the row if needed."""
        self.conn.execute(
            """INSERT INTO stock_level (item_id, location_id, quantity)
               VALUES (?, ?, ?)
               ON CONFLICT (item_id, location_id)
               DO UPDATE SET quantity = quantity + excluded.quantity""",
            (item_id, location_id, delta),
        )

    def insert_movement(self, item_id, location_id, movement_type,
                        quantity_change, reason, over_issue, created_at):
        cur = self.conn.execute(
            """INSERT INTO stock_movement
               (item_id, location_id, movement_type, quantity_change,
                reason, over_issue, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (item_id, location_id, movement_type, quantity_change,
             reason, 1 if over_issue else 0, created_at),
        )
        return cur.lastrowid

    def sum_movements(self, item_id, location_id):
        row = self.conn.execute(
            """SELECT COALESCE(SUM(quantity_change), 0) AS total
               FROM stock_movement WHERE item_id = ? AND location_id = ?""",
            (item_id, location_id),
        ).fetchone()
        return row["total"]

    def list_movements(self, item_id=None, limit=200):
        sql = """SELECT m.id, m.item_id, i.sku, i.name AS item_name,
                        m.location_id, l.name AS location, m.movement_type,
                        m.quantity_change, m.reason, m.over_issue, m.created_at
                 FROM stock_movement m
                 JOIN item i ON i.id = m.item_id
                 JOIN location l ON l.id = m.location_id"""
        params = []
        if item_id is not None:
            sql += " WHERE m.item_id = ?"
            params.append(item_id)
        sql += " ORDER BY m.id DESC LIMIT ?"
        params.append(limit)
        return [dict(r) for r in self.conn.execute(sql, params)]

    def levels_for_item(self, item_id):
        return [dict(r) for r in self.conn.execute(
            """SELECT l.id AS location_id, l.name AS location, s.quantity
               FROM location l
               LEFT JOIN stock_level s
                 ON s.location_id = l.id AND s.item_id = ?
               ORDER BY l.name""",
            (item_id,),
        )]
