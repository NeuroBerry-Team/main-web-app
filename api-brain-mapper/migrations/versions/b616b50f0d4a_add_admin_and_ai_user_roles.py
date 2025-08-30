"""add_admin_and_ai_user_roles

Revision ID: b616b50f0d4a
Revises: 5c4043a139b6
Create Date: 2025-08-26 22:34:59.889556

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b616b50f0d4a'
down_revision = '5c4043a139b6'
branch_labels = None
depends_on = None


def upgrade():
    # Insert all required roles
    op.execute("INSERT INTO roles (id, name) VALUES (1, 'SUPERADMIN') ON CONFLICT (id) DO NOTHING;")
    op.execute("INSERT INTO roles (id, name) VALUES (2, 'ADMIN') ON CONFLICT (id) DO NOTHING;")
    op.execute("INSERT INTO roles (id, name) VALUES (3, 'AI_USER') ON CONFLICT (id) DO NOTHING;")
    
    # Fix the sequence to start from the next available ID
    op.execute("""
        SELECT setval('roles_id_seq',
                     (SELECT COALESCE(MAX(id), 0) FROM roles) + 1,
                     false);
    """)


def downgrade():
    # Remove the added roles (keep existing roles that might have been added manually)
    op.execute("DELETE FROM roles WHERE name IN ('ADMIN', 'AI_USER');")
