"""Add icon to interviews

Revision ID: d7f532b99c21
Revises: c9e421a88b10
Create Date: 2026-08-31 20:23:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7f532b99c21'
down_revision: Union[str, Sequence[str], None] = 'c9e421a88b10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('interviews', sa.Column('icon', sa.String(length=50), nullable=True))
    op.execute("UPDATE interviews SET icon = '💼' WHERE icon IS NULL")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('interviews', 'icon')
