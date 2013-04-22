"""add spec_type

Revision ID: 4bc13c7caa37
Revises: 196b293a6da2
Create Date: 2013-03-12 11:44:10.906000

"""

# revision identifiers, used by Alembic.
revision = '4bc13c7caa37'
down_revision = '196b293a6da2'

from alembic import op
from sqlalchemy import Column,Integer,String,ForeignKey


def upgrade():
    from lite_mms.models import ConsignmentProduct

    op.create_table(ConsignmentProduct.__tablename__,
                    Column('id', Integer(), primary_key=True, nullable=False),
                    Column('consignment_id', Integer(),
                           ForeignKey('TB_CONSIGNMENT.id'), nullable=False),
                    Column('product_id', Integer(),
                           ForeignKey('TB_PRODUCT.id'), nullable=False),
                    Column('delivery_task_id', Integer(),
                           ForeignKey('TB_DELIVERY_TASK.id'), nullable=False),
                    Column('weight', Integer()),
                    Column('quantity', Integer()),
                    Column('unit', String(length=16), default=''),
                    Column('spec', String(length=64)),
                    Column('type', String(length=64)),
                    Column('returned_weight', Integer()),
                    Column('team_id', Integer(), ForeignKey('TB_TEAM.id'),
                           nullable=False))

    from lite_mms.utilities import do_commit
    from lite_mms.apis.delivery import get_delivery_session_list
    delivery_session_list = get_delivery_session_list()[0]
    for delivery_session in delivery_session_list:
        for consignment in delivery_session.consignment_list:
            for t in delivery_session.delivery_task_list:
                if t.customer:
                    if t.customer.id == consignment.customer_id:
                        p = ConsignmentProduct(t.product, t, consignment)
                        if t.team_list:
                            p.team = t.team_list[0]
                        p.weight = t.weight
                        p.returned_weight = t.returned_weight
                        if not t.quantity:
                            t.quantity = sum(
                                store_bill.quantity for store_bill in
                                t.store_bill_list)
                        p.quantity = t.quantity
                        sb = t.sub_order_list.next()
                        p.unit = sb.unit
                        p.spec = sb.spec
                        p.type = sb.type
                        do_commit((p, t))
                else:
                    do_commit(t, "delete")

def downgrade():
    from lite_mms.models import ConsignmentProduct
    op.drop_table(ConsignmentProduct.__tablename__)