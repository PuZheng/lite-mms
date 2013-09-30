# -*- coding: UTF-8 -*-
from hashlib import md5

from lite_mms import constants
from pyfeature import Feature, Scenario, given, when, and_, then, flask_sqlalchemy_setup, clear_hooks

import lite_mms
from lite_mms.basemain import app
from lite_mms.database import db



def test():
    flask_sqlalchemy_setup(app, db, create_step_prefix=u"创建",
                           model_name_getter=lambda model: model.__name__,
                           attr_name_getter=lambda model, attr: model.__col_desc__.get(attr, attr),
                           set_step_pattern=u'(\w+)([\.\w+]+)设置为(.+)')

    with Feature(u'订单测试', step_files=['lite_mms.test.at.steps.manufacture']):
        with Scenario(u'准备数据'):
            cargo_clerk_group= and_(u'创建Group(cargo_clerk)', 
                                    id=lite_mms.constants.groups.CARGO_CLERK)
            cargo_clerk = and_(u'创建User', username='cc', 
                               password=md5('cc').hexdigest(),
                              groups=[cargo_clerk_group])
            scheduler_group = and_(u'创建Group(scheduler)', 
                                   id=lite_mms.constants.groups.SCHEDULER)
            and_(u'创建User', username='s', password=md5('s').hexdigest(), 
                 groups=[scheduler_group])
            customer = and_(u'创建Customer', name='foo', abbr='foo')
            plate = and_(u'创建Plate', name='foo')
            unload_session = and_(u'创建UnloadSession', plate_=plate, 
                                  gross_weight=5000)
            goods_receipt = and_(u'创建GoodsReceipt', customer=customer, 
                                 unload_session=unload_session, 
                                 creator=cargo_clerk)
            order = and_(u'创建Order', goods_receipt=goods_receipt, 
                         creator=cargo_clerk)
            product_type = and_(u'创建ProductType', name='foo') 
            product = and_(u'创建Product', name='foo', 
                           product_type=product_type)
            harbor = and_(u'创建Harbor', name='foo')
            sub_order = and_(u'创建SubOrder', product=product, weight=100,
                             harbor=harbor, order=order, quantity=100, 
                             unit='KG')
            department_leader_group = and_(u'创建Group(department_leader)', 
                                           id=lite_mms.constants.groups.DEPARTMENT_LEADER)
            department_leader = and_(u'创建User', username='dl', 
                                     password=md5('dl').hexdigest(), 
                                     groups=[department_leader_group])
            department = and_(u'创建Department', name='foo', 
                              leader_list=[department_leader],
                             harbor_list=[harbor])
            team_leader_group = and_(u'创建Group(team_leader)',
                                    id=lite_mms.constants.groups.TEAM_LEADER)
            team_leader = and_(u'创建User', username='tl',
                               password=md5('tl').hexdigest(),
                               groups=[team_leader_group])
            team = and_(u'创建Team', name='foo', department=department,
                       leader=team_leader)
            quality_inspector_group = and_(u'创建Group(quality_inspector)',
                                           id=lite_mms.constants.groups.QUALITY_INSPECTOR)
            quality_inspector = and_(u'创建User', username='qi', 
                                     password=md5('qi').hexdigest(),
                                     groups=[quality_inspector_group])


        with Scenario(u'最简流程'):
            when(u'调度员对子订单进行预排产60公斤', sub_order)
            wc = then(u'一条重量是60公斤的工单生成了', sub_order)
            and_(u'原子订单的剩余重量是40公斤', sub_order)
            when(u'调度员将工单排产给车间', wc, department)
            then(u'车间主任将看到工单', wc, department)
            then(u'车间主任将工单分配到班组', wc, department, team)
            then(u'班组长将看到工单', wc, team)
            
            when(u'班组长增加重量20公斤', wc)
            when(u'班组长增加重量30公斤', wc)
            when(u'班组长增加重量50公斤, 并且结束', wc)
            and_(u'工单的工序后重量是100公斤', wc)

            then(u'质检员可以看到工单', wc, team)

            qir = when(u'质检员全部通过该工单', wc)
            then(u'该工单已经结束', wc)
            store_bill = and_(u'一条对应的仓单生成了', qir, harbor)

    clear_hooks()

if __name__ == '__main__':
    test()

