"""SQLite connection, schema setup, and transactions."""

import sqlite3
from contextlib import contextmanager

SCHEMA = """
CREATE TABLE IF NOT EXISTS category (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS location (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS item (
    id               INTEGER PRIMARY KEY,
    sku              TEXT NOT NULL UNIQUE,
    name             TEXT NOT NULL,
    category_id      INTEGER NOT NULL REFERENCES category(id),
    unit_cost_cents  INTEGER NOT NULL CHECK (unit_cost_cents >= 0),
    reorder_level    INTEGER NOT NULL CHECK (reorder_level >= 0),
    is_active        INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_item_category ON item(category_id);

CREATE TABLE IF NOT EXISTS stock_level (
    item_id     INTEGER NOT NULL REFERENCES item(id),
    location_id INTEGER NOT NULL REFERENCES location(id),
    quantity    INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (item_id, location_id)
);

CREATE TABLE IF NOT EXISTS stock_movement (
    id              INTEGER PRIMARY KEY,
    item_id         INTEGER NOT NULL REFERENCES item(id),
    location_id     INTEGER NOT NULL REFERENCES location(id),
    movement_type   TEXT NOT NULL CHECK (movement_type IN ('IN', 'OUT', 'ADJUST')),
    quantity_change INTEGER NOT NULL CHECK (quantity_change <> 0),
    reason          TEXT NOT NULL,
    over_issue      INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT NOT NULL,
    CHECK (
        (movement_type = 'IN' AND quantity_change > 0)
        OR (movement_type = 'OUT' AND quantity_change < 0)
        OR movement_type = 'ADJUST'
    )
);
CREATE INDEX IF NOT EXISTS idx_movement_item_time ON stock_movement(item_id, created_at);
"""


def connect(db_path):
    """Open a connection with foreign keys on and manual transaction control."""
    conn = sqlite3.connect(db_path, isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn):
    """Create all tables and indexes if they do not exist."""
    conn.executescript(SCHEMA)


@contextmanager
def transaction(conn):
    """Run a block in one write transaction; roll back if it raises."""
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
    except Exception:
        conn.execute("ROLLBACK")
        raise
    else:
        conn.execute("COMMIT")
