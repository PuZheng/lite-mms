#-*- coding:utf-8 -*-
from lite_mms import constants
from pyfeature import Feature, Scenario, given, when, and_, then, flask_sqlalchemy_setup

from lite_mms.basemain import app
from lite_mms.database import db


def generate(times=1):
    from random import choice
    import string

    temp = ""
    for i in range(times):
        temp += choice(string.letters)
    return temp


def test():
    flask_sqlalchemy_setup(app, db, create_step_prefix=u"创建",
                           model_name_getter=lambda model: model.__name__,
                           attr_name_getter=lambda model, attr: model.__col_desc__.get(attr, attr),
                           set_step_pattern=u'(\w+)([\.\w+]+)设置为(.+)')
    with Feature(u"发货会话测试", step_files=["lite_mms.test.at.steps.delivery"]):
        with Scenario(u"准备数据"):
            plate = given(u"创建Plate", name=generate(5))
            product_type_default = and_(u"创建ProductType", name=constants.DEFAULT_PRODUCT_TYPE_NAME)
            product_default = and_(u"创建Product", name=constants.DEFAULT_PRODUCT_NAME,
                                   product_type=product_type_default)
            and_(u"创建User", username="cc", password="cc")
            customer = and_(u"创建Customer", name=generate(5), abbr=generate(2))
            department = and_(u"创建Department", name=generate(5))
            harbor = and_(u"创建Harbor", name=generate(5), department=department)
            store_bill1 = and_(u"生成StoreBill", customer, harbor=harbor)
            store_bill2 = and_(u"生成StoreBill", customer, harbor=harbor)

        with Scenario(u"创建发货会话，并生成发货单"):
            delivery_session = when(u"收发员创建发货会话", plate=plate, tare=1500)
            then(u"收发员选择仓单", delivery_session, [store_bill1, store_bill2])
            and_(u"装卸工全部装货、完全装货", delivery_session, store_bill1)
            consignment = and_(u"收发员生成发货单", delivery_session)
            then(u"发货单产品与仓单相同", consignment, store_bill1)

        with Scenario(u"修改发货会话"):
            delivery_session = given(u"已关闭的发货会话", plate, tare=1000)
            status_code = when(u"修改发货会话", delivery_session)
            then(u"无法修改", status_code)
            when(u"重新打开发货会话", delivery_session)
            status_code = and_(u"修改发货会话", delivery_session)
            then(u"修改成功", status_code)

        with Scenario(u"修改发货任务"):
            delivery_session = given(u"已关闭的发货会话", plate, tare=1000)
            delivery_task = and_(u"发货任务", delivery_session)
            status_code = when(u"修改发货任务", delivery_task)
            then(u"无法修改", status_code)
            when(u"重新打开发货会话", delivery_session)
            status_code = and_(u"修改发货任务", delivery_task)
            then(u"修改成功", status_code)

        with Scenario(u"修改发货单"):
            consignment = given(u"未打印的发货单", customer, delivery_session, store_bill1.sub_order.product)
            status_code = when(u"修改发货单的产品", consignment)
            then(u"修改成功", status_code)
            when(u"打印发货单", consignment)
            status_code = and_(u"修改发货单的产品", consignment)
            then(u"无法修改", status_code)

        with Scenario(u"对已生成发货单的发货会话，新增发货任务"):
            delivery_session = given(u"已生成发货单的发货会话", plate, 1000, customer, store_bill1.sub_order.product)
            then(u"重新打开发货会话", delivery_session)
            when(u"新增发货任务", delivery_session, store_bill2)
            then(u"提示需要重新生成发货单", delivery_session)

