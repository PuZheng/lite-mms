# -*- coding: UTF-8 -*-
from pyfeature import Feature, Scenario, given, and_, when, then
from lite_mms.basemain import app
from lite_mms.database import db

def test():

    from pyfeature import flask_sqlalchemy_setup
    flask_sqlalchemy_setup(app, db)
    with Feature("调度流程(计重类型)测试", ['lite_mms.test.steps.schedule']):
        with Scenario("获取订单列表(计重类型)"):
            # GIVEN
            department = given(u'创建一个车间富士康')
            harbor = and_(u"创建一个装卸点A", department)
            order, cargo_clerk = and_(u'创建一个订单, 毛重是10000公斤, 客户是宁力')
            product_type = and_(u'创建一个产品类型紧固件')
            sub_order1 = and_(u'创建一个计重子订单, 重量是10000公斤, 产品是螺丝', 
                              order, department, product_type, harbor)
            sub_order2 = and_(u'创建一个计重子订单, 重量是20000公斤, 产品是螺母', 
                              order, department, product_type, harbor)
            scheduler = and_(u'创建一个调度员') 
            then(u"订单列表为空")
            when(u'完善子订单', sub_order1)
            and_(u'完善子订单', sub_order2)
            and_(u"将订单下发", order)
            and_(u'订单的生产中重量是0公斤', order)
            then(u"订单列表中包含此订单", order, scheduler)
            and_(u"可以获取一个计重类型的订单, 这个订单有两个子订单", order, scheduler)
        with Scenario("对计重类型的子订单进行预排产"):
            procedure = given(u'创建一个工序抛砂', department)
            when(u'对子订单1进行预排产5000公斤', sub_order1, procedure)
            then(u'子订单1未预排产的重量是5000公斤', sub_order1)
            and_(u'子订单1生产中的重量是5000公斤', sub_order1)
            and_(u'生成了新工单, 这个工单的状态是待排产, 重量5000公斤', sub_order1, procedure)

            when(u'对子订单2进行预排产3000公斤', sub_order2, procedure)
            then(u'子订单2未预排产的重量是17000公斤', sub_order2)
            and_(u'子订单2生产中的重量是3000公斤', sub_order2)

            and_(u'订单未预排产重量是22000公斤', order)
            and_(u'订单的生产中重量是8000公斤', order)
        
    with Feature("调度流程(计件类型)测试", ['lite_mms.test.steps.schedule']):
        with Scenario("获取订单列表(计件类型)"):
            # GIVEN
            department = given(u'创建一个车间富士康')
            harbor = and_(u"创建一个装卸点A", department)
            order, cargo_clerk = and_(u'创建一个订单, 毛重是10000公斤, 客户是宁力')
            product_type = and_(u'创建一个产品类型紧固件')
            scheduler = and_(u'创建一个调度员') 
            then(u"订单列表为空")
            sub_order1 = and_(u'创建一个计件子订单, 重量是10000公斤, 个数是100, 单位是桶, 产品是螺丝', 
                              order, department, product_type, harbor)
            sub_order2 = and_(u'创建一个计件子订单, 重量是20000公斤, 个数是40, 单位是箱, 产品是螺母', 
                              order, department, product_type, harbor)
            when(u'完善子订单', sub_order1)
            and_(u'完善子订单', sub_order2)
            and_(u"将订单下发", order)
            then(u"订单列表中包含此订单", order, scheduler)
            and_(u"可以获取一个计件类型的订单, 这个订单有两个子订单", order, scheduler)
        with Scenario("对计件类型子订单进行预排产"):
            procedure = given(u'创建一个工序抛砂', department)
            when(u'对子订单1进行预排产20件', sub_order1, procedure)
            then(u'子订单1未预排产的数量是80件, 重量是8000公斤', sub_order1)
            and_(u'子订单1生产中的数量是20件, 重量是2000公斤', sub_order1)
            and_(u'生成了新工单, 这个工单的状态是待排产, 数量是20件, 重量2000公斤', sub_order1, procedure)

            when(u'对子订单2进行预排产10件', sub_order2, procedure)
            then(u'子订单2未预排产的数量是30件, 重量是15000公斤', sub_order2)
            and_(u'子订单2生产中的数量是10件, 重量是5000公斤', sub_order2)

            and_(u'订单未预排产重量是23000公斤', order)
            and_(u'订单的生产中重量是7000公斤', order)

    from pyfeature import clear_hooks
    clear_hooks()


if __name__ == "__main__":
    test() 
