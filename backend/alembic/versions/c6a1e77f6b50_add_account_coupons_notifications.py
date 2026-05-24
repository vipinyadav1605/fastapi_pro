"""add account coupons notifications

Revision ID: c6a1e77f6b50
Revises: b8a92dc31f20
Create Date: 2026-05-13 00:00:02.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = "c6a1e77f6b50"
down_revision: Union[str, Sequence[str], None] = "b8a92dc31f20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("product", sa.Column("brand", sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column("product", sa.Column("sku", sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column("product", sa.Column("tags", sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column("product", sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False, server_default="published"))
    op.create_index(op.f("ix_product_brand"), "product", ["brand"], unique=False)
    op.create_index(op.f("ix_product_sku"), "product", ["sku"], unique=True)
    op.create_index(op.f("ix_product_status"), "product", ["status"], unique=False)
    op.create_table(
        "address",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("label", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("full_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("phone", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("line1", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("line2", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("city", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("state", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("postal_code", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("country", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "savedpaymentmethod",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("provider", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("brand", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("last4", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("expiry_month", sa.Integer(), nullable=True),
        sa.Column("expiry_year", sa.Integer(), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "coupon",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("discount_percent", sa.Float(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("min_order_amount", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_coupon_code"), "coupon", ["code"], unique=True)
    op.create_index(op.f("ix_coupon_is_active"), "coupon", ["is_active"], unique=False)
    op.create_table(
        "notification",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("message", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notification_is_read"), "notification", ["is_read"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_notification_is_read"), table_name="notification")
    op.drop_table("notification")
    op.drop_index(op.f("ix_coupon_is_active"), table_name="coupon")
    op.drop_index(op.f("ix_coupon_code"), table_name="coupon")
    op.drop_table("coupon")
    op.drop_table("savedpaymentmethod")
    op.drop_table("address")
    op.drop_index(op.f("ix_product_status"), table_name="product")
    op.drop_index(op.f("ix_product_sku"), table_name="product")
    op.drop_index(op.f("ix_product_brand"), table_name="product")
    op.drop_column("product", "status")
    op.drop_column("product", "tags")
    op.drop_column("product", "sku")
    op.drop_column("product", "brand")
