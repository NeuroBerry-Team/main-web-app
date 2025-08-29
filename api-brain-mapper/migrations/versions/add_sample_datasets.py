"""Add sample datasets for training

Revision ID: add_sample_datasets
Revises: 20250828_insert_first_model_data
Create Date: 2025-08-28

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_sample_datasets'
down_revision = '20250828_insert_first_model_data'
branch_labels = None
depends_on = None

# SAMPLE DATA TEST DATA - SHOULD DELETE THIS MIGRATION A DO A PROPER ONE WHEN DATASET IS FINISHED
def upgrade():
    # Get the superadmin user ID
    # (assuming it was created in a previous migration)
    connection = op.get_bind()
    query = "SELECT id FROM users WHERE email = 'admin@neuroberry.com' LIMIT 1"
    result = connection.execute(sa.text(query))
    user_id = result.fetchone()

    if user_id:
        user_id = user_id[0]
    else:
        # Fallback to user ID 1 if superadmin not found
        user_id = 1

    # Insert sample datasets
    op.execute(sa.text(f"""
        INSERT INTO datasets (id, name, description, "datasetType",
                             "s3Path", "createdBy", "createdOn")
        VALUES
        (
            1,
            'Frambuesas_Dataset_v1',
            'Dataset inicial con imágenes de frambuesas maduras e inmaduras. '
            'Contiene aproximadamente 500 imágenes etiquetadas.',
            'YOLO',
            's3://neuroberry-datasets/frambuesas/v1/',
            {user_id},
            NOW()
        ),
        (
            2,
            'Frambuesas_Augmented_v2',
            'Dataset aumentado con transformaciones y más imágenes. '
            'Incluye rotaciones, cambios de brillo y 1000+ imágenes.',
            'YOLO',
            's3://neuroberry-datasets/frambuesas/v2/',
            {user_id},
            NOW()
        ),
        (
            3,
            'Frambuesas_Quality_Dataset',
            'Dataset especializado en clasificación de calidad de frambuesas. '
            'Incluye categorías: perfecta, buena, defectuosa.',
            'YOLO',
            's3://neuroberry-datasets/frambuesas/quality/',
            {user_id},
            NOW()
        )
        ON CONFLICT (id) DO NOTHING;
    """))


def downgrade():
    op.execute(sa.text("DELETE FROM datasets WHERE id IN (1, 2, 3);"))
