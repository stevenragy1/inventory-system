"""Catalog rules: categories, locations, items."""

from app.db import transaction
from app.errors import DomainError, DuplicateError, NotFoundError
from app.repositories.catalog_repo import CatalogRepo


class CatalogService:
    def __init__(self, conn):
        self.conn = conn
        self.repo = CatalogRepo(conn)

    @staticmethod
    def _clean_name(value, label):
        name = (value or "").strip()
        if not name:
            raise DomainError(f"{label} is required.")
        return name

    # Categories and locations ----------------------------------------------

    def create_category(self, name):
        name = self._clean_name(name, "Category name")
        if any(c["name"].lower() == name.lower() for c in self.repo.list_categories()):
            raise DuplicateError(f"Category '{name}' already exists.")
        with transaction(self.conn):
            cid = self.repo.insert_category(name)
        return self.repo.find_category(cid)

    def list_categories(self):
        return self.repo.list_categories()

    def create_location(self, name):
        name = self._clean_name(name, "Location name")
        if any(l["name"].lower() == name.lower() for l in self.repo.list_locations()):
            raise DuplicateError(f"Location '{name}' already exists.")
        with transaction(self.conn):
            lid = self.repo.insert_location(name)
        return self.repo.find_location(lid)

    def list_locations(self):
        return self.repo.list_locations()

    # Items -------------------------------------------------------------------

    def create_item(self, sku, name, category_id, unit_cost_cents, reorder_level):
        sku = self._clean_name(sku, "SKU").upper()
        name = self._clean_name(name, "Item name")
        if self.repo.find_category(category_id) is None:
            raise NotFoundError(f"Category {category_id} not found.")
        if not isinstance(unit_cost_cents, int) or unit_cost_cents < 0:
            raise DomainError("Unit cost must be zero or more, in whole cents.")
        if not isinstance(reorder_level, int) or reorder_level < 0:
            raise DomainError("Reorder level must be zero or more.")
        if self.repo.find_item_by_sku(sku) is not None:
            raise DuplicateError(f"SKU '{sku}' already exists.")

        with transaction(self.conn):
            iid = self.repo.insert_item(
                sku, name, category_id, unit_cost_cents, reorder_level)
        return self.repo.find_item(iid)

    def get_item(self, item_id):
        item = self.repo.find_item(item_id)
        if item is None:
            raise NotFoundError(f"Item {item_id} not found.")
        return item

    def list_items(self, include_inactive=False):
        return self.repo.list_items(include_inactive=include_inactive)

    def deactivate_item(self, item_id):
        self.get_item(item_id)
        with transaction(self.conn):
            self.repo.set_item_active(item_id, False)
        return self.repo.find_item(item_id)
