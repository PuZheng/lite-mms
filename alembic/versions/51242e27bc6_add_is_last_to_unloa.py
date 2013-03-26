"""add is_last to unload task

Revision ID: 51242e27bc6
Revises: d9c0f19bdf3
Create Date: 2013-03-26 11:03:42.724269

"""

# revision identifiers, used by Alembic.
revision = '51242e27bc6'
down_revision = 'd9c0f19bdf3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("TB_UNLOAD_TASK", 
                 sa.Column("is_last", sa.Boolean, default=False))

def downgrade():
    op.drop_column("TB_UNLOAD_TASK", "is_last")
