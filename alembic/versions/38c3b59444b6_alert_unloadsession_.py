"""alert unloadsession add with_person

Revision ID: 38c3b59444b6
Revises: 185ce9f63e22
Create Date: 2013-01-28 14:39:58.618228

"""

# revision identifiers, used by Alembic.
revision = '38c3b59444b6'
down_revision = '185ce9f63e22'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("TB_UNLOAD_SESSION", sa.Column("with_person", sa.Boolean, default=False))
    op.add_column("TB_DELIVERY_SESSION", sa.Column("with_person", sa.Boolean, default=False))



def downgrade():
    op.drop_column("TB_UNLOAD_SESSION", "with_person")
    op.drop_column("TB_DELIVERY_SESSION", "with_person")
