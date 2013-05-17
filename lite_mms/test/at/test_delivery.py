#-*- coding:utf-8 -*-
from pyfeature import Feature, Scenario, given, when, and_, then, flask_sqlalchemy_setup

from lite_mms.basemain import app
from lite_mms.database import db

#TODO 未实现！
with Feature(u"发货会话测试", step_files=["lite_mms.test.at.steps.delivery"]):
    flask_sqlalchemy_setup(app, db, create_step_prefix=u"创建",
                           model_name_getter=lambda model: model.__name__,
                           attr_name_getter=lambda model, attr: model.__col_desc__.get(attr, attr),
                           set_step_pattern=u'(\w+)([\.\w+]+)设置为(.+)')

    with Scenario(u"准备数据"):
        plate = given(u"创建Plate")
        and_(u"创建User", username="cc", password="cc")
        store_bill1 = and_(u"创建StoreBill")
        store_bill2 = and_(u"创建StoreBill")
        and_(u"创建Harbor")
        and_(u"创建Customer")

    with Scenario(u"创建发货会话，并生成发货单"):
        when(u"收发员创建发货会话", plate=plate, tare=1500)
        then(u"收发员选择仓单", store_bill1, store_bill2)
        and_(u"装卸工全部装货、完全装货", store_bill1)
        and_(u"收发员生成发货单")
        then(u"发货单产品与仓单相同", store_bill1)

    with Scenario(u"修改发货会话"):
        delivery_session = given(u"已关闭的发货会话")
        when(u"修改发货会话", delivery_session)
        then(u"无法修改发货会话", delivery_session)
        when(u"重新打开", delivery_session)
        then(u"可以修改发货会话", delivery_session)

    with Scenario(u"修改发货任务"):
        delivery_session = given(u"已关闭的发货会话")
        delivery_task = and_(u"发货任务")
        when(u"修改发货任务", delivery_task)
        then(u"无法修改发货任务", delivery_task)
        when(u"重新打开发货会话", delivery_session)
        and_(u"修改发货任务", delivery_task)
        then(u"可以修改发货任务", delivery_task)

    with Scenario(u"修改发货单"):
        consignment = given(u"未打印的发货单")
        when(u"修改发货单的产品", consignment)
        then(u"修改成功")
        when(u"打印发货单", consignment)
        and_(u"修改发货单的产品", consignment)
        then(u"无法修改")

    with Scenario(u"对已生成发货单的发货会话，新增发货任务"):
        delivery_session = given(u"已生成发货单的发货会话")
        then(u"重新打开",delivery_session)
        when(u"新增发货任务")
        then(u"提示需要重新生成发货单", delivery_session)

