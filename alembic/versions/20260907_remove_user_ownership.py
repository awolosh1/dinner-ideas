"""Remove single-owner columns from recipes, restaurants, and menu items.

Revision ID: 20260907_remove_user_ownership
Revises: 20260907_add_shared_user_links
Create Date: 2026-09-07 00:00:00.000000
"""

import sqlalchemy as sa

from alembic import op

revision = "20260907_remove_user_ownership"
down_revision = "20260907_add_shared_user_links"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("menu_items") as batch_op:
        if batch_op.get_bind().dialect.name == "sqlite":
            batch_op.drop_index(batch_op.f("ix_menu_items_user_email"))
        batch_op.drop_column("user_email")

    with op.batch_alter_table("restaurants") as batch_op:
        if batch_op.get_bind().dialect.name == "sqlite":
            batch_op.drop_index(batch_op.f("ix_restaurants_user_email"))
        batch_op.drop_column("user_email")

    with op.batch_alter_table("recipes") as batch_op:
        if batch_op.get_bind().dialect.name == "sqlite":
            batch_op.drop_index(batch_op.f("ix_recipes_user_email"))
        batch_op.drop_column("user_email")


def downgrade() -> None:
    with op.batch_alter_table("recipes") as batch_op:
        batch_op.add_column(
            sa.Column("user_email", sa.String(), nullable=False, server_default="")
        )
        batch_op.create_index(
            batch_op.f("ix_recipes_user_email"), ["user_email"], unique=False
        )

    with op.batch_alter_table("restaurants") as batch_op:
        batch_op.add_column(
            sa.Column("user_email", sa.String(), nullable=False, server_default="")
        )
        batch_op.create_index(
            batch_op.f("ix_restaurants_user_email"), ["user_email"], unique=False
        )

    with op.batch_alter_table("menu_items") as batch_op:
        batch_op.add_column(
            sa.Column("user_email", sa.String(), nullable=False, server_default="")
        )
        batch_op.create_index(
            batch_op.f("ix_menu_items_user_email"), ["user_email"], unique=False
        )
