"""initial schema

Revision ID: initial_schema
Revises: 
Create Date: 2024-03-27 16:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create wine_categories table
    op.create_table('wine_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create wine_regions table
    op.create_table('wine_regions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create wine_varietals table
    op.create_table('wine_varietals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create wines table with all necessary columns
    op.create_table('wines',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=True),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('alcohol_percentage', sa.Float(), nullable=True),
        sa.Column('varietal_id', sa.Integer(), nullable=True),
        sa.Column('region_id', sa.Integer(), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['wine_categories.id'], ),
        sa.ForeignKeyConstraint(['region_id'], ['wine_regions.id'], ),
        sa.ForeignKeyConstraint(['varietal_id'], ['wine_varietals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create wine_traits table
    op.create_table('wine_traits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create wine_traits_association table
    op.create_table('wine_traits_association',
        sa.Column('wine_id', sa.Integer(), nullable=False),
        sa.Column('trait_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['trait_id'], ['wine_traits.id'], ),
        sa.ForeignKeyConstraint(['wine_id'], ['wines.id'], ),
        sa.PrimaryKeyConstraint('wine_id', 'trait_id')
    )

def downgrade():
    # Drop tables in reverse order of creation
    op.drop_table('wine_traits_association')
    op.drop_table('wine_traits')
    op.drop_table('wines')
    op.drop_table('wine_varietals')
    op.drop_table('wine_regions')
    op.drop_table('wine_categories') 