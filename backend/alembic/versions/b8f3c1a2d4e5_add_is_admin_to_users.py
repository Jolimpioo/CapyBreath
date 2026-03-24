"""add is_admin to users

Revision ID: b8f3c1a2d4e5
Revises: ae204bc0a436
Create Date: 2026-03-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b8f3c1a2d4e5'
down_revision: Union[str, None] = 'ae204bc0a436'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false')
    )


def downgrade() -> None:
    op.drop_column('users', 'is_admin')
