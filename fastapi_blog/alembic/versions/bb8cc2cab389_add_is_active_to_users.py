
"""add_is_active_to_users

Revision ID: bb8cc2cab389
Revises: ba70f3b1c867
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "bb8cc2cab389"
down_revision: Union[str, Sequence[str], None] = "ba70f3b1c867"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Post modeliga updated_at qo'shish
    op.add_column(
        "posts",
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=True
        )
    )

    # User modeliga is_active qo'shish
    op.add_column(
        "users",
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("TRUE"),
            nullable=False
        )
    )


def downgrade() -> None:
    # O'zgarishlarni orqaga qaytarish
    op.drop_column("users", "is_active")
    op.drop_column("posts", "updated_at")
