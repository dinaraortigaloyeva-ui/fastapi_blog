"""rename_content_to_body_in_posts

Revision ID: ba70f3b1c867
Revises: a967e9088119
Create Date: 2026-10-06 23:38:39.203887

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba70f3b1c867'
down_revision: Union[str, Sequence[str], None] = 'a967e9088119'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'posts',
        'content',
        new_column_name='body'
    )


def downgrade() -> None:
    op.alter_column(
        'posts',
        'body',
        new_column_name='content'
    )