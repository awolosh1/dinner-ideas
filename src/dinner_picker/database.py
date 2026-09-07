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
from contextlib import contextmanager
from pathlib import Path

from alembic.config import Config
from sqlmodel import create_engine

from alembic import command

BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dinner.db")

engine = create_engine(DATABASE_URL, echo=False)


def _alembic_config() -> Config:
    cfg = Config(str(BASE_DIR / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    return cfg


def init_db() -> None:
    command.upgrade(_alembic_config(), "head")


@contextmanager
def get_conn():
    with engine.connect() as conn:
        yield conn
