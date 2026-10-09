"""add_phone_to_users

Revision ID: a967e9088119
Revises: 1a1a7c85a4fc
Create Date: 2026-10-05 16:09:33.197965

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a967e9088119'
down_revision: Union[str, Sequence[str], None] = '1a1a7c85a4fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column('phone', sa.String(length=20), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'phone')