"""move deduction

Revision ID: 185ce9f63e22
Revises: 2ca6fa63fb40
Create Date: 2013-01-24 10:13:04.855000

"""

# revision identifiers, used by Alembic.
revision = '185ce9f63e22'
down_revision = '2ca6fa63fb40'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table("TB_DEDUCTION", sa.Column('id', sa.Integer),
                    sa.Column('weight', sa.Integer),
                    sa.Column('work_command_id', sa.Integer),
                    sa.Column('actor_id', sa.Integer),
                    sa.Column('team_id', sa.Integer, nullable=False),
                    sa.Column('create_time', sa.DateTime),
                    sa.Column('remark', sa.String(256)),
                    sa.ForeignKeyConstraint(['work_command_id'],
                                            ['TB_WORK_COMMAND.id'], ),
                    sa.ForeignKeyConstraint(['actor_id'], ['TB_USER.id'], ),
                    sa.ForeignKeyConstraint(['team_id'], ['TB_TEAM.id'], ),
                    sa.PrimaryKeyConstraint('id'))

    op.execute(
        "INSERT INTO tb_deduction ( weight, work_command_id, team_id, "
        "actor_id, create_time ) SELECT deduction, tb_work_command.id, "
        "tb_work_command.team_id, tb_user.id, NOW() FROM tb_work_command, "
        "tb_user WHERE tb_work_command.deduction > 0 AND tb_user.username = "
        "'qi';commit;")

    op.drop_column("TB_WORK_COMMAND", "deduction")


def downgrade():
    op.add_column("TB_WORK_COMMAND", sa.Column("deduction", sa.Integer))
    op.execute(
        "UPDATE TB_WORK_COMMAND SET TB_WORK_COMMAND.deduction = ( SELECT "
        "weight FROM TB_DEDUCTION WHERE TB_WORK_COMMAND.id = TB_DEDUCTION"
        ".work_command_id); commit;")
    op.drop_table("TB_DEDUCTION")
