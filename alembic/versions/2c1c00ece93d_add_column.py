"""Add Column

Revision ID: 2c1c00ece93d
Revises: None
Create Date: 2013-01-21 16:29:16.970000

"""

# revision identifiers, used by Alembic.
revision = '2c1c00ece93d'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, Integer, ForeignKey

def upgrade():
    op.add_column('TB_SUB_ORDER',
                  Column('team_id', Integer, ForeignKey("TB_TEAM.id")))

def downupgrade():
    pass
