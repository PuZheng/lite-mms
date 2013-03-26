# -*- coding: UTF-8 -*-
from hashlib import md5
from flask import url_for
from lite_mms.basemain import app
from pyfeature import step
from lite_mms.utilities.decorators import committed
from lite_mms.models import Group, User, Department, Team, Customer, Plate, UnloadSession, GoodsReceipt, Order, ProductType, Product, Harbor, SubOrder, Procedure, WorkCommand
from lite_mms.constants import groups, work_command as const

@step(u"创建小组-(.+)")
@committed
def _(step, group_name):
    if group_name == u"收发员":
        group = Group(u'收发员')
        group.id = groups.CARGO_CLERK
    elif group_name == u"班组长":
        group = Group(u'班组长')
        group.id = groups.TEAM_LEADER
    return group


@step(u"创建一个用户-(.+)")
@committed
def _(step, name, group):
    if name == u"收发员":
        return User(u'cc', md5('cc').hexdigest(), [group])
    elif name == u"班组长":
        return User(u'tl', md5('tl').hexdigest(), [group])

@step(u"创建一个车间")
@committed
def _(step):
    return Department('cj1')

@step(u"创建一个班组")
@committed
def _(step, department, tl):
    return Team('tl', department, tl)

@step(u"创建一个客户")
@committed
def _(step):
    return Customer(u'宁波机械长','nbjxc')

@step(u"创建一个车牌号(.+)")
@committed
def _(step, plate_num):
    return Plate(plate_num)

@step(u"创建一个卸货会话")
@committed
def _(step, plate):
    return UnloadSession(plate.name, 12000)

@step(u"创建一个收获单")
@committed
def _(step, customer, unload_session):
    return GoodsReceipt(customer, unload_session)

@step(u"创建一个订单1")
@committed
def _(step, creator, goods_receipt):
    return Order(goods_receipt, creator)

@step(u"创建一个产品类型")
@committed
def _(step):
    return ProductType(u'默认加工件')

@step(u"创建一个产品")
@committed
def _(step, product_type):
    return Product(u'加工件', product_type)

@step(u"创建一个卸货点")
@committed
def _(step, department):
    return Harbor(u'装卸点一', department)

@step(u"生成一个订单1的子订单，重量为(\d+)")
@committed
def _(step, weight, order, product, harbor):
    return SubOrder(product, weight, harbor, order, weight, 'KG')

@step(u"创建一个工序(.+)")
@committed
def _(step, name, department):
    return Procedure(u'镀锌',[department])

@step(u"生成一个待结束、结转的工单，工序前重量为(\d+)，工序后重量为0")
@committed
def _(step, org_wegiht, suborder, team, procedure):
    return WorkCommand(suborder, org_wegiht, procedure, org_cnt=org_wegiht, status=const.STATUS_ENDING, team=team)

@step(u'班组长快速结转工单(.+)')
def _(step, result, work_command, actor):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.put(url_for("manufacture_ws.work_command", work_command_id=work_command.id, actor_id=actor.id, action=215))
            if result == u"失败":
                assert rv.status_code != 200
            else:
                assert rv.status_code == 200

@step(u'班组长增加重量(\d+)kg')
def _(step, processed_weight, work_command, actor):
    processed_weight = int(processed_weight)
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.put(url_for("manufacture_ws.work_command", work_command_id=work_command.id, actor_id=actor.id, weight=processed_weight, action=204))
            assert rv.status_code == 200

@step(u'生成一个新的待质检工单，重量为(\d+)')
def _(step, processed_weight, work_command):
    wc_list = WorkCommand.query.filter(WorkCommand.sub_order_id==work_command.sub_order_id, WorkCommand.status==const.STATUS_QUALITY_INSPECTING).all()
    assert len(wc_list) == 1
    assert wc_list[0].processed_weight == int(processed_weight)

@step(u'原工单的工序前重量为(\d+)，且状态还是待结束结转')
def _(step, org_weight, work_command):
    from lite_mms.apis.manufacture import WorkCommandWrapper
    wc = WorkCommandWrapper.get_work_command(work_command.id)
    assert wc.org_weight == int(org_weight)

