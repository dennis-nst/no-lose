"""Add chats_count to evolution_instances

Revision ID: 002_add_chats_count
Revises: 001_initial
Create Date: 2026-02-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '002_add_chats_count'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('evolution_instances', sa.Column('chats_count', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('evolution_instances', 'chats_count')
