"""add inventory and wishlist

Revision ID: b8a92dc31f20
Revises: 7d41f3c2e9b1
Create Date: 2026-05-13 00:00:01.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = "b8a92dc31f20"
down_revision: Union[str, Sequence[str], None] = "7d41f3c2e9b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("product", sa.Column("stock", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("product", sa.Column("image_url", sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column("product", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_index(op.f("ix_product_is_active"), "product", ["is_active"], unique=False)
    op.create_table(
        "wishlistitem",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["product.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("wishlistitem")
    op.drop_index(op.f("ix_product_is_active"), table_name="product")
    op.drop_column("product", "is_active")
    op.drop_column("product", "image_url")
    op.drop_column("product", "stock")
