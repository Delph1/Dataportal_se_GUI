"""trying to update description length0

Revision ID: c4a4681bb0d3
Revises: f7a3497ac1a3
Create Date: 2024-07-08 13:43:40.421011

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4a4681bb0d3'
down_revision: Union[str, None] = 'f7a3497ac1a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
