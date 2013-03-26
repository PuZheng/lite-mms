#-*- coding:utf-8 -*-
# -*- coding: UTF-8 -*-
from pyfeature import step
from lite_mms import models
from lite_mms.utilities.decorators import committed
from lite_mms.utilities import do_commit
from lite_mms.basemain import app


def random():
    import random, string

    return random.choice(string.letters) + random.choice(
        string.letters) + random.choice(string.letters)


@step(u"调度员组")
@committed
def _(step):
    from lite_mms.permissions import permissions
    from lite_mms.constants.groups import SCHEDULER

    for perm in permissions.keys():
        do_commit(models.Permission(name=perm))
    g = models.Group("schedule")
    g.id = SCHEDULER
    g.permissions = models.Permission.query.filter(
        models.Permission.name.like(
            "%schedule_order%")).all() + models.Permission.query.filter(
        models.Permission.name.like("work_command%")).all()
    return g


@step(u"调度员001")
@committed
def _(step, username, password, group):
    from hashlib import md5

    return models.User(username, md5(password).hexdigest(), [group])


@step(u"车间1")
def _(step):
    depart = do_commit(models.Department(name=u"车间" + random()))
    do_commit(models.Procedure(name=u"测试工序", department_list=[depart]))
    return depart


@step(u"班组1")
@committed
def _(step, department):
    return models.Team(name=u"班组" + random(), department=department,
                       leader=None)


@step(u"(.+)类型子订单(.*)")
@committed
def _(step, type_, extra, department, weight, quantity=0):
    harbor = do_commit(
        models.Harbor(u"仓库1" + random(), department))
    product_type = do_commit(
        models.ProductType(u"测试用" + random()))
    product = models.Product(u"测试用" + random(),
                             product_type)
    customer = do_commit(
        models.Customer(u"匿名" + random(), abbr=u'nm'))
    us = models.UnloadSession(plate=u"测试车辆" + random(),
                              gross_weight=50000)
    ut = do_commit(
        models.UnloadTask(us, harbor=harbor, customer=customer, creator=None,
                          product=product, pic_path=""))
    goods_receipt = do_commit(models.GoodsReceipt(customer, us))
    order = do_commit(models.Order(goods_receipt, None))
    returned = False
    unit = u"KG"
    from lite_mms.constants import STANDARD_ORDER_TYPE, EXTRA_ORDER_TYPE

    order_type = STANDARD_ORDER_TYPE
    if u"退货" in extra:
        returned = True

    if type_ == u"计重":
        quantity = weight

    elif type_ == u"计件":
        unit = u"件"
        order_type = EXTRA_ORDER_TYPE
    return models.SubOrder(product, weight, harbor, order, quantity,
                           unit, order_type, returned=returned)


@step(u"调度员从子订单中预排产(.*)")
def _(step, status, sub_order, weight, username, password, quantity=0):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.post("/auth/login",
                        data={"username": username, "password": password})
            assert 302 == rv.status_code
            data = {"schedule_weight": weight,
                    "tech_req": u"超脱",
                    "id": sub_order.id,
                    "order_id": sub_order.order.id}
            if not sub_order.returned:
                data["procedure"] = 1
            if quantity:
                data["schedule_count"] = quantity
            rv = c.post("/schedule/work-command",
                        data=data)
            if u"失败" in status:
                assert 403 == rv.status_code
            else:
                assert 302 == rv.status_code
                from lite_mms.apis.manufacture import get_work_command_list

                return get_work_command_list(0)[0][-1]


@step(u"子订单中未分配的重量是(\d+)公斤")
def _(step, weight, sub_order):
    from lite_mms.apis.order import get_sub_order

    sub_order = get_sub_order(sub_order.id)
    assert int(weight) == sub_order.remaining_weight


@step(u"生成了新的工单,其重量是(\d+)公斤")
def _(step, weight, sub_order):
    from lite_mms.apis.manufacture import get_work_command_list

    wc = get_work_command_list(0)[0][-1]
    assert wc.org_weight == int(weight)
    assert wc.sub_order.id == sub_order.id


