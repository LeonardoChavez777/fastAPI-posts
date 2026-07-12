"""create post table

Revision ID: 70758407282c
Revises: 
Create Date: 2026-07-10 00:29:18.640990

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '70758407282c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('posts',
    sa.Column('Id', sa.Integer(), nullable=False, primary_key=True),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('content', sa.String(), nullable=False),
    sa.Column('published', sa.Boolean(), nullable=False, server_default='TRUE'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('posts')
