"""Update candidate status strings

Revision ID: ebca2c5e1bc8
Revises: f87e6febde44
Create Date: 2026-08-20 18:02:56.913632

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ebca2c5e1bc8'
down_revision: Union[str, Sequence[str], None] = 'f87e6febde44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("UPDATE candidates SET status = 'not-started' WHERE status = 'not_started'")
    op.execute("UPDATE candidates SET status = 'on-progress' WHERE status = 'in_progress'")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("UPDATE candidates SET status = 'not_started' WHERE status = 'not-started'")
    op.execute("UPDATE candidates SET status = 'in_progress' WHERE status = 'on-progress'")
