"""add column 'status' to delivery tableRevision ID: 56765d423498Revises: 35979bf471d6Create Date: 2013-05-21 09:27:20.960000"""# revision identifiers, used by Alembic.revision = '56765d423498'down_revision = '35979bf471d6'from alembic import opimport sqlalchemy as sadef upgrade():    op.add_column("TB_DELIVERY_SESSION", sa.Column("status", sa.Integer, default=1, nullable=False))    op.execute("UPDATE TB_DELIVERY_SESSION SET STATUS = 3")def downgrade():    op.drop_column("TB_DELIVERY_SESSION", "status")