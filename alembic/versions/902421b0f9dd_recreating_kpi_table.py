"""recreating kpi table

Revision ID: 902421b0f9dd
Revises: c4a4681bb0d3
Create Date: 2024-07-08 14:03:26.935814

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '902421b0f9dd'
down_revision: Union[str, None] = 'c4a4681bb0d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
