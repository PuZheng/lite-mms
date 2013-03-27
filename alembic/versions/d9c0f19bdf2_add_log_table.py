"""add log table

Revision ID: d9c0f19bdf2
Revises: 4bc13c7caa37
Create Date: 2013-03-20 09:42:40.802000

"""

# revision identifiers, used by Alembic.
revision = 'd9c0f19bdf2'
down_revision = '4bc13c7caa37'

from datetime import datetime
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table("TB_LOG",
                    sa.Column("id", sa.Integer, primary_key=True),
                    sa.Column("actor_id", sa.Integer, sa.ForeignKey("TB_USER.id")),
                    sa.Column("obj_cls", sa.String(64), nullable=False),
                    sa.Column("obj_pk", sa.String(64), nullable=False),
                    sa.Column("obj", sa.String(64), nullable=False),
                    sa.Column("action", sa.String(64), nullable=False),
                    sa.Column("create_time", sa.DateTime, default=datetime.now),
                    sa.Column("name", sa.String(64)),
                    sa.Column("level", sa.String(64)),
                    sa.Column("module", sa.String(64)),
                    sa.Column("func_name", sa.String(64)),
                    sa.Column("line_no", sa.Integer),
                    sa.Column("thread", sa.Integer),
                    sa.Column("thread_name", sa.String(64)),
                    sa.Column("process", sa.Integer),
                    sa.Column("message", sa.String(64)),
                    sa.Column("args", sa.String(64)),
                    sa.Column("extra", sa.String(64)))


def downgrade():
    op.drop_table("TB_LOG")
