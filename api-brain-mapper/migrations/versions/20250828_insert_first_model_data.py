"""insert first model data

Revision ID: 20250828_insert_first_model_data
Revises: de8bc6094fb5  # <-- set this to your latest migration's revision id
Create Date: 2025-08-28

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, DateTime
import datetime

# revision identifiers, used by Alembic.
revision = '20250828_insert_first_model_data'
down_revision = 'de8bc6094fb5'
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""
        INSERT INTO models (id, name, version, description, "modelType", "createdOn", "updatedOn")
        VALUES (
            1,
            'YOLOv8_1',
            '1.0',
            'Default model.',
            'YOLO',
            NOW(),
            NOW()
        )
        ON CONFLICT (id) DO NOTHING;
    """)
    
    # Fix the sequence to start from the next available ID
    op.execute("""
        SELECT setval('models_id_seq',
                     (SELECT COALESCE(MAX(id), 0) FROM models) + 1,
                     false);
    """)


def downgrade():
    op.execute("DELETE FROM models WHERE id=1;")