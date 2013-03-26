# -*- coding: UTF-8 -*-
"""
@author: Yangminghua
@version: $
"""
from pyfeature import (Feature, Scenario, given, and_, when, then, 
                       flask_sqlalchemy_setup, clear_hooks)
from lite_mms.basemain import app
from lite_mms.database import db

def test():
    flask_sqlalchemy_setup(app, db)

    with Feature(u"卸货流程测试", ["lite_mms.test.steps.cargo"]):
        #import lite_mms.test.steps.cargo

        with Scenario(u"新建卸货会话"):
            group = given(u"创建用户组'收发员小组'")
            default_product=and_(u"创建默认产品")
            type = and_(u"创建产品类型'type_1772'")
            product = and_(u"创建产品'product_d123'", product_type=type)
            department = and_(u"创建车间'A'")
            harbor = and_(u"创建装卸点'X'", department=department)
            procedure = and_(u"创建工序'镀锌'", department=department)
            customer = and_(u"创建客户'宁力'")
            password = u"7758258"
            user = and_(u"创建收发员'收发员0638', 密码'%s'" % password, group=group)

            us = when(u"收发员生成新卸货会话,车牌号'浙E D12DA', 毛重'54165'KG",
                      username=user.username, password=password)
            ut = and_(u"装卸工生成新卸货任务", user, us, customer, harbor.name, is_finished=1)
            then(u"生成卸货任务成功", ut)
            ut1 = when(u"装卸工生成新卸货任务", user, us, customer, harbor.name, is_finished=1)
            then(u"生成卸货任务失败", ut1)


        with Scenario(u"收发员更新收货单"):
            us = given(u"创建新卸货会话,车牌号'浙E D12DA', 毛重'54165'KG")
            ut = and_(u"创建卸货任务", user, us, customer, harbor, default_product,
                      weight=5000)
            gr = and_(u"生成收货单", unload_session=us, customer=customer)
            order = and_(u"生成订单", goods_receipt=gr, user=user)
            sub_order = and_(u"生成计重类型的子订单", order=order, product=default_product,
                             weight=ut.weight, harbor=harbor, unload_task=ut)
            and_(u"完善子订单信息", sub_order)
            import random
            weight = random.randint(5000,10000)
            when(u"收发员修改收货单内产品的重量成功", product=product, weight=weight,
                      unload_task=ut, username=user.username,
                      password=password)
            then(u"收货单内产品ID为'%d'的产品重量为'%d'" % (product.id, weight), goods_receipt=gr)
            and_(u"子订单内产品ID为'%d'的产品重量为'%d'" % (product.id, weight), sub_order=sub_order)

            when(u"下发订单", order)
            then(u"收发员修改收货单内产品的重量失败", product=default_product, weight=weight,
                 unload_task=ut, username=user.username, password=password)

    clear_hooks()

if __name__ == "__main__":
    test()
