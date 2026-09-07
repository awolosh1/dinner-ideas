"""Initial schema matching the current app before ingredient feature work.

Revision ID: 20260906_initial_current_schema
Revises:
Create Date: 2026-09-06 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260906_initial_current_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "recipes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False, server_default=""),
        sa.Column("image_url", sa.String(), nullable=False, server_default=""),
        if_not_exists=True,
    )
    op.create_index(
        op.f("ix_recipes_name"), "recipes", ["name"], unique=False, if_not_exists=True
    )

    op.create_table(
        "restaurants",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("image_url", sa.String(), nullable=False, server_default=""),
        if_not_exists=True,
    )
    op.create_index(
        op.f("ix_restaurants_name"),
        "restaurants",
        ["name"],
        unique=False,
        if_not_exists=True,
    )

    op.create_table(
        "menu_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("restaurant_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False, server_default=""),
        sa.Column("price", sa.String(), nullable=False, server_default=""),
        sa.Column("image_url", sa.String(), nullable=False, server_default=""),
        sa.ForeignKeyConstraint(
            ["restaurant_id"], ["restaurants.id"], ondelete="CASCADE"
        ),
        if_not_exists=True,
    )
    op.create_index(
        op.f("ix_menu_items_name"),
        "menu_items",
        ["name"],
        unique=False,
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table("menu_items")
    op.drop_table("restaurants")
    op.drop_table("recipes")
