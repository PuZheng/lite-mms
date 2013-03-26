"""order_add_refined

Revision ID: 53c00532a76
Revises: 2a4cf5743519
Create Date: 2013-02-27 16:40:36.958412

"""

# revision identifiers, used by Alembic.
revision = '53c00532a76'
down_revision = '2a4cf5743519'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("TB_ORDER", sa.Column("refined", sa.Boolean, default=False))
    op.execute("update tb_order t set refined=1 where t.dispatched=1; commit;")
    op.execute("INSERT INTO TB_PERMISSION (name)values('deduction.addDeduction')")
    op.execute("INSERT INTO TB_PERMISSION (name)values('deduction.deleteDeduction')")
    op.execute("INSERT INTO TB_PERMISSION (name)values('deduction.editDeduction')")
    op.execute("INSERT INTO TB_PERMISSION_AND_GROUP(permission_name,group_id)VALUES('deduction.addDeduction',4)")
    op.execute("INSERT INTO TB_PERMISSION_AND_GROUP(permission_name,group_id)VALUES('deduction.deleteDeduction',4)")
    op.execute("INSERT INTO TB_PERMISSION_AND_GROUP(permission_name,group_id)VALUES('deduction.editDeduction',4)")

def downgrade():
    op.drop_column("TB_ORDER", "refined")
    op.execute("DELETE FROM TB_PERMISSION_AND_GROUP WHERE permission_name='deduction.addDeduction' and group_id=4")
    op.execute("DELETE FROM TB_PERMISSION_AND_GROUP WHERE permission_name='deduction.deleteDeduction' and group_id=4")
    op.execute("DELETE FROM TB_PERMISSION_AND_GROUP WHERE permission_name='deduction.editDeduction' and group_id=4")
    op.execute("DELETE FROM TB_PERMISSION WHERE name='deduction.addDeduction'")
    op.execute("DELETE FROM TB_PERMISSION WHERE name='deduction.deleteDeduction'")
    op.execute("DELETE FROM TB_PERMISSION WHERE name='deduction.editDeduction'")

