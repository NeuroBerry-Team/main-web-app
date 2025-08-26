"""add_default_superadmin_user

Revision ID: de8bc6094fb5
Revises: b616b50f0d4a
Create Date: 2025-08-26 22:41:04.371959

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'de8bc6094fb5'
down_revision = 'b616b50f0d4a'
branch_labels = None
depends_on = None


def upgrade():
    # Insert the default SUPERADMIN user
    # Password is 'Pass$612345' hashed with bcrypt and salt 10
    op.execute("""
        INSERT INTO users (name, "lastName", email, password, "roleId") 
        VALUES ('SUPERADMIN', 'SUPER', 'admin@gmail.com', '$2b$10$D1z2Q2Ms.R.JIk.3bif9fectcs3ilUqTGoUWQvkc9xNtS0Yygfkf2', 1)
        ON CONFLICT (email) DO NOTHING;
    """)


def downgrade():
    # Remove the default SUPERADMIN user
    op.execute("DELETE FROM users WHERE email = 'admin@gmail.com';")
