"""let the default url of accountant point to new congignment list

Revision ID: 35979bf471d6
Revises: 18d5259ad2f7
Create Date: 2013-05-03 18:45:20.162994

"""

# revision identifiers, used by Alembic.
revision = '35979bf471d6'
down_revision = '18d5259ad2f7'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

from lite_mms.constants import groups
group_table = table(
    "TB_GROUP",
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("name", sa.String(32), nullable=False, unique=True),
    sa.Column("default_url", sa.String(256))
)

def upgrade():
    op.execute(group_table.update().where(group_table.c.id==groups.ACCOUNTANT).values({"default_url": "/consignment/consignment-list?order_by=create_time&desc=1&customer=1"}))

def downgrade():
    op.execute(group_table.update().where(group_table.c.id==groups.ACCOUNTANT).values({"default_url": "/delivery/consignment-list"}))
