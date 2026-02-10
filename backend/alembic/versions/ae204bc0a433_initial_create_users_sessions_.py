"""Initial: create users, sessions, achievements, user_achievements tables

Revision ID: ae204bc0a433
Revises: 
Create Date: 2026-02-06 11:44:36.756175

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ae204bc0a433'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ==================== USERS TABLE ====================
    op.create_table(
        'users',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('total_sessions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_retention_time', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('best_retention_time', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('current_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('longest_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_session_date', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_created_at'), 'users', ['created_at'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=False)

    # ==================== SESSIONS TABLE ====================
    op.create_table(
        'sessions',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('user_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('breaths_count', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('retention_time', sa.Integer(), nullable=False),
        sa.Column('recovery_time', sa.Integer(), nullable=False, server_default='15'),
        sa.Column('session_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('duration_seconds', sa.Integer(), nullable=False),
        sa.Column('notes', sa.String(500), nullable=True),
        sa.Column('mood_before', sa.Integer(), nullable=True),
        sa.Column('mood_after', sa.Integer(), nullable=True),
        sa.Column('technique_variant', sa.String(50), nullable=False, server_default='standard'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('retention_time >= 0', name='retention_time_positive'),
        sa.CheckConstraint('breaths_count > 0', name='breaths_count_positive'),
        sa.CheckConstraint('duration_seconds > 0', name='duration_seconds_positive'),
        sa.CheckConstraint('mood_before IS NULL OR (mood_before >= 1 AND mood_before <= 10)', name='mood_before_range'),
        sa.CheckConstraint('mood_after IS NULL OR (mood_after >= 1 AND mood_after <= 10)', name='mood_after_range')
    )
    op.create_index(op.f('ix_sessions_created_at'), 'sessions', ['created_at'], unique=False)
    op.create_index(op.f('ix_sessions_session_date'), 'sessions', ['session_date'], unique=False)
    op.create_index(op.f('ix_sessions_user_id'), 'sessions', ['user_id'], unique=False)

    # ==================== ACHIEVEMENTS TABLE ====================
    op.create_table(
        'achievements',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('icon_emoji', sa.String(10), nullable=False),
        sa.Column('unlock_condition', sa.String(50), nullable=False),
        sa.Column('unlock_value', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_achievements_created_at'), 'achievements', ['created_at'], unique=False)
    op.create_index(op.f('ix_achievements_category'), 'achievements', ['category'], unique=False)

    # ==================== USER_ACHIEVEMENTS TABLE ====================
    op.create_table(
        'user_achievements',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('user_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('achievement_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('unlocked_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['achievement_id'], ['achievements.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'achievement_id', name='_user_achievement_uc')
    )
    op.create_index(op.f('ix_user_achievements_created_at'), 'user_achievements', ['created_at'], unique=False)
    op.create_index(op.f('ix_user_achievements_user_id'), 'user_achievements', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_achievements_achievement_id'), 'user_achievements', ['achievement_id'], unique=False)


def downgrade() -> None:
    # Drop in reverse order of creation (due to foreign keys)
    op.drop_index(op.f('ix_user_achievements_achievement_id'), table_name='user_achievements')
    op.drop_index(op.f('ix_user_achievements_user_id'), table_name='user_achievements')
    op.drop_index(op.f('ix_user_achievements_created_at'), table_name='user_achievements')
    op.drop_table('user_achievements')
    
    op.drop_index(op.f('ix_achievements_category'), table_name='achievements')
    op.drop_index(op.f('ix_achievements_created_at'), table_name='achievements')
    op.drop_table('achievements')
    
    op.drop_index(op.f('ix_sessions_user_id'), table_name='sessions')
    op.drop_index(op.f('ix_sessions_session_date'), table_name='sessions')
    op.drop_index(op.f('ix_sessions_created_at'), table_name='sessions')
    op.drop_table('sessions')
    
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_created_at'), table_name='users')
    op.drop_table('users')
