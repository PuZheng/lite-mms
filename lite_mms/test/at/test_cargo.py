# -*- coding: UTF-8 -*-
from pyfeature import Feature, Scenario, given, and_, when, then
from lite_mms.basemain import app
from lite_mms.database import db

def test():
    from pyfeature import flask_sqlalchemy_setup
    flask_sqlalchemy_setup(app, db, create_step_prefix=u"创建")

    with Feature("卸货会话生成发货单", ['lite_mms.test.at.steps.cargo']):
        with Scenario(u"最简完整流程"):
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

        with Scenario(u'除非卸货会话关闭，否则卸货会话都可以修改'):
            pass

        with Scenario(u'收发员删除最后一个未称重的卸货任务'):
            pass

        with Scenario(u'收发员强行关闭卸货会话'):
            pass

        with Scenario(u'收发员创建卸货会话时，不能选择正在装货或者卸货的车辆'):
            pass

        with Scenario(u'收发员打开关闭的卸货会话，并且修改'):
            pass


if __name__ == "__main__":
    test()
