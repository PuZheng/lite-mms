"""reset default url for admin group

Revision ID: d9c0f19bdf5 
Revises: d9c0f19bdf5
Create Date: 2013-04-01 16:49:52.141337

"""

# revision identifiers, used by Alembic.
revision = 'd9c0f19bdf6'
down_revision = 'd9c0f19bdf5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    from lite_mms.constants import groups
    group_table = sa.sql.table("TB_GROUP", 
                 sa.Column("id", sa.Integer, primary_key=True),
                 sa.Column("name", sa.String(32), nullable=False, unique=True),
                 sa.Column("default_url", sa.String(256)))
    op.execute(group_table.update().where(group_table.c.id==groups.ADMINISTRATOR).values(default_url="/admin2/"))

def downgrade():
    from lite_mms.constants import groups
    group_table = sa.sql.table("TB_GROUP", 
                 sa.Column("id", sa.Integer, primary_key=True),
                 sa.Column("name", sa.String(32), nullable=False, unique=True),
                 sa.Column("default_url", sa.String(256)))
    op.execute(group_table.update().where(group_table.c.id==groups.ADMINISTRATOR).values(default_url="/admin/"))
