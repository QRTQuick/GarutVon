"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-06
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(120), nullable=False), sa.Column("email", sa.String(255), nullable=False), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("is_admin", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_table("api_keys", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("label", sa.String(120), nullable=False), sa.Column("key", sa.String(80), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_api_keys_key", "api_keys", ["key"], unique=True)
    op.create_table("api_logs", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("endpoint", sa.String(120), nullable=False), sa.Column("status", sa.String(40), nullable=False), sa.Column("detail", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("downloads", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("platform", sa.String(80), nullable=False), sa.Column("ip_address", sa.String(80), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("support_tickets", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_email", sa.String(255), nullable=False), sa.Column("subject", sa.String(180), nullable=False), sa.Column("message", sa.Text(), nullable=False), sa.Column("status", sa.String(40), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))


def downgrade() -> None:
    op.drop_table("support_tickets")
    op.drop_table("downloads")
    op.drop_table("api_logs")
    op.drop_index("ix_api_keys_key", table_name="api_keys")
    op.drop_table("api_keys")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
