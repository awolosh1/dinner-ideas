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
import tomllib
from contextlib import contextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "dinner.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"


def _alembic_config() -> Config:
    cfg = Config(str(BASE_DIR / "alembic.ini"))

    pyproject_path = BASE_DIR / "pyproject.toml"
    with pyproject_path.open("rb") as fh:
        pyproject = tomllib.load(fh)

    alembic_cfg = pyproject.get("tool", {}).get("alembic", {})
    for key, value in alembic_cfg.items():
        if key == "script_location":
            cfg.set_main_option("script_location", str(BASE_DIR / value))
        elif key == "sqlalchemy.url":
            cfg.set_main_option("sqlalchemy.url", value)

    cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    return cfg


def init_db():
    command.upgrade(_alembic_config(), "head")


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()
