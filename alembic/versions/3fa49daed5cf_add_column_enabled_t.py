"""add column enabled to Customer

Revision ID: 3fa49daed5cf
Revises: 2c6eb11ac2d7
Create Date: 2013-07-05 10:25:47.646022

"""

# revision identifiers, used by Alembic.
revision = '3fa49daed5cf'
down_revision = '2c6eb11ac2d7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("TB_CUSTOMER", sa.Column("enabled", sa.Boolean, server_default='1'))

def downgrade():
    op.drop_column('TB_CUSTOMER', 'enabled')
