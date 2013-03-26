"""qi_group add permissions

Revision ID: 41614d172256
Revises: 38c3b59444b6
Create Date: 2013-01-28 16:52:57.668206

"""

# revision identifiers, used by Alembic.
revision = '41614d172256'
down_revision = '38c3b59444b6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute(
        "insert into TB_PERMISSION_AND_GROUP(permission_name, group_id)(select TB_PERMISSION.name, "
        "TB_GROUP.id from TB_PERMISSION,TB_GROUP where TB_PERMISSION.name like '%view_work_command' and TB_GROUP.name"
        " ='quality_inspector' )"
    )


def downgrade():
    op.execute(
        "delete from TB_PERMISSION_AND_GROUP where group_id in (select id from TB_GROUP where "
        "name='quality_inspector') and permission_name like '%view_work_command'"
    )
