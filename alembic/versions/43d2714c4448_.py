"""empty message

Revision ID: 43d2714c4448
Revises: 2dda2c7c7e83
Create Date: 2013-09-21 20:43:41.755716

"""

# revision identifiers, used by Alembic.
revision = '43d2714c4448'
down_revision = '26777e9808c2'

from alembic import op
import sqlalchemy as sa


def upgrade():

    # create model Node
    op.create_table("TB_NODE", 
                    sa.Column('id', sa.Integer),
                    sa.Column('work_flow_id', sa.Integer),
                    sa.Column('name', sa.String(64)),
                    sa.Column('approved', sa.Boolean),
                    sa.Column('failed', sa.Boolean),
                    sa.Column('create_time', sa.DateTime),
                    sa.Column('handle_time', sa.DateTime),
                    sa.Column('policy_name', sa.String(64)),
                    sa.Column('tag', sa.String(32)),
                    sa.Column('handler_group_id', sa.Integer),
                    sa.ForeignKeyConstraint(['handler_group_id'], ['TB_GROUP.id']),
                    sa.PrimaryKeyConstraint('id'))

    # create model WorkFlow
    op.create_table('TB_WORK_FLOW',
                    sa.Column('id', sa.Integer),
                    sa.Column('tag', sa.String(32)),
                    sa.Column('annotation', sa.String(64)),
                    sa.Column('status', sa.Integer),
                    sa.Column('failed', sa.Boolean),
                    sa.Column('root_node_id', sa.Integer),
                    sa.Column('current_node_id', sa.Integer),
                    sa.Column('token', sa.String(32)),
                    sa.ForeignKeyConstraint(['root_node_id'], ['TB_NODE.id']),
                    sa.ForeignKeyConstraint(['current_node_id'], ['TB_NODE.id']),
                    sa.PrimaryKeyConstraint('id'))

    op.create_foreign_key('fk_work_flow_node', 
                          'TB_NODE',
                          'TB_WORK_FLOW',
                          ['work_flow_id'],
                          ['id'])

def downgrade():
    op.drop_constraint('fk_work_flow_node', "TB_NODE", 'foreignkey')
    op.drop_table("TB_WORK_FLOW")
    op.drop_table("TB_NODE")