@step(u"子订单中未分配的重量是(\d+)公斤,件数是(\d+)件")
def _(step, weight, quantity, sub_order):
    from lite_mms.apis.order import get_sub_order

    sub_order = get_sub_order(sub_order.id)
    assert int(weight) == sub_order.remaining_weight
    assert int(quantity) == sub_order.remaining_quantity


@step(u"生成了新的工单,其重量是(\d+)公斤,件数是(\d+)件")
def _(step, weight, quantity):
    from lite_mms.apis.manufacture import get_work_command_list

    wc = get_work_command_list(0)[0][-1]
    assert wc.org_weight == int(weight)
    assert wc.org_cnt == int(quantity)


@step(u"质检员的待质检列表中增加了一个(\d+)公斤的工单")
def _(step, weight):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.get("/manufacture_ws/work-command-list?status=7")
            import json

            data = json.loads(rv.data)
            assert 1 == data["totalCnt"]
            assert int(weight) == data["data"][0]["orgWeight"]
            from lite_mms.apis.manufacture import get_work_command

            return get_work_command(data["data"][0]["id"])


@step(u"这个工单的子订单是3")
def _(step, work_command, sub_order):
    assert work_command.sub_order.id == sub_order.id


@step(u"调度员将工单调度给车间")
def _(step, work_command, department, username, password):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.post("/auth/login",
                        data={"username": username, "password": password})
            assert 302 == rv.status_code
            rv = c.post("/manufacture/schedule",
                        data={"id": work_command.id, "procedure_id": 1,
                              "department_id": department.id,
                              "tech_req": u"测试"})
            assert 302 == rv.status_code


@step(u"车间主任可获取的工单列表包括工单")
def _(step, department, wc):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.get(
                "/manufacture_ws/work-command-list?status=2&department_id=%d"
                "" % department.id)
            import json

            data = json.loads(rv.data)
            assert 1 == data["totalCnt"]
            assert wc.id == data["data"][0]["id"]


@step(u"调度员回收工单")
def _(step, work_command, username, password):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.post("/auth/login",
                        data={"username": username, "password": password})
            assert 302 == rv.status_code
            rv = c.post("/manufacture/retrieve",
                        data={"work_command_id": work_command.id})
            return rv.status_code


@step(u"工单的状态转变为(.+)")
def _(step, status, work_command):
    from lite_mms.apis.manufacture import get_work_command

    wc = get_work_command(work_command.id)
    from lite_mms.constants import work_command

    if status == u"未调度":
        assert work_command.STATUS_DISPATCHING == wc.status
    elif status == u"锁定":
        assert work_command.STATUS_LOCKED == wc.status
    elif status == u"车间主任打回":
        assert work_command.STATUS_REFUSED == wc.status
    elif status == u"待质检":
        assert work_command.STATUS_QUALITY_INSPECTING == wc.status
    elif status == u"待分配":
        assert work_command.STATUS_ASSIGNING == wc.status
    elif status == u"结束":
        assert work_command.STATUS_FINISHED == wc.status

@step(u"工单没有出现在车间主任的工单列表中")
def _(step, department, work_command):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.get(
                "/manufacture_ws/work-command-list?status=2&department_id=%d"
                "" % department.id)
            import json

            data = json.loads(rv.data)
            id_list = []
            for wc in data["data"]:
                id_list.append(int(wc["id"]))
            assert work_command.id not in id_list


@step(u"工单不能够再次增加重量")
def _(step, work_command):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.put(
                "/manufacture_ws/work-command?work_command_id=%d&actor_id=1"
                "&weight=1&quantity=1&action=204" % work_command.id)
            assert 403 == rv.status_code


@step(u"车间主任确认回收工单")
def _(step, work_command):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.put(
                "/manufacture_ws/work-command?work_command_id=%d&actor_id=1"
                "&action=211&weight=300&quantity=300" % work_command.id)
            assert 200 == rv.status_code


@step(u"工单生产完毕的部分成为一个待质检工单,重量是(\d+)公斤(,件数是(\d+)件)?")
def _(step, weight, extra, quantity, work_command):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.get("/manufacture_ws/work-command-list?status=7")
            import json

            data = json.loads(rv.data)
            assert int(weight) == data["data"][-1]["orgWeight"]
            if quantity:
                assert int(quantity) == data["data"][-1]["orgCnt"]
            from lite_mms.apis.manufacture import get_work_command

            return get_work_command(data["data"][0]["id"])


