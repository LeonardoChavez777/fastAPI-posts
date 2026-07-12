"""add user table

Revision ID: e19132e320d9
Revises: 5ef51e6b6e7d
Create Date: 2026-07-10 00:48:41.497437

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e19132e320d9'
down_revision: Union[str, Sequence[str], None] = '5ef51e6b6e7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('users',
    sa.Column('Id', sa.Integer(), nullable=False, primary_key=True),
    sa.Column('email', sa.String(), nullable=False, unique=True),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('users')
    pass
