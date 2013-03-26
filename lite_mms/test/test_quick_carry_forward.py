# -*- coding: UTF-8 -*-
__author__ = 'wangjiali'
from pyfeature import Feature, Scenario, given, and_, when, then
from lite_mms.basemain import app
from lite_mms.database import db

def test():
    from pyfeature import flask_sqlalchemy_setup
    flask_sqlalchemy_setup(app, db)
    with Feature(u"班组长快速结转", ['lite_mms.test.steps.quick_carry_forward']):
        with Scenario(u'快速结转'):
            cc_group = given(u"创建小组-收发员")
            tl_group = and_(u"创建小组-班组长")
            team_lead = and_(u"创建一个用户-班组长", group=tl_group)
            cc = and_(u"创建一个用户-收发员", group=cc_group)

            department = and_(u"创建一个车间")
            team = and_(u"创建一个班组", department, team_lead)

            customer = and_(u"创建一个客户")
            plate = and_(u"创建一个车牌号aA12345")
            unload_session = and_(u"创建一个卸货会话", plate)
            goods_receipt = and_(u"创建一个收获单", customer, unload_session)
            order = and_(u"创建一个订单1", cc, goods_receipt)
            product_type = and_(u"创建一个产品类型")
            product = and_(u"创建一个产品", product_type)
            harbor = and_(u"创建一个卸货点", department)
            suborder = and_(u"生成一个订单1的子订单，重量为10000", order=order, product=product, harbor=harbor)
            procedure = and_(u"创建一个工序镀锌", department)
            work_command = and_(u"生成一个待结束、结转的工单，工序前重量为3000，工序后重量为0", suborder=suborder, team=team, procedure=procedure)

            then(u'班组长快速结转工单失败', work_command, team_lead)

            when(u'班组长增加重量1000kg', work_command, team_lead)
            then(u'班组长快速结转工单成功', work_command, team_lead)
            and_(u'生成一个新的待质检工单，重量为1000', work_command)
            and_(u'原工单的工序前重量为2000，且状态还是待结束结转', work_command)
    
    from pyfeature import clear_hooks
    clear_hooks()
