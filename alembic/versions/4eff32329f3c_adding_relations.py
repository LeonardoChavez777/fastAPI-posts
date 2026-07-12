"""adding relations

Revision ID: 4eff32329f3c
Revises: e19132e320d9
Create Date: 2026-07-10 01:12:11.191547

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4eff32329f3c'
down_revision: Union[str, Sequence[str], None] = 'e19132e320d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('owner_id', sa.Integer(), nullable=False))
    op.create_foreign_key('posts_owner_id_fkey', 'posts', 'users', ['owner_id'], ['Id'], ondelete='CASCADE')
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('posts_owner_id_fkey', 'posts', type_='foreignkey')
    op.drop_column('posts', 'owner_id')
    pass
