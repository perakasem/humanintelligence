"""Initial schema

Revision ID: 001
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('google_sub', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('picture', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_google_sub', 'users', ['google_sub'], unique=True)

    # Create spending_snapshots table
    op.create_table(
        'spending_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        # ML Input Features
        sa.Column('age', sa.Integer(), nullable=False),
        sa.Column('gender', sa.Integer(), nullable=False),
        sa.Column('year_in_school', sa.Integer(), nullable=False),
        sa.Column('major', sa.Integer(), nullable=False),
        sa.Column('monthly_income', sa.Integer(), nullable=False),
        sa.Column('financial_aid', sa.Integer(), nullable=False),
        sa.Column('tuition', sa.Integer(), nullable=False),
        sa.Column('housing', sa.Integer(), nullable=False),
        sa.Column('food', sa.Integer(), nullable=False),
        sa.Column('transportation', sa.Integer(), nullable=False),
        sa.Column('books_supplies', sa.Integer(), nullable=False),
        sa.Column('entertainment', sa.Integer(), nullable=False),
        sa.Column('personal_care', sa.Integer(), nullable=False),
        sa.Column('technology', sa.Integer(), nullable=False),
        sa.Column('health_wellness', sa.Integer(), nullable=False),
        sa.Column('miscellaneous', sa.Integer(), nullable=False),
        sa.Column('preferred_payment_method', sa.Integer(), nullable=False),
        # ML Outputs
        sa.Column('overspending_prob', sa.Float(), nullable=True),
        sa.Column('financial_stress_prob', sa.Float(), nullable=True),
        # Summary cache
        sa.Column('summary', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        # Timestamp
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_spending_snapshots_user_id', 'spending_snapshots', ['user_id'])

    # Create teacher_interactions table
    op.create_table(
        'teacher_interactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('snapshot_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_message', sa.Text(), nullable=False),
        sa.Column('teacher_response', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['snapshot_id'], ['spending_snapshots.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_teacher_interactions_user_id', 'teacher_interactions', ['user_id'])


def downgrade() -> None:
    op.drop_table('teacher_interactions')
    op.drop_table('spending_snapshots')
    op.drop_table('users')
