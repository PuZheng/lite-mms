# -*- coding: UTF-8 -*-
"""
@author: Yangminghua
@version: $
"""
from pyfeature import Feature, Scenario, given, and_, when, then
from lite_mms.basemain import app
from lite_mms.database import db

def test():
    from pyfeature import flask_sqlalchemy_setup
    flask_sqlalchemy_setup(app, db)
    with Feature(u"搜索功能测试", ['lite_mms.test.steps.search_steps']):

        with Scenario(u"收发员搜索功能测试"):
            group = given(u"创建用户组'收发员小组'")
            and_(u"创建默认产品")
            type = and_(u"创建产品类型'type_1772'")
            product = and_(u"创建产品'product_d123'", product_type=type)
            department = and_(u"创建车间'进口棉'")
            harbor = and_(u"创建装卸点'jkdlnm'", department=department)
            procedure = and_(u"创建工序'一般工序'", department=department)
            customer = and_(u"创建客户'宁力'")
            password = 7758258
            user = and_(u"创建收发员'收发员0638', 密码'%s'" % password, group=group)
            us = and_(u"创建新卸货会话,车牌号'浙E D12DA', 毛重'54165'KG")
            ut = and_(u"创建卸货任务", user, us, customer, harbor, product,
                      weight=5000)
            gr = and_(u"生成收货单", unload_session=us, customer=customer)
            order = and_(u"生成订单", goods_receipt=gr, user=user)
            sub_order = and_(u"生成计重类型的子订单", order=order, product=product,
                             weight=ut.weight, harbor=harbor)
            and_(u"完善子订单信息", sub_order)
            and_(u"下发订单", order)
            wc = and_(u"预排产", sub_order, ut.weight, procedure)

            rv = when(u"收发员登录，搜索'1'", user, password)
            then(u"可以搜索卸货会话信息", us, rv)
            and_(u"可以搜索订单信息", order, rv)
            and_(u"不能搜索工单信息", wc, rv)

    from pyfeature import clear_hooks
    clear_hooks()
