# -*- coding: UTF-8 -*-"""add Config TableRevision ID: 318cae8ec27eRevises: d9c0f19bdf7Create Date: 2013-04-15 18:01:54.714000"""# revision identifiers, used by Alembic.revision = '318cae8ec27e'down_revision = 'd9c0f19bdf7'from alembic import opimport sqlalchemy as sadef upgrade():    op.create_table("TB_CONFIG", sa.Column("id", sa.Integer, primary_key=True),                    sa.Column("property_name", sa.String(64), nullable=False),                    sa.Column("property_desc", sa.String(64)),                    sa.Column("property_value", sa.String(64), nullable=False))    op.execute(u"INSERT INTO TB_CONFIG VALUES (1, 'print_count_per_page', '打印时展示的每页产品数', '5');")def downgrade():    op.drop_table("TB_CONFIG")