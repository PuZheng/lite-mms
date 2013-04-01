"""add completed_time to work_command

Revision ID: d9c0f19bdf5
Revises: d9c0f19bdf4
Create Date: 2013-03-31 11:31:57.969339

"""

# revision identifiers, used by Alembic.
revision = 'd9c0f19bdf5'
down_revision = 'd9c0f19bdf4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("TB_WORK_COMMAND", 
                  sa.Column("completed_time", sa.DateTime, doc=u"生产完毕的时间"),
                 )


def downgrade():
    op.drop_column("TB_WORK_COMMAND", "completed_time")
