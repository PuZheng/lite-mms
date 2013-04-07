"""add is_last to unload task

Revision ID: 51242e27bc6
Revises: d9c0f19bdf3
Create Date: 2013-03-26 11:03:42.724269

"""

# revision identifiers, used by Alembic.
revision = 'd9c0f19bdf7'
down_revision = 'd9c0f19bdf6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("TB_UNLOAD_SESSION",
                 sa.Column("status", sa.Integer, default=1, nullable=False))

def downgrade():
    op.drop_column("TB_UNLOAD_SESSION", "status")
