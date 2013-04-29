"""add TODO table

Revision ID: 18d5259ad2f7
Revises: 335ff300f22b
Create Date: 2013-04-29 19:25:35.921755

"""

# revision identifiers, used by Alembic.
revision = '18d5259ad2f7'
down_revision = '335ff300f22b'

from datetime import datetime
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        "TB_TODO", 
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("TB_USER.id")),
        sa.Column("obj_cls", sa.String(64)),
        sa.Column("obj_pk", sa.String(64)),
        sa.Column("create_time", sa.DateTime, default=datetime.now),
        sa.Column("actor_id", sa.Integer, sa.ForeignKey("TB_USER.id")),
        sa.Column("action", sa.String(64)),
        sa.Column("priority", sa.Integer),
        sa.Column("msg", sa.String(128)))


def downgrade():
    op.drop_table("TB_TODO")
