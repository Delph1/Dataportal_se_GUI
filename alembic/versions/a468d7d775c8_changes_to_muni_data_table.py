"""changes to muni data table

Revision ID: a468d7d775c8
Revises: 4a66609bc85e
Create Date: 2024-07-09 15:48:17.078262

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a468d7d775c8'
down_revision: Union[str, None] = '4a66609bc85e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
