"""remove the printed column of TB_Consignment

Revision ID: 2a4cf5743519
Revises: 41614d172256
Create Date: 2013-02-26 10:28:22.937000

"""

# revision identifiers, used by Alembic.
revision = '2a4cf5743519'
down_revision = '41614d172256'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column("TB_CONSIGNMENT", "PRINTED")

def downgrade():
    op.add_column("TB_CONSIGNMENT", "PRINTED")
