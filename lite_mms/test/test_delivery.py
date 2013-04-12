# -*- coding: utf-8 -*-
"""
发货相关的测试，见ticket 223
"""
from pyfeature import Feature, Scenario, given, and_, when, then
from lite_mms.basemain import app
from lite_mms.database import db

def test():
    # TODO 缺乏对计件类型的发货流程测试
    from pyfeature import flask_sqlalchemy_setup
    flask_sqlalchemy_setup(app, db)
    with Feature("发货流程测试", ["lite_mms.test.steps.delivery"]):
        with Scenario("获取发货会话列表"):
            # GIVEN
            pt = given(u'生成产品类型"手机"')
            product = and_(u'生成产品"iphone4"', product_type=pt)
            group = and_(u'创建用户组"调度员"')
            user = and_(u'生成调度员"小明", 密码是xm', group=group)
            department = and_(u'生成车间"A"')
            team = and_(u"生成班组'f'", department)
            harbor = and_(u'生成装卸点"X"', department=department)
            procedure = and_(u'生成工序"镀锌"', department=department)
            customer = and_(u'生成客户"宁力"')
            us = and_(u"生成卸货会话, 重量为10000公斤", customer=customer)
            gr = and_(u"生成收货单", customer=customer, unload_session=us)
            order = and_(u"生成订单", goods_receipt=gr, creator=user)
            so = and_(u"生成计重类型的子订单, 重量是10000公斤", harbor=harbor,
                      order=order, product=product, unit="KG")
            wc1 = and_(u"生成工单1, 重量是5000KG", sub_order=so, procedure=procedure,
                       team=team)
            wc2 = and_(u"生成工单2, 重量是5000KG", sub_order=so, procedure=procedure,
                       team=team)
            wc3 = and_(u"生成工单3, 重量是5000KG", sub_order=so, procedure=procedure,
                       team=team)
            qir1 = and_(u"对工单1生成质检单1, 结果是全部质检通过", work_command=wc1)
            qir2 = and_(u"对工单2生成质检单2, 结果是全部质检通过", work_command=wc2)
            qir3 = and_(u"对工单3生成质检单3, 结果是全部质检通过", work_command=wc3)
            ds = and_(u'生成发货会话, 车牌号是"浙A 12345", 皮重是2000公斤')
            sb1 = and_(u'根据质检单1生成仓单1, 将其加入发货会话', qir=qir1, delivery_session=ds,
                       harbor=harbor)
            sb2 = and_(u'根据质检单2生成仓单2, 将其加入发货会话', qir=qir2, delivery_session=ds,
                       harbor=harbor)
            sb3 = and_(u'根据质检单3生成仓单3, 将其加入发货会话', qir=qir3, delivery_session=ds,
                       harbor=harbor)

            # ASSERTIONS
            ds_dict = then(u'可以获得发货会话, 其车牌号是"浙A 12345", 皮重是2000公斤',
                           delivery_session=ds)
            and_(u'该发货会话没有锁定', delivery_session=ds)
            and_(u'该发货会话下有三个仓单, 正是之前创建的三个仓单', delivery_session_dict=ds_dict,
                 store_bill_list=[sb1, sb2, sb3], order=order, sub_order=so)
            dt_id, new_sb_id = when(
                u'创建一个发货任务, 该发货任务试图按顺序完成上述三个仓单, 车辆已经装满, 但是仍然剩余了1000公斤',
                delivery_session=ds, store_bills=[sb1, sb2, sb3])
            new_sb = then(u"生成了一个新的仓单", new_sb_id)
            then(u'该发货任务包含仓单1, 2和新发货任务', dt_id, store_bills=[sb1, sb2, new_sb])
            and_(u"新仓单的状态是完成", store_bill=new_sb)
            and_(u"新仓单的质检报告仍然是质检报告1", store_bill=new_sb, qir=qir3)
            and_(u"新仓单的重量是4000公斤", store_bill=new_sb)
            and_(u"新仓单已经被打印过", store_bill=new_sb)
            and_(u"新仓单的发货会话是原发货会话", store_bill=new_sb, delivery_session=ds)
            and_(u"仓单3的重量是1000公斤", store_bill=sb3)
            and_(u"仓单3的质检报告仍然是质检报告1", store_bill=sb3, qir=qir3)
            and_(u"仓单3的状态是未完成", store_bill=sb3)
            and_(u"仓单1的重量是5000公斤", store_bill=sb1)
            and_(u"仓单1的状态是完成", store_bill=sb1)
            and_(u"仓单2的重量是5000公斤", store_bill=sb2)
            and_(u"仓单2的状态是完成", store_bill=sb2)

            when(u"该发货任务称重为30000公斤", delivery_task_id=dt_id,
                 user=user) # 那么其实本次发货任务的重量是30000 - 2000 = 28000
            then(u"仓单1的重量是10000公斤", store_bill=sb1)
            and_(u"仓单2的重量是10000公斤", store_bill=sb2)
            and_(u"新仓单的重量是8000公斤", store_bill=new_sb)

        with Scenario(u"生成发货单"):
            consignment = given(u"生成发货单, 未导入原系统", delivery_session=ds,
                                customer=customer, user=user)
            import random

            weight = random.randint(30000, 35000)
            when(u"修改发货单", consignment=consignment, weight=weight, user=user)
            then(u"发货单中产品的重量已修改", consignment=consignment, weight=weight)

            when(u"发货单导入原系统", consignment=consignment)
            then(u"修改发货单失败", consignment=consignment,
                 weight=random.randint(30000, 35000), user=user)
        
    from pyfeature import clear_hooks
    clear_hooks()

if __name__ == "__main__":
    test()
