"""update returned_weight

Revision ID: 196b293a6da2
Revises: 53c00532a76
Create Date: 2013-03-11 10:09:46.289000

"""

# revision identifiers, used by Alembic.
revision = '196b293a6da2'
down_revision = '53c00532a76'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("TB_DELIVERY_TASK", sa.Column("returned_weight", sa.Integer))
    op.execute("UPDATE TB_DELIVERY_TASK T SET T.RETURNED_WEIGHT = ( SELECT SUM(S.WEIGHT) FROM TB_STORE_BILL S, TB_SUB_ORDER O WHERE S.SUB_ORDER_ID = O.ID AND O.RETURNED = 1 AND S.DELIVERY_TASK_ID = T.ID GROUP BY T.ID ); COMMIT;")
    op.execute("UPDATE TB_DELIVERY_TASK T SET T.RETURNED_WEIGHT = 0 WHERE T.RETURNED_WEIGHT IS NULL; COMMIT;")


def downgrade():
    op.drop_column("TB_DELIVERY_TASK", "returned_weight")