@step(u"工单重新变成待调度,重量是(\d+)公斤")
def _(step, weight, work_command):
    from lite_mms.apis.manufacture import get_work_command

    wc = get_work_command(work_command.id)
    from lite_mms.constants.work_command import STATUS_DISPATCHING

    assert int(weight) == work_command.org_weight
    assert STATUS_DISPATCHING == work_command.status


@step(u"返回403错误")
def _(step, result_code):
    assert 403 == result_code


@step(u"工单的状态仍然是待质检")
def _(step, work_command):
    from lite_mms.apis.manufacture import get_work_command

    wc = get_work_command(work_command.id)
    from lite_mms.constants.work_command import STATUS_QUALITY_INSPECTING

    assert STATUS_QUALITY_INSPECTING == wc.status


@step(u"车间主任分配工单给班组")
def _(step, department, work_command, team):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.put(
                "/manufacture_ws/work-command?work_command_id=%d&actor_id=1"
                "&team_id=%d&action=203" % (
                    work_command.id, team.id))
            assert 200 == rv.status_code


@step(u"工单出现在班组的工单列表中")
def _(step, work_command, team):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.get(
                "/manufacture_ws/work-command-list?status=4&team=%d" % team.id)
            import json

            data = json.loads(rv.data)
            id_list = []
            for wc in data["data"]:
                id_list.append(int(wc["id"]))
            assert work_command.id in id_list


@step(u"车间主任打回工单")
def _(step, work_command):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.put(
                "/manufacture_ws/work-command?work_command_id=%d&actor_id=1"
                "&reason=%s&action=209" % (
                    work_command.id, "Nothing"))
            assert 200 == rv.status_code


@step(u"班组长增加了工单的工序后重量(\d+)公斤(,件数是(\d+)件)?")
def _(step, weight, extra, quantity, work_command):
    if not quantity:
        quantity = weight
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.put(
                "/manufacture_ws/work-command?work_command_id=%d&actor_id=1"
                "&weight=%s&quantity=%s&action=204" % (
                    work_command.id, weight, quantity))
            assert 200 == rv.status_code


@step(u"班组长(.+)工单$")
def _(step, action, work_command):
    if action == u"结束":
        action = 205
    elif action == u"结转":
        action = 206
    else:
        return
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.put(
                "/manufacture_ws/work-command?work_command_id=%d&actor_id=1"
                "&action=%d" % (
                    work_command.id, action))

            assert 200 == rv.status_code
            if action == 206:
                from lite_mms.apis.manufacture import get_work_command_list
                return get_work_command_list(0)[0][-1]

@step(u"工单的工序后重量是(\d+)公斤(,件数是(\d+)件)?")
def _(step, weight, extra, quantity, work_command):
    from lite_mms.apis.manufacture import get_work_command

    wc = get_work_command(work_command.id)

    assert int(weight) == wc.processed_weight
    if quantity:
        assert int(quantity) == wc.processed_cnt

@step(u"工单重量是(\d+)公斤(,件数(\d+)件)?")
def _(step, weight, extra, quantity, work_command):
    from lite_mms.apis.manufacture import get_work_command
    wc = get_work_command(work_command.id)

    assert int(weight) == wc.org_weight
    if quantity:
        assert int(quantity) == wc.org_cnt

@step(u"班组长快速结转工单成功")
def _(step, work_command):
    with app.test_request_context():
        with app.test_client() as c:
            from flask import url_for

            rv = c.put(url_for("manufacture_ws.work_command",
                               work_command_id=work_command.id, actor_id=1,
                               action=215))
            assert rv.status_code == 200
            from lite_mms.apis.manufacture import get_work_command_list

            return get_work_command_list(0)[0][-1]

@step(u"工单状态还是待结束结转")
def _(step, work_command):
    from lite_mms.apis.manufacture import get_work_command
    wc = get_work_command(work_command.id)
    from lite_mms.constants.work_command import STATUS_ENDING

    assert STATUS_ENDING == wc.status

