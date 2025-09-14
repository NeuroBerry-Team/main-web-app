"""Remove static model data insertion

Revision ID: remove_static_model_data
Revises: 20250901_add_metadata_url
Create Date: 2025-09-13

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "remove_static_model_data"
down_revision = "20250901_add_metadata_url"
branch_labels = None
depends_on = None


def upgrade():
    """
    Remove the statically inserted model data since models are now handled dynamically by code.
    This removes the YOLOv8_1 model that was inserted in the 20250828_insert_first_model_data migration.
    """
    # Delete the static model data that was inserted previously
    op.execute("DELETE FROM models WHERE id = 1 AND name = 'YOLOv8_1';")

    # Reset the sequence to start from 1 since we're removing static data
    op.execute(
        """
        SELECT setval('models_id_seq', 1, false);
    """
    )


def downgrade():
    """
    Restore the static model data for rollback compatibility.
    """
    op.execute(
        """
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
    """
    )

    # Fix the sequence to start from the next available ID
    op.execute(
        """
        SELECT setval('models_id_seq',
                     (SELECT COALESCE(MAX(id), 0) FROM models) + 1,
                     false);
    """
    )
