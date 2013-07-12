"""add column enabled to User

Revision ID: 430e5c7bc3aa
Revises: 3fa49daed5cf
Create Date: 2013-07-11 16:56:21.183231

"""

# revision identifiers, used by Alembic.
revision = '430e5c7bc3aa'
down_revision = '3fa49daed5cf'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("TB_USER", sa.Column("enabled", sa.Boolean, server_default='1'))

def downgrade():
    op.drop_column('TB_USER', 'enabled')
