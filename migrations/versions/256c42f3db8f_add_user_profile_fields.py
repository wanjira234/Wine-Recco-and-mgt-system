"""Add user profile fields

Revision ID: 256c42f3db8f
Revises: abcdef123456
Create Date: 2025-03-25 20:59:47.880

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '256c42f3db8f'
down_revision = 'abcdef123456'
branch_labels = None
depends_on = None

def upgrade():
    # Create a new table with all required fields
    op.create_table(
        'users_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=64), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=128), nullable=False),
        sa.Column('first_name', sa.String(length=64), nullable=True),
        sa.Column('last_name', sa.String(length=64), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('wine_preferences', sa.JSON(), nullable=True),
        sa.Column('taste_preferences', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )

    # Copy data from old table to new table
    op.execute('''
        INSERT INTO users_new (id, username, email, password_hash)
        SELECT id, username, email, password_hash
        FROM users
    ''')

    # Drop the old table
    op.drop_table('users')

    # Rename the new table to users
    op.rename_table('users_new', 'users')

def downgrade():
    # Create a new table with old schema
    op.create_table(
        'users_old',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=64), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=256), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )

    # Copy data from new table to old table
    op.execute('''
        INSERT INTO users_old (id, username, email, password_hash)
        SELECT id, username, email, password_hash
        FROM users
    ''')

    # Drop the new table
    op.drop_table('users')

    # Rename the old table to users
    op.rename_table('users_old', 'users')
