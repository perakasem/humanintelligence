"""Add profile fields to user

Revision ID: 002
Revises: 001
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add profile fields to users table
    op.add_column('users', sa.Column('age', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('gender', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('year_in_school', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('major', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('preferred_payment_method', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'preferred_payment_method')
    op.drop_column('users', 'major')
    op.drop_column('users', 'year_in_school')
    op.drop_column('users', 'gender')
    op.drop_column('users', 'age')
