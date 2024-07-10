"""just trying to see if some changes didn't go through

Revision ID: f7a3497ac1a3
Revises: 83301a41007a
Create Date: 2024-07-08 13:02:50.122793

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7a3497ac1a3'
down_revision: Union[str, None] = '83301a41007a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
