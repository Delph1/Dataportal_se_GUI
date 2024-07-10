"""changes to kpi table, operating area extended to 255

Revision ID: 9b9b5b354585
Revises: 1234f304bf69
Create Date: 2024-07-08 12:45:40.660289

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b9b5b354585'
down_revision: Union[str, None] = '1234f304bf69'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
