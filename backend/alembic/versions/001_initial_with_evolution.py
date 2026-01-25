"""Initial migration with Evolution API support

Revision ID: 001_initial
Revises:
Create Date: 2025-01-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Evolution Instances table
    op.create_table(
        'evolution_instances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('instance_name', sa.String(100), nullable=True),
        sa.Column('status', sa.String(50), default='disconnected'),
        sa.Column('qr_code', sa.Text(), nullable=True),
        sa.Column('qr_code_updated_at', sa.DateTime(), nullable=True),
        sa.Column('phone_number', sa.String(50), nullable=True),
        sa.Column('profile_name', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_connected_at', sa.DateTime(), nullable=True),
        sa.Column('raw_data', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_evolution_instances_id', 'evolution_instances', ['id'])
    op.create_index('ix_evolution_instances_instance_name', 'evolution_instances', ['instance_name'], unique=True)

    # Contacts table
    op.create_table(
        'contacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('wa_id', sa.String(50), nullable=True),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('profile_name', sa.String(255), nullable=True),
        sa.Column('evolution_remote_jid', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_contacts_id', 'contacts', ['id'])
    op.create_index('ix_contacts_wa_id', 'contacts', ['wa_id'])
    op.create_index('ix_contacts_user_id', 'contacts', ['user_id'])
    op.create_index('ix_contacts_evolution_remote_jid', 'contacts', ['evolution_remote_jid'])

    # Conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('last_message_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_conversations_id', 'conversations', ['id'])

    # Messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('wa_message_id', sa.String(255), nullable=True),
        sa.Column('contact_id', sa.Integer(), nullable=True),
        sa.Column('conversation_id', sa.Integer(), nullable=True),
        sa.Column('evolution_key_id', sa.String(255), nullable=True),
        sa.Column('source', sa.String(50), default='cloud_api'),
        sa.Column('message_type', sa.String(50), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('media_url', sa.String(500), nullable=True),
        sa.Column('media_id', sa.String(255), nullable=True),
        sa.Column('is_outbound', sa.Boolean(), default=False),
        sa.Column('status', sa.String(50), default='received'),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('raw_data', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id']),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_messages_id', 'messages', ['id'])
    op.create_index('ix_messages_wa_message_id', 'messages', ['wa_message_id'])
    op.create_index('ix_messages_user_id', 'messages', ['user_id'])
    op.create_index('ix_messages_evolution_key_id', 'messages', ['evolution_key_id'], unique=True)


def downgrade() -> None:
    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('contacts')
    op.drop_table('evolution_instances')
    op.drop_table('users')
