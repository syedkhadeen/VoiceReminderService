"""Initial migration - create users, reminders, and call_logs tables

Revision ID: 001
Revises: 
Create Date: 2024-12-09

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
    # Create reminder_status enum type
    reminder_status = postgresql.ENUM(
        'scheduled', 'processing', 'called', 'failed',
        name='reminder_status'
    )
    # reminder_status.create(op.get_bind()) handled by create_table
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    
    # Create reminders table
    op.create_table(
        'reminders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('phone_number', sa.String(20), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(), nullable=False),
        sa.Column('status', reminder_status, nullable=False, server_default='scheduled'),
        sa.Column('external_call_id', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_reminders_user_id', 'reminders', ['user_id'])
    op.create_index('ix_reminders_scheduled_at', 'reminders', ['scheduled_at'])
    op.create_index('ix_reminders_status_scheduled_at', 'reminders', ['status', 'scheduled_at'])
    
    # Create call_logs table
    op.create_table(
        'call_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('reminder_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('reminders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('external_call_id', sa.String(255), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('transcript', sa.Text(), nullable=True),
        sa.Column('received_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_call_logs_reminder_id', 'call_logs', ['reminder_id'])
    op.create_index('ix_call_logs_external_call_id', 'call_logs', ['external_call_id'])
    op.create_index('ix_call_logs_external_call_id_status', 'call_logs', ['external_call_id', 'status'])


def downgrade() -> None:
    op.drop_table('call_logs')
    op.drop_table('reminders')
    op.drop_table('users')
    
    # Drop enum type
    op.execute('DROP TYPE reminder_status')
