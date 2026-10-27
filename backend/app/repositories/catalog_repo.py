"""SQL access for categories, locations, and items. No business rules here."""


class CatalogRepo:
    def __init__(self, conn):
        self.conn = conn

    # Categories
    def insert_category(self, name):
        cur = self.conn.execute("INSERT INTO category (name) VALUES (?)", (name,))
        return cur.lastrowid

    def list_categories(self):
        return [dict(r) for r in self.conn.execute(
            "SELECT id, name FROM category ORDER BY name")]

    def find_category(self, category_id):
        row = self.conn.execute(
            "SELECT id, name FROM category WHERE id = ?", (category_id,)).fetchone()
        return dict(row) if row else None

    # Locations
    def insert_location(self, name):
        cur = self.conn.execute("INSERT INTO location (name) VALUES (?)", (name,))
        return cur.lastrowid

    def list_locations(self):
        return [dict(r) for r in self.conn.execute(
            "SELECT id, name FROM location ORDER BY name")]

    def find_location(self, location_id):
        row = self.conn.execute(
            "SELECT id, name FROM location WHERE id = ?", (location_id,)).fetchone()
        return dict(row) if row else None

    # Items
    def insert_item(self, sku, name, category_id, unit_cost_cents, reorder_level):
        cur = self.conn.execute(
            """INSERT INTO item (sku, name, category_id, unit_cost_cents, reorder_level)
               VALUES (?, ?, ?, ?, ?)""",
            (sku, name, category_id, unit_cost_cents, reorder_level),
        )
        return cur.lastrowid

    def find_item(self, item_id):
        row = self.conn.execute(
            """SELECT i.id, i.sku, i.name, i.category_id, c.name AS category,
                      i.unit_cost_cents, i.reorder_level, i.is_active
               FROM item i JOIN category c ON c.id = i.category_id
               WHERE i.id = ?""",
            (item_id,),
        ).fetchone()
        return dict(row) if row else None

    def find_item_by_sku(self, sku):
        row = self.conn.execute(
            "SELECT id FROM item WHERE sku = ?", (sku,)).fetchone()
        return row["id"] if row else None

    def list_items(self, include_inactive=False):
        sql = """SELECT i.id, i.sku, i.name, i.category_id, c.name AS category,
                        i.unit_cost_cents, i.reorder_level, i.is_active
                 FROM item i JOIN category c ON c.id = i.category_id"""
        if not include_inactive:
            sql += " WHERE i.is_active = 1"
        sql += " ORDER BY i.sku"
        return [dict(r) for r in self.conn.execute(sql)]

    def set_item_active(self, item_id, is_active):
        self.conn.execute(
            "UPDATE item SET is_active = ? WHERE id = ?",
            (1 if is_active else 0, item_id),
        )
