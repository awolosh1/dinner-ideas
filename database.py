"""
SQLite database layer for the Dinner Picker app.

Three tables:
  - recipes:      home-cooking ideas
  - restaurants:  local restaurants, added manually by name (+ one picture)
  - menu_items:   individual dishes, added by item, linked to a restaurant.
                  If a menu item has no picture of its own, it falls back
                  to the restaurant's picture (per the "pictures come from
                  the restaurant" rule).
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(__file__).parent / "dinner.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS recipes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    description TEXT DEFAULT '',
    image_url   TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS restaurants (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    image_url   TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS menu_items (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_id INTEGER NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    name          TEXT NOT NULL,
    description   TEXT DEFAULT '',
    price         TEXT DEFAULT '',
    image_url     TEXT DEFAULT ''
);
"""

SEED = """
INSERT INTO restaurants (name, image_url) VALUES
    ('Luigi''s Pizzeria', 'https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600'),
    ('Golden Dragon',     'https://images.unsplash.com/photo-1526318896980-cf78c088247c?w=600');

INSERT INTO menu_items (restaurant_id, name, description, price, image_url) VALUES
    (1, 'Margherita Pizza', 'Classic tomato, mozzarella, basil', '$14', ''),
    (1, 'Chicken Parm Sub', 'Breaded chicken, marinara, provolone', '$12', ''),
    (2, 'General Tso''s Chicken', 'Crispy chicken in sweet-spicy sauce', '$13', ''),
    (2, 'Vegetable Lo Mein', 'Stir-fried noodles with mixed vegetables', '$11', '');

INSERT INTO recipes (name, description, image_url) VALUES
    ('Homemade Tacos', 'Ground beef or veggie tacos with all the fixings',
     'https://images.unsplash.com/photo-1551504734-5ee1c4a1479b?w=600'),
    ('Sheet-Pan Salmon', 'Salmon and roasted veggies, one pan, 25 minutes',
     'https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=600'),
    ('Creamy Mushroom Risotto', 'Slow-stirred arborio rice with mushrooms and parmesan',
     'https://images.unsplash.com/photo-1476124369491-e7addf5db371?w=600');
"""


def _needs_seed(conn) -> bool:
    row = conn.execute(
        "SELECT (SELECT COUNT(*) FROM recipes) + (SELECT COUNT(*) FROM restaurants)"
    ).fetchone()
    return row[0] == 0


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)
        if _needs_seed(conn):
            conn.executescript(SEED)
        conn.commit()


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()
