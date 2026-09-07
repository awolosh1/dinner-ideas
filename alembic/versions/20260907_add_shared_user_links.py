"""Create many-to-many user link tables for recipes and menu items.

Revision ID: 20260907_add_shared_user_links
Revises: 20260907_add_user_ownership
Create Date: 2026-09-07 00:00:00.000000
"""

import sqlalchemy as sa

from alembic import op

revision = "20260907_add_shared_user_links"
down_revision = "20260907_add_user_ownership"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "recipe_user_links",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_email", sa.String(), nullable=False),
        sa.Column("recipe_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_email", "recipe_id"),
    )
    op.create_index(
        op.f("ix_recipe_user_links_user_email"),
        "recipe_user_links",
        ["user_email"],
        unique=False,
    )

    op.create_table(
        "menu_item_user_links",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_email", sa.String(), nullable=False),
        sa.Column("menu_item_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["menu_item_id"], ["menu_items.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint("user_email", "menu_item_id"),
    )
    op.create_index(
        op.f("ix_menu_item_user_links_user_email"),
        "menu_item_user_links",
        ["user_email"],
        unique=False,
    )

    op.execute(
        sa.text(
            "INSERT INTO recipe_user_links (user_email, recipe_id) "
            "SELECT user_email, id FROM recipes WHERE user_email IS NOT NULL AND user_email != '' "
            "ON CONFLICT (user_email, recipe_id) DO NOTHING"
        )
    )
    op.execute(
        sa.text(
            "INSERT INTO menu_item_user_links (user_email, menu_item_id) "
            "SELECT user_email, id FROM menu_items WHERE user_email IS NOT NULL AND user_email != '' "
            "ON CONFLICT (user_email, menu_item_id) DO NOTHING"
        )
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_menu_item_user_links_user_email"), table_name="menu_item_user_links"
    )
    op.drop_table("menu_item_user_links")
    op.drop_index(
        op.f("ix_recipe_user_links_user_email"), table_name="recipe_user_links"
    )
    op.drop_table("recipe_user_links")
