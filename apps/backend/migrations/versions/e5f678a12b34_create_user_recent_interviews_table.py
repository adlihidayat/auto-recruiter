"""Create user_recent_interviews table

Revision ID: e5f678a12b34
Revises: d7f532b99c21
Create Date: 2026-08-31 22:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f678a12b34'
down_revision: Union[str, Sequence[str], None] = 'd7f532b99c21'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'user_recent_interviews',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('interview_id', sa.UUID(), nullable=False),
        sa.Column('viewed_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['interview_id'], ['interviews.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'interview_id', name='uq_user_interview_recent')
    )
    op.create_index(op.f('ix_user_recent_interviews_interview_id'), 'user_recent_interviews', ['interview_id'], unique=False)
    op.create_index(op.f('ix_user_recent_interviews_user_id'), 'user_recent_interviews', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_user_recent_interviews_user_id'), table_name='user_recent_interviews')
    op.drop_index(op.f('ix_user_recent_interviews_interview_id'), table_name='user_recent_interviews')
    op.drop_table('user_recent_interviews')
