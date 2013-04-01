"""add desc to Permission

Revision ID: d9c0f19bdf4
Revises: 4b191d5efa1e
Create Date: 2013-03-28 11:42:39.474538

"""

# revision identifiers, used by Alembic.
revision = 'd9c0f19bdf4'
down_revision = '4b191d5efa1e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("TB_PERMISSION", 
                  sa.Column("desc", sa.String(64), default=""))
    perm_table = sa.sql.table("TB_PERMISSION", 
                              sa.Column("name", sa.String(64), primary_key=True),
                              sa.Column("desc", sa.String(64), default=""))
    conn = op.get_bind()
    from lite_mms.permissions import permissions
    for perm in conn.execute(perm_table.select()):
        desc = permissions[perm.name]["brief"]
        op.execute(perm_table.update().where(perm_table.c.name==perm.name).values(desc=desc)) 

def downgrade():
    op.drop_column("TB_PERMISSION", "desc")
