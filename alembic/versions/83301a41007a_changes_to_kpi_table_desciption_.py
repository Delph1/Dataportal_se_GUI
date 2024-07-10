"""changes to kpi table, desciption extended to 255

Revision ID: 83301a41007a
Revises: 9b9b5b354585
Create Date: 2024-07-08 12:48:30.528424

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '83301a41007a'
down_revision: Union[str, None] = '9b9b5b354585'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
