"""add diet_preferences and dislikes to children

Revision ID: 674c55b64816
Revises: b38a3f91bd8e
Create Date: 2026-02-25 08:34:53.967198

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '674c55b64816'
down_revision: Union[str, Sequence[str], None] = 'b38a3f91bd8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("children", sa.Column("diet_preferences", sa.Text(), nullable=True))
    op.add_column("children", sa.Column("dislikes", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("children", "dislikes")
    op.drop_column("children", "diet_preferences")
