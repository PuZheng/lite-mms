"""table TB_CONSIGNMENT add column MSSQL_ID

Revision ID: 2f9253b0fa2d
Revises: None
Create Date: 2013-01-22 16:32:31.080000

"""

# revision identifiers, used by Alembic.
revision = '2f9253b0fa2d'
down_revision = '2c1c00ece93d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, Integer


def upgrade():
    op.add_column("TB_CONSIGNMENT", Column("MSSQL_ID", Integer))


def downgrade():
    op.drop_column("TB_CONSIGNMENT", "MSSQL_ID")
