# -*- coding: UTF-8 -*-
from datetime import timedelta

from hashlib import md5
from flask import url_for
from flask.ext.login import current_user
from lite_mms.basemain import app
from lite_mms.constants import groups, work_command as status, quality_inspection
from pyfeature import step
from lite_mms.models import Group, User, Team, Department, Order, Plate, Customer, UnloadSession, GoodsReceipt, SubOrder, Product, ProductType, Harbor, WorkCommand, Procedure, QIReport, DeliverySession, Permission
from lite_mms.utilities.decorators import committed


@step(u"创建小组-(.+)")
@committed
def _(step, group_name):
    if group_name == u"质检员":
        group = Group(name=u'质检')
        group.id = groups.QUALITY_INSPECTOR
    elif group_name == u"收发员":
        group = Group(name=u'收发员')
        group.id = groups.CARGO_CLERK
    elif group_name == u"班组长":
        group = Group(name=u'班组长')
        group.id = groups.TEAM_LEADER
    elif group_name == u"调度员":
        group = Group(name=u'调度员')
        group.id = groups.SCHEDULER
        group.permissions = [
            Permission(name="work_command.schedule_work_command")]
    return group


@step(u"创建一个用户-(.+)")
@committed
def _(step, name, group):
    username = ""
    if name == u"质检员":
        username = u"qi"
    elif name == u"收发员":
        username = u'cc'
    elif name == u"班组长":
        username = u"tl"
    elif name == u"调度员":
        username = u"s"
    return User(username=username, password=md5(username).hexdigest(),
                groups=[group])



@step(u"创建一个车间")
@committed
def _(step):
    return Department(name='cj1')


@step(u"创建一个班组")
@committed
def _(step, department, tl):
    return Team(name='tl', department=department, leader=tl)


@step(u"创建一个客户")
@committed
def _(step):
    return Customer(name=u'宁波机械长', abbr='nbjxc')


@step(u"创建一个车牌号(.+)")
@committed
def _(step, plate_num):
    return Plate(plate_num)


@step(u"创建一个卸货会话")
@committed
def _(step, plate):
    return UnloadSession(plate=plate.name, gross_weight=12000)


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
    return Harbor(name=u'装卸点一', department=department)


@step(u"生成一个订单1的子订单，重量为(\d+)")
@committed
def _(step, weight, order, product, harbor):
    return SubOrder(product, weight, harbor, order, weight, 'KG')


@step(u"创建一个工序(.+)")
@committed
def _(step, name, department):
    return Procedure(name=u'镀锌', department_list=[department])


@step(u"生成一个待质检状态的工单，重量为(\d+)")
@committed
def _(step, weight, suborder, department, team, procedure):
    return WorkCommand(suborder, weight, procedure, department=department,
                       status=status.STATUS_QUALITY_INSPECTING, team=team)


@step(u"生成一个(.+)的质检报告，重量为(\d+)")
@committed
def _(step, result, weight, work_command, actor):
    if result == u'合格结束':
        result = quality_inspection.FINISHED
    elif result == u'合格转下道工序':
        result = quality_inspection.NEXT_PROCEDURE
    elif result == u'返修':
        result = quality_inspection.REPAIR
    elif result == u'返镀':
        result = quality_inspection.REPLATE
    return QIReport(work_command, weight, weight, result, actor.id)


@step(u"创建一个发货会话")
@committed
def _(step, plate):
    return DeliverySession(plate.name, 1000)


@step(u"提交质检单，扣重为(\d+)")
def _(step, deduction, actor, work_command):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.put(url_for("manufacture_ws.work_command",
                               work_command_id=work_command.id,
                               actor_id=actor.id, action=212,
                               deduction=deduction))
            assert rv.status_code == 200
            from lite_mms.apis import manufacture

            return manufacture.get_work_command(work_command.id)


@step(u"质检报告生成的新工单任意一个已经分配")
def _(step, qi_report_list, team):
    assert qi_report_list
    wc = qi_report_list[1].generated_work_command
    assert wc.team == None
    from lite_mms import constants

    assert wc.status == constants.work_command.STATUS_ASSIGNING
    assert wc.department is not None
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.post(url_for('auth.login'),
                        data=dict(username='s',
                                  password='s'))
            assert rv.status_code == 302
            us = current_user
            rv = c.put(
                url_for("manufacture_ws.work_command", work_command_id=wc.id,
                        actor_id=current_user.id, team_id=team.id, action=203))
            print rv.data
            assert rv.status_code == 200


@step(u"取消质检结果(.+)")
def _(step, result, actor, work_command):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.put(url_for("manufacture_ws.work_command",
                               work_command_id=work_command.id,
                               actor_id=actor.id, action=214))
            if result == u"失败":
                assert rv.status_code != 200
            else:
                assert rv.status_code == 200


@step(u"工单扣重量还是(\d+)")
def _(step, weight, work_command):
    from lite_mms.apis import manufacture

    wc = manufacture.get_work_command(work_command.id)
    assert wc.deduction == int(weight)


@step(u"质检报告生成的新工单都未分配")
def _(step, qi_report_list):
    assert qi_report_list
    wc1, wc2, wc3 = [qir.generated_work_command for qir in qi_report_list]
    assert wc1 and wc2 and wc3
    from lite_mms import constants
    assert wc1.status == constants.work_command.STATUS_DISPATCHING
    assert wc2.status == wc3.status == constants.work_command.STATUS_ASSIGNING
    assert wc1.department is None
    assert wc2.department.name == wc3.department.name
    assert wc1.team == wc2.team == wc3.team is None
    return wc1.id, wc2.id, wc3.id

@step(u"质检报告生成的工单被删除")
def _(step, qi_report_list, wc_id_list):
    assert qi_report_list
    assert wc_id_list
    from lite_mms.apis import manufacture

    for qir in qi_report_list:
        assert not manufacture.get_work_command(qir.generated_work_command_id)

    for id_ in wc_id_list:
        assert not manufacture.get_work_command(id_)

@step(u"工单状态变回待质检,扣重为0")
def _(step, work_command):
    from lite_mms.apis import manufacture

    wc = manufacture.get_work_command(work_command.id)
    assert wc.status == status.STATUS_QUALITY_INSPECTING
    assert wc.deduction == 0


@step(u"质检报告还关联着工单")
def _(step, qi_report_list, work_command):
    for qi_report in qi_report_list:
        assert qi_report.id in [qir.id for qir in work_command.qir_list]


@step(u"生成一个新的仓单和一个新的工单")
def _(step, qi_report_over, qi_report_repair):
    from lite_mms.apis import quality_inspection

    store_bill_list = quality_inspection.get_qir(
        qi_report_over.id).store_bill_list
    assert len(store_bill_list) == 1
    wc = quality_inspection.get_qir(qi_report_repair.id).generated_work_command
    assert wc
    return store_bill_list[0], wc


@step(u"仓单已经发货")
@committed
def _(step, store_bill, work_command, delivery_session):
    store_bill.delivery_session_id = delivery_session.id
    return store_bill


@step(u"仓单未发货，且工单未排产")
def _(step, store_bill, work_command):
    pass


@step(u"仓单被删除")
def _(step, store_bill):
    from lite_mms.apis import delivery

    assert not delivery.get_store_bill(store_bill.id)


@step(u"质检结果是前一天提交")
@committed
def _(step, work_command):
    work_command.model.last_mod = work_command.last_mod - timedelta(1)
    return work_command.model
