"""Complete schema

Revision ID: abcdef123456
Revises: 
Create Date: 2024-03-24 20:25:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'abcdef123456'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Drop existing tables if they exist
    op.execute('DROP TABLE IF EXISTS user_traits')
    op.execute('DROP TABLE IF EXISTS wine_traits_association')
    op.execute('DROP TABLE IF EXISTS wine_traits')
    op.execute('DROP TABLE IF EXISTS users')
    op.execute('DROP TABLE IF EXISTS wine_varietals')
    op.execute('DROP TABLE IF EXISTS wine_regions')
    op.execute('DROP TABLE IF EXISTS wines')
    op.execute('DROP TABLE IF EXISTS user_preference')
    op.execute('DROP TABLE IF EXISTS wine_reviews')
    op.execute('DROP TABLE IF EXISTS user_wine_interactions')
    op.execute('DROP TABLE IF EXISTS wine_restocks')
    op.execute('DROP TABLE IF EXISTS wine_inventory')
    op.execute('DROP TABLE IF EXISTS order_items')
    op.execute('DROP TABLE IF EXISTS orders')
    op.execute('DROP TABLE IF EXISTS notifications')
    op.execute('DROP TABLE IF EXISTS user_notification_preferences')
    op.execute('DROP TABLE IF EXISTS subscriptions')
    op.execute('DROP TABLE IF EXISTS subscription_plans')
    op.execute('DROP TABLE IF EXISTS subscription_transactions')
    op.execute('DROP TABLE IF EXISTS events')
    op.execute('DROP TABLE IF EXISTS event_attendees')
    op.execute('DROP TABLE IF EXISTS community_posts')
    op.execute('DROP TABLE IF EXISTS post_comments')
    op.execute('DROP TABLE IF EXISTS user_connections')
    op.execute('DROP TABLE IF EXISTS wine_cellars')
    op.execute('DROP TABLE IF EXISTS wine_cellar_transactions')
    op.execute('DROP TABLE IF EXISTS wine_courses')
    op.execute('DROP TABLE IF EXISTS course_modules')
    op.execute('DROP TABLE IF EXISTS course_quizzes')
    op.execute('DROP TABLE IF EXISTS quiz_questions')
    op.execute('DROP TABLE IF EXISTS user_course_progress')
    op.execute('DROP TABLE IF EXISTS wine_knowledge_content')
    op.execute('DROP TABLE IF EXISTS wine_content_categories')
    op.execute('DROP TABLE IF EXISTS content_categories')
    op.execute('DROP TABLE IF EXISTS user_content_interactions')
    op.execute('DROP TABLE IF EXISTS model_performance_metrics')
    op.execute('DROP TABLE IF EXISTS model_retraining_logs')

    # Create tables
    op.create_table('wine_traits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=80), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=256), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('preferred_wine_types', sqlite.JSON(), nullable=True),
        sa.Column('is_admin', sa.Boolean(), default=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )

    op.create_table('user_traits',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('trait_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['trait_id'], ['wine_traits.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'trait_id')
    )

    op.create_table('wine_varietals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    op.create_table('wine_regions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    op.create_table('wines',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=True),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('alcohol_percentage', sa.Float(), nullable=True),
        sa.Column('varietal_id', sa.Integer(), nullable=True),
        sa.Column('region_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['region_id'], ['wine_regions.id'], ),
        sa.ForeignKeyConstraint(['varietal_id'], ['wine_varietals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('wine_traits_association',
        sa.Column('wine_id', sa.Integer(), nullable=False),
        sa.Column('trait_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['wine_id'], ['wines.id'], ),
        sa.ForeignKeyConstraint(['trait_id'], ['wine_traits.id'], ),
        sa.PrimaryKeyConstraint('wine_id', 'trait_id')
    )

    op.create_table('user_preference',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('preference_type', sa.String(length=50), nullable=False),
        sa.Column('preference_value', sa.String(length=100), nullable=False),
        sa.Column('preferred_wine_types', sqlite.JSON(), nullable=True),
        sa.Column('preferred_regions', sqlite.JSON(), nullable=True),
        sa.Column('preferred_price_range', sqlite.JSON(), nullable=True),
        sa.Column('flavor_profiles', sqlite.JSON(), nullable=True),
        sa.Column('wine_styles', sqlite.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('wine_reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('wine_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Float(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['wine_id'], ['wines.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('user_wine_interactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('wine_id', sa.Integer(), nullable=False),
        sa.Column('interaction_type', sa.String(length=50), nullable=False),
        sa.Column('interaction_weight', sa.Float(), default=1.0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['wine_id'], ['wines.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('wine_inventory',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('wine_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, default=0),
        sa.Column('min_threshold', sa.Integer(), default=20),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['wine_id'], ['wines.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('wine_id')
    )

    op.create_table('orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=50), default='Pending'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('wine_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.ForeignKeyConstraint(['wine_id'], ['wines.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    # Drop all tables in reverse order
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('wine_inventory')
    op.drop_table('user_wine_interactions')
    op.drop_table('wine_reviews')
    op.drop_table('user_preference')
    op.drop_table('wine_traits_association')
    op.drop_table('wines')
    op.drop_table('wine_regions')
    op.drop_table('wine_varietals')
    op.drop_table('user_traits')
    op.drop_table('users')
    op.drop_table('wine_traits') 