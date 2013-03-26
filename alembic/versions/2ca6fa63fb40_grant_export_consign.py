# -*- coding: UTF-8 -*-

"""grant export_consignment permission to account

Revision ID: 2ca6fa63fb40
Revises: 2f9253b0fa2d
Create Date: 2013-01-22 18:30:26.463733

"""

# revision identifiers, used by Alembic.
revision = '2ca6fa63fb40'
down_revision = '2f9253b0fa2d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # 增加权限data.export_consignment
    from lite_mms.models import Permission
    t = Permission.__table__
    op.bulk_insert(t, [{"name": "data.export_consignment"}])
    # 将权限赋予组accountant
    from lite_mms.models import permission_and_group_table as t
    import lite_mms.constants as constants
    op.bulk_insert(t, [{"permission_name": "data.export_consignment", "group_id": constants.groups.ACCOUNTANT}])

def downgrade():
    # 将权限从组accountant中删除
    from lite_mms.models import permission_and_group_table as t
    op.execute(t.delete().where(t.c.permission_name=="data.export_consignment"))
    # 删除权限data.export_consignment
    from lite_mms.models import Permission
    t = Permission.__table__
    op.execute(t.delete().where(t.c.name=="data.export_consignment"))
    

