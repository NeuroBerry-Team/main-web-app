"""Add user sessions table for login tracking

Revision ID: add_user_sessions
Revises: 20250828_insert_first_model_data
Create Date: 2025-08-31

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_user_sessions'
down_revision = '20250828_insert_first_model_data'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('user_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('userId', sa.Integer(), nullable=False),
        sa.Column('loginAt', sa.DateTime(), nullable=False),
        sa.Column('logoutAt', sa.DateTime(), nullable=True),  # NULL = still active
        sa.Column('ipAddress', sa.String(45), nullable=True),
        sa.Column('userAgent', sa.String(200), nullable=True),  # Browser/OS info
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['userId'], ['users.id'], ondelete='CASCADE'),
        sa.Index('idx_user_sessions_user_login', 'userId', 'loginAt'),
        sa.Index('idx_user_sessions_login_date', 'loginAt')  # For date-based queries
    )

def downgrade():
    op.drop_table('user_sessions')