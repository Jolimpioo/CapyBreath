"""add round metadata to sessions

Revision ID: c1d2e3f4a5b6
Revises: b8f3c1a2d4e5
Create Date: 2026-05-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, None] = 'b8f3c1a2d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'sessions',
        sa.Column('session_group_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.add_column(
        'sessions',
        sa.Column('round_number', sa.Integer(), nullable=False, server_default='1')
    )
    op.add_column(
        'sessions',
        sa.Column('total_rounds', sa.Integer(), nullable=False, server_default='1')
    )

    op.execute('UPDATE sessions SET session_group_id = id WHERE session_group_id IS NULL')
    op.alter_column('sessions', 'session_group_id', nullable=False)

    op.create_index('ix_sessions_session_group_id', 'sessions', ['session_group_id'])
    op.create_check_constraint(
        'ck_sessions_round_number_positive',
        'sessions',
        'round_number > 0'
    )
    op.create_check_constraint(
        'ck_sessions_total_rounds_positive',
        'sessions',
        'total_rounds > 0'
    )
    op.create_check_constraint(
        'ck_sessions_round_number_lte_total_rounds',
        'sessions',
        'round_number <= total_rounds'
    )


def downgrade() -> None:
    op.drop_constraint('ck_sessions_round_number_lte_total_rounds', 'sessions', type_='check')
    op.drop_constraint('ck_sessions_total_rounds_positive', 'sessions', type_='check')
    op.drop_constraint('ck_sessions_round_number_positive', 'sessions', type_='check')
    op.drop_index('ix_sessions_session_group_id', table_name='sessions')
    op.drop_column('sessions', 'total_rounds')
    op.drop_column('sessions', 'round_number')
    op.drop_column('sessions', 'session_group_id')
