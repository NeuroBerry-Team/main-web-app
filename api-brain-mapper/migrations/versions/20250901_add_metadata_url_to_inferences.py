"""Add metadataUrl to inferences table

Revision ID: 20250901_add_metadata_url
Revises: add_user_sessions
Create Date: 2025-09-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250901_add_metadata_url'
down_revision = 'add_user_sessions'
branch_labels = None
depends_on = None


def upgrade():
    # Add metadataUrl column to inferences table
    op.add_column('inferences',
                  sa.Column('metadataUrl', sa.String(), nullable=True))


def downgrade():
    # Remove metadataUrl column from inferences table
    op.drop_column('inferences', 'metadataUrl')
