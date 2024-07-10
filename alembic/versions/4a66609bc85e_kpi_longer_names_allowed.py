"""kpi: longer names allowed

Revision ID: 4a66609bc85e
Revises: 902421b0f9dd
Create Date: 2024-07-08 14:06:23.442181

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a66609bc85e'
down_revision: Union[str, None] = '902421b0f9dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