@step(u"质检结果合格结束")
def _(step, work_command, weight):
    with app.test_request_context():
        with app.test_client() as c:
            from lite_mms.constants.quality_inspection import FINISHED

            rv = c.post(
                "/manufacture_ws/quality-inspection-report?actor_id=1"
                "&work_command_id=%d&quantity=%d&result=%d" % (
                    work_command.id, weight, FINISHED))

            assert 200 == rv.status_code
            from lite_mms.apis.quality_inspection import get_qir_list
            return get_qir_list()[0][-1]

@step(u"生成一个仓单")
def _(step, qir, weight):
    from lite_mms.apis.quality_inspection import get_qir
    qir = get_qir(qir.id)
    assert 1 == len(qir.store_bill_list)
    assert int(weight) == qir.store_bill_list[0].weight

@step(u"质检结果部分返修,其他合格结束")
def _(step, work_command, weight1, weight2):
    with app.test_request_context():
        with app.test_client() as c:
            from lite_mms.constants.quality_inspection import REPAIR, FINISHED

            rv = c.post(
                "/manufacture_ws/quality-inspection-report?actor_id=1"
                "&work_command_id=%d&quantity=%d&result=%d" % (
                    work_command.id, weight1, REPAIR))

            assert 200 == rv.status_code
            rv = c.post(
                "/manufacture_ws/quality-inspection-report?actor_id=1"
                "&work_command_id=%d&quantity=%d&result=%d" % (
                    work_command.id, weight2, FINISHED))

            assert 200 == rv.status_code

            from lite_mms.apis.quality_inspection import get_qir_list

            return get_qir_list()[0][-1]

@step(u"生成一个待质检的工单, 工序为空")
def _(step, weight):
    from lite_mms.apis.manufacture import get_work_command_list

    wc = get_work_command_list(0)[0][-1]
    from lite_mms.constants.work_command import STATUS_QUALITY_INSPECTING

    assert wc.status == STATUS_QUALITY_INSPECTING
    assert wc.org_weight == weight
    assert not wc.procedure
    return wc


@step(u"全部返镀")
def _(step, work_command, weight):
    with app.test_request_context():
        with app.test_client() as c:
            from lite_mms.constants.quality_inspection import REPLATE

            rv = c.post(
                "/manufacture_ws/quality-inspection-report?actor_id=1"
                "&work_command_id=%d&quantity=%d&result=%d" % (
                    work_command.id, weight, REPLATE))

            assert 200 == rv.status_code


@step(u"质检员提交质检单")
def _(step, work_command):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.put(
                "/manufacture_ws/work-command?work_command_id=%d&actor_id=1"
                "&action=212" % work_command.id)
            assert 200 == rv.status_code


@step(u"原工单的状态为结束,待发货重量为0")
def _(step, work_command):
    from lite_mms.apis.manufacture import get_work_command

    wc = get_work_command(work_command.id)
    from lite_mms.constants.work_command import STATUS_FINISHED

    assert STATUS_FINISHED == wc.status
    assert 0 == wc.sub_order.order.to_deliver_weight


@step(u"新工单状态为(.+)")
def _(step,status, weight):
    from lite_mms.apis.manufacture import get_work_command_list

    wc = get_work_command_list(0)[0][-1]
    from lite_mms.constants import work_command
    if status == u"待排产":
        assert work_command.STATUS_DISPATCHING == wc.status
    elif status == u"待分配":
        assert work_command.STATUS_ASSIGNING == wc.status
    assert weight == wc.org_weight
    return wc


@step(u"取消质检单")
def _(step, work_command):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.put(
                "/manufacture_ws/work-command?work_command_id=%d&actor_id=1"
                "&action=214" % work_command.id)
            assert 200 == rv.status_code


@step(u"工单状态还原为待质检")
def _(step, work_command):
    from lite_mms.apis.manufacture import get_work_command

    wc = get_work_command(work_command.id)
    from lite_mms.constants.work_command import STATUS_QUALITY_INSPECTING

    assert STATUS_QUALITY_INSPECTING == wc.status


@step(u"新工单被删除")
def _(step, work_command):
    from lite_mms.apis.manufacture import get_work_command

    wc = get_work_command(work_command.id)
    assert None == wc