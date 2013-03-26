# -*- coding: UTF-8 -*-
from hashlib import md5
import json
from flask import url_for
from pyfeature import step
from lite_mms import models, constants
from lite_mms.utilities.decorators import committed


@step(u'生成产品类型"手机"')
@committed
def _(step):
    return models.ProductType(u'手机')


@step(u'生成产品"iphone4"')
@committed
def _(step, product_type):
    return models.Product(u"iphone4", product_type)


@step(u'创建用户组"调度员"')
@committed
def _(step):
    group = models.Group(u"调度员")
    group.id = constants.groups.CARGO_CLERK
    return group


@step(u'生成调度员"小明", 密码是xm')
@committed
def _(step, group):
    return models.User(u"小明", md5("xm").hexdigest(), [group])


@step(u'生成车间"A"')
@committed
def _(step):
    return models.Department(u"A")

@step(u"生成班组'(.+)'")
@committed
def _(step, name, department):
    return models.Team(name, department, None)


@step(u'生成装卸点"X"')
@committed
def _(step, department):
    return models.Harbor("habor", department)


@step(u'生成工序"镀锌"')
@committed
def _(step, department):
    return models.Procedure(u"镀锌", [department])


@step(u'生成客户"宁力"')
@committed
def _(step):
    return models.Customer("foo", "foo")


@step(u"生成卸货会话, 重量为10000公斤")
@committed
def _(step, customer):
    return models.UnloadSession(customer.name, 10000)


@step(u"生成收货单")
@committed
def _(step, customer, unload_session):
    return models.GoodsReceipt(customer=customer,
                               unload_session=unload_session)


@step(u"生成订单")
@committed
def _(step, goods_receipt, creator):
    return models.Order(goods_receipt, creator=creator)


@step(u"生成计件类型的子订单, 重量是(\d+)公斤, 数量是(\d+)桶, 规格是(.+), 型号是(.+)")
@committed
def _(step, weight, count, spec, type, harbor, order, product, unit):
    return models.SubOrder(product=product, spec=spec, type=type,
                           weight=weight,
                           harbor=harbor, order=order, quantity=count,
                           order_type=constants.EXTRA_ORDER_TYPE,
                           unit=unit)


@step(u"生成工单(\d+), 重量是(\d+)KG")
@committed
def _(step, seq, weight, sub_order, procedure, team):
    wc = models.WorkCommand(sub_order, org_weight=int(weight),
                            org_cnt=int(int(weight) * sub_order.quantity / sub_order.weight),
                            processed_weight=weight, processed_cnt=weight,
                            procedure=procedure, team=team)
    return wc


@step(u"对工单(\d+)生成质检单(\d+), 结果是全部质检通过")
@committed
def _(step, wc_seq, qir_seq, work_command):
    return models.QIReport(work_command, work_command.org_cnt,
                           work_command.org_weight,
                           constants.quality_inspection.FINISHED, 0)


@step(u'生成发货会话, 车牌号是"(.+)", 皮重是(\d+)公斤')
@committed
def _(step, plate, tare):
    return models.DeliverySession(plate=plate, tare=tare)


@step(u'根据质检单(\d+)生成仓单(\d+), 将其加入发货会话')
@committed
def _(step, qir_seq, sb_seq, qir, delivery_session, harbor):
    ret = models.StoreBill(qir)
    ret.harbor = harbor
    ret.delivery_session = delivery_session
    return ret

@step(u"创建一个发货任务, 选择的仓单全部发货")
def _(step, delivery_session, finished_store_bill_list, unfinished_store_bill=None):
    dt = models.DeliveryTask(delivery_session, actor_id=1)
    from lite_mms.utilities import do_commit

    do_commit(dt)
    for sb in finished_store_bill_list:
        sb.delivery_task_id = dt.id
    do_commit(dt)
    return dt

@step(u"对发货任务进行称重，重量为(\d+)公斤")
def _(step, weight, delivery_task):
    from lite_mms.apis.delivery import get_delivery_task
    delivery_task = get_delivery_task(delivery_task.id)
    delivery_task.update(weight = int(weight)- delivery_task.delivery_session.tare)
    return delivery_task


@step(u"生成发货单")
def _(step, delivery_session, customer, username, password):
    from lite_mms.basemain import app

    with app.test_request_context():
        with app.test_client() as c:
            rv = c.post(url_for("auth.login"),
                        data={"username": username, "password": password})
            assert 302 == rv.status_code
            rv = c.post(url_for('delivery.consignment'),
                        data={"customer": customer.id, "pay_mod": 0,
                              "delivery_session_id": delivery_session.id})
            assert 302 == rv.status_code
            from lite_mms.apis.delivery import get_delivery_session
            delivery_session = get_delivery_session(delivery_session.id)
            for consignment in delivery_session.consignment_list:
                if consignment.customer_id == customer.id:
                    return consignment

@step(u"发货单只有一个产品")
def _(step, consignment, product):
    from lite_mms.apis.delivery import get_consignment
    consignment = get_consignment(consignment.id)
    assert len(consignment.product_list)
    assert consignment.product_list[0].product.id == product.id

@step(u"发货单产品重量为两仓单重量之和")
def _(step, consignment, sb1, sb2):
    from lite_mms.apis.delivery import get_consignment
    consignment = get_consignment(consignment.id)
    assert consignment.product_list[0].weight == sb1.weight +sb2.weight
    assert consignment.product_list[0].quantity == sb1.quantity + sb2.quantity


@step(u"发货单产品的规格是(.+), 型号是(.+)")
def _(step, spec, type, consignment):
    from lite_mms.apis.delivery import get_consignment
    consignment = get_consignment(consignment.id)
    assert spec == consignment.product_list[0].spec
    assert type == consignment.product_list[0].type

@step(u"发货单的总重是发货任务的重量")
def _(step, consignment, dt):
    from lite_mms.apis.delivery import get_consignment
    consignment = get_consignment(consignment.id)
    assert dt.weight == sum(p.weight for p in consignment.product_list)
    assert dt.returned_weight == sum(p.returned_weight for p in consignment.product_list)
    assert dt.quantity == sum(p.quantity for p in consignment.product_list)

@step(u"发货单产品的数量是20桶")
def _(step, consignment):
    from lite_mms.apis.delivery import get_consignment
    consignment = get_consignment(consignment.id)
    assert 20 == sum(p.quantity for p in consignment.product_list)
    assert u"桶" == consignment.product_list[0].unit

@step(u"修改发货单产品的重量")
def _(step, consignment, weight, username, password):
    from lite_mms.basemain import app

    with app.test_request_context():
        with app.test_client() as c:
            rv = c.post(url_for("auth.login"),
                        data={"username": username, "password": password})
            assert 302 == rv.status_code
            rv = c.post(url_for("delivery.consignment", id_=consignment.id),
                        data={
                        "consignment_product_id": consignment.product_list[
                            0].id, "weight": weight,
                        'product_id': consignment.product_list[0].product.id,
                        'weight': 9000,
                        'team_id': consignment.product_list[0].team.id,
                        'returned_weight': 0, 'type': u'测试', 'spec': u'测试',
                        'unit': u'桶'})

            assert 302 == rv.status_code

@step(u"发货单产品的重量改变")
def _(step, consignment, weight):
    from lite_mms.apis.delivery import get_consignment
    consignment = get_consignment(consignment.id)
    assert weight == sum(p.weight for p in consignment.product_list)


@step(u"发货任务的重量保持不变")
def _(step, delivery_task, weight):
    from lite_mms.apis.delivery import get_delivery_task
    delivery_task = get_delivery_task(delivery_task.id)
    assert weight != delivery_task.weight

