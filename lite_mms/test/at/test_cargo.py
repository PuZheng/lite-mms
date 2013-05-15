# -*- coding: UTF-8 -*-
from pyfeature import Feature, Scenario, given, and_, when, then
from lite_mms.basemain import app
from lite_mms.database import db

def test():
    from pyfeature import flask_sqlalchemy_setup
    flask_sqlalchemy_setup(app, db, create_step_prefix=u"创建", 
                           model_name_getter=lambda model: model.__modelname__, 
                           attr_name_getter=lambda model, attr: model.__col_desc__.get(attr, attr),
                           set_step_pattern=u'(\w+)([\.\w+]+)设置为(.+)',
                           test_step_pattern=u'(\w+)([\.\w+]+)是(.+)')

    with Feature("卸货会话生成发货单", ['lite_mms.test.at.steps.cargo']):
        with Scenario(u"最简完整流程"):
            plate = when(u"创建车辆(浙B 00001)")
            and_(u'车辆.车牌号设置为u"浙B 00002"', plate)
            then(u'车辆.车牌号是u"浙B 00002"', plate)
            then(u'车辆.车牌号是s', plate, s=u"浙B 00002")
            #when(u'收发员创建Plate(浙B 00001)')
            #and_(u'收发员创建UnloadSession， 毛重是10000公斤')
            #and_(u'装卸工进行卸货，该货物来自宁波机床厂，并且标记是最后一个任务')
            #and_(u'收发员称重8000公斤')

            #then(u"卸货任务的重量是2000公斤")
            #and_(u'卸货任务已经关闭')

            #when(u'收发员生成收货单')
            #then(u'该收货单中包含一个项目，该项目的客户是宁波机床厂, 项目的重量是2000公斤')

        with Scenario(u"包含多次卸货任务的卸货会话"):
            pass
            #when(u'收发员创建Plate(浙B 00001)')
            #and_(u'收发员创建UnloadSession， 毛重是10000公斤')
            #and_(u'装卸工进行卸货，该货物来自宁波机床厂')
            #then(u'装卸工此时不能进行卸货')

            #when(u'收发员称重8000公斤')
            #then(u"卸货任务的重量是2000公斤")
            #and_(u'卸货任务没有关闭')

            #when(u'装卸工进行卸货，该货物来自宁力紧固件, 并且标记是最后一个任务')
            #and_(u'收发员称重5000公斤')
            #then(u'收货任务的重量是3000公斤')
            #and_(u"卸货会话已经关闭")

            #when(u'收发员生成收货单')
            #then(u'该收货单中包含两个项目')
            #and_(u'第一个项目的客户是宁波机床厂, 项目的重量是2000公斤')
            #and_(u'第二个项目的客户是宁力紧固件, 项目的重量是3000公斤')

        with Scenario(u'除非卸货会话关闭，否则卸货会话都可以修改'):
            pass
            #when(u'创建卸货会话, 其状态是待称重')
            #and_(u'创建卸货任务')
            #and_(u'修改卸货会话的车牌号为浙B 00002')
            #and_(u'修改卸货会话的毛重为10000公斤')
            #then(u'卸货会话的车牌号为浙B 00002') 
            #and_(u'卸货会话的重量为10000公斤')
            #and_(u'修改卸货任务的重量为2000公斤')
            #then(u'卸货任务的重量是2000公斤')

            #when(u'关闭卸货会话')
            #then_(u'不能修改卸货会话')
            #and_(u'不能修改卸货任务')

        with Scenario(u'收发员删除最后一个未称重的卸货任务'):
            pass

        with Scenario(u'收发员强行关闭卸货会话'):
            pass

        with Scenario(u'收发员创建卸货会话时，不能选择正在装货或者卸货的车辆'):
            pass

        with Scenario(u'收发员打开关闭的卸货会话，并且修改'):
            pass

        with Scenario(u'若收货单过时，或者已经生成了订单，那么不能修改收货单'):
            pass
            #when(u'创建卸货会话')
            #and_(u'创建卸货任务，客户是宁波机床厂')
            #and_(u'生成收货单')
            #and_(u'创建卸货任务，客户是宁波机床厂')

            #then(u'收货单过时')
            #and_(u'不能修改收货单')
            
            #when(u'重新生成收货单')
            #and_(u'生成订单')
            #then(u'不能修改收货单')


            


if __name__ == "__main__":
    test()
