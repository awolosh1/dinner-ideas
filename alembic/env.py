from logging.config import fileConfig
from pathlib import Path
import tomllib

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

from dinner_picker.models import *

config = context.config

pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
with pyproject_path.open("rb") as fh:
    pyproject = tomllib.load(fh)

alembic_cfg = pyproject.get("tool", {}).get("alembic", {})
if "sqlalchemy.url" in alembic_cfg:
    config.set_main_option("sqlalchemy.url", alembic_cfg["sqlalchemy.url"])
if "script_location" in alembic_cfg:
    config.set_main_option("script_location", str(Path(__file__).resolve().parents[1] / alembic_cfg["script_location"]))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
