#-*- coding:utf-8 -*-

from pyfeature import (Feature, Scenario, given, and_, when, then,
                       flask_sqlalchemy_setup, clear_hooks)
from lite_mms.basemain import app
from lite_mms.database import db

def test():
    flask_sqlalchemy_setup(app, db)
    with Feature(u"发货单相关流程", ["lite_mms.test.steps.consignment_steps"]):
        with Scenario(u"生成发货单"):
            # GIVEN
            pt = given(u'生成产品类型"手机"')
            product = and_(u'生成产品"iphone4"', product_type=pt)
            group = and_(u'创建用户组"调度员"')
            user = and_(u'生成调度员"小明", 密码是xm', group=group)
            department = and_(u'生成车间"A"')
            team = and_(u"生成班组'A0123'", department)
            harbor = and_(u'生成装卸点"X"', department=department)
            procedure = and_(u'生成工序"镀锌"', department=department)
            customer = and_(u'生成客户"宁力"')
            us = and_(u"生成卸货会话, 重量为10000公斤", customer=customer)
            gr = and_(u"生成收货单", customer=customer, unload_session=us)
            order = and_(u"生成订单", goods_receipt=gr, creator=user)
            so = and_(u"生成计件类型的子订单, 重量是10000公斤, 数量是20桶, 规格是20*200, 型号是133", harbor=harbor,
                      order=order, product=product, unit=u"桶")
            wc1 = and_(u"生成工单1, 重量是5000KG", sub_order=so, procedure=procedure, team=team)
            wc2 = and_(u"生成工单2, 重量是5000KG", sub_order=so, procedure=procedure, team=team)
            qir1 = and_(u"对工单1生成质检单1, 结果是全部质检通过", work_command=wc1)
            qir2 = and_(u"对工单2生成质检单2, 结果是全部质检通过", work_command=wc2)
            ds = and_(u'生成发货会话, 车牌号是"浙A 12345", 皮重是2000公斤')
            sb1 = and_(u'根据质检单1生成仓单1, 将其加入发货会话', qir=qir1, delivery_session=ds,
                       harbor=harbor)
            sb2 = and_(u'根据质检单2生成仓单2, 将其加入发货会话', qir=qir2, delivery_session=ds,
                       harbor=harbor)
            dt = and_(u"创建一个发货任务, 选择的仓单全部发货", ds, finished_store_bill_list = [sb1, sb2])
            dt = and_(u"对发货任务进行称重，重量为13000公斤", dt)

            #ASSERT
            consignment = when(u"生成发货单", ds, customer, user.username, password="xm")
            then(u"发货单只有一个产品", consignment, product)
            and_(u"发货单产品重量为两仓单重量之和", consignment, sb1, sb2)
            and_(u"发货单产品的规格是20*200, 型号是133", consignment)
            and_(u"发货单的总重是发货任务的重量", consignment, dt)
            and_(u"发货单产品的数量是20桶", consignment)

        with Scenario(u"修改发货单"):
            weight = 9000
            when(u"修改发货单产品的重量", consignment, weight=weight,
                 username=user.username, password="xm")
            then(u"发货单产品的重量改变", consignment, weight=weight)
            and_(u"发货任务的重量保持不变", consignment, weight=weight)
