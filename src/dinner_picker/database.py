"""
SQLite database layer for the Dinner Picker app.

Four tables:
  - recipes:      home-cooking ideas
  - ingredients:  canonical ingredient catalog shared across recipes
  - recipe_ingredients: per-recipe ingredient rows, with quantity/notes
  - restaurants:  local restaurants, added manually by name (+ one picture)
  - menu_items:   individual dishes, added by item, linked to a restaurant.
                  If a menu item has no picture of its own, it falls back
                  to the restaurant's picture (per the "pictures come from
                  the restaurant" rule).
"""

import os
import sqlite3
import tomllib
from contextlib import contextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlmodel import Session, create_engine

BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dinner_picker.db")

engine = create_engine(DATABASE_URL, echo=False)

def _alembic_config() -> Config:
    cfg = Config(str(BASE_DIR / "alembic.ini"))

    pyproject_path = BASE_DIR / "pyproject.toml"
    with pyproject_path.open("rb") as fh:
        pyproject = tomllib.load(fh)

    alembic_cfg = pyproject.get("tool", {}).get("alembic", {})
    if "script_location" in alembic_cfg:
        cfg.set_main_option("script_location", str(BASE_DIR / alembic_cfg["script_location"]))
    if "sqlalchemy.url" in alembic_cfg:
        cfg.set_main_option("sqlalchemy.url", alembic_cfg["sqlalchemy.url"])

    cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    return cfg


def init_db() -> None:
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
