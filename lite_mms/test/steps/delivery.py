# -*- coding: UTF-8 -*-
from hashlib import md5
import json
from flask import url_for
from pyfeature import step
from lite_mms import models
import lite_mms.constants as constants
from lite_mms.database import db
from lite_mms.utilities import do_commit
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

@step(u'生成装卸点"X"')
@committed
def _(step, department):
    return models.Harbor("habor", department)

@step(u'生成工序"镀锌"')
@committed
def _(step, department):
    return models.Procedure(u"镀锌",[department])

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
    return models.GoodsReceipt(customer=customer, unload_session=unload_session)

@step(u"生成订单")
@committed
def _(step, goods_receipt, creator):
    return models.Order(goods_receipt, creator=creator)

@step(u"生成计重类型的子订单, 重量是10000公斤")
@committed
def _(step, harbor, order, unit, product):
    return models.SubOrder(product=product, spec="", type="", weight=10000,
                           harbor=harbor, order=order, quantity=10000, 
                           unit="KG")

@step(u"生成工单(\d+), 重量是(\d+)KG")
@committed
def _(step, seq, weight, sub_order, procedure):
    wc = models.WorkCommand(sub_order, org_weight=weight, org_cnt=weight, 
                            processed_weight=weight, processed_cnt=weight, 
                            procedure=procedure)
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

@step(u'可以获得发货会话, 其车牌号是"(.+)", 皮重是(\d+)公斤')
def _(step, plate, tare, delivery_session):
    from lite_mms.basemain import app
    with app.test_request_context():
        with app.test_client() as c:
            app.preprocess_request()
            rv = c.get(url_for("delivery_ws.delivery_session_list"))
            json_ds_list = json.loads(rv.data)
            assert len(json_ds_list) == 1
            json_ds = json_ds_list[0]
            assert json_ds["sessionID"] == delivery_session.id
            assert json_ds["plateNumber"] == plate
            assert not json_ds["isLocked"]

            rv = c.get(url_for("delivery_ws.delivery_session", id=delivery_session.id))
            assert rv.status_code == 200
            json_ds = json.loads(rv.data)
            assert json_ds["id"] == delivery_session.id
            assert json_ds["plate"] == plate
            return json_ds

@step(u"该发货会话没有锁定")
def _(step, delivery_session):
    from lite_mms.apis.delivery import DeliverySessionWrapper
    assert not DeliverySessionWrapper(delivery_session).is_locked

@step(u'该发货会话下有三个仓单, 正是之前创建的三个仓单')
def _(step, delivery_session_dict, store_bill_list, order, sub_order):
    haystack = [sb["id"] for sb in delivery_session_dict["store_bills"][order.customer_order_number][str(sub_order.id)]]
    for sb in store_bill_list:
        assert sb.id in haystack
    
@step(u'创建一个发货任务, 该发货任务试图按顺序完成上述三个仓单, 车辆已经装满, 但是仍然剩余了1000公斤')
def _(step, store_bills, delivery_session):
    from lite_mms.basemain import app
    with app.test_request_context():
        with app.test_client() as c:
            data = [
                dict(store_bill_id=store_bills[0].id, is_finished=1),
                dict(store_bill_id=store_bills[1].id, is_finished=1),
                dict(store_bill_id=store_bills[2].id, is_finished=0), # 仓单3没有完成
            ]
            rv = c.post(url_for("delivery_ws.delivery_task", sid=delivery_session.id, 
                        is_finished=1, actor_id=1, remain=1000),
                        data=json.dumps(data))
            assert rv.status_code == 200
            json_ret =  json.loads(rv.data)
            assert store_bills[0].id in json_ret["store_bill_id_list"]
            assert store_bills[1].id in json_ret["store_bill_id_list"]
            assert store_bills[2].id not in json_ret["store_bill_id_list"]
            return json_ret["id"], (set(json_ret["store_bill_id_list"]) - set(sb.id for sb in store_bills)).pop()

@step(u'该发货任务包含(.+)')
def _(step, store_bill_id, dt_id, store_bills):
    
    from lite_mms.models import DeliveryTask
    dt = DeliveryTask.query.get(int(dt_id))
    hay_stack = [sb.id for sb in dt.store_bill_list]
    assert all(sb.id in hay_stack for sb in store_bills)

@step(u"生成了一个新的仓单")
def _(step, new_sb_id):
    from lite_mms.apis.delivery import StoreBillWrapper
    return StoreBillWrapper(models.StoreBill.query.filter(models.StoreBill.id==new_sb_id).one())

@step(u"(.+)的状态是(.+)")
def _(step, sb_name, status, store_bill):
    if isinstance(store_bill, db.Model):
        from lite_mms.apis.delivery import StoreBillWrapper
        store_bill = StoreBillWrapper.get_store_bill(store_bill.id)
    if status == u"完成":
        assert store_bill.delivered
    else:
        assert not store_bill.delivered

@step(u"(.+)已经被打印过")
def _(step, sb_name, store_bill):
    assert store_bill.printed

@step(u"(.*)的发货会话是原发货会话")
def _(step, sb_name, store_bill, delivery_session):
	store_bill.ds = delivery_session

@step(u"(.+)的质检报告仍然是(.+)")
def _(step, sb_name, qir_name, store_bill, qir):
    assert store_bill.qir.id == qir.id

@step(u"(.+)的重量是(\d+)公斤")
def _(step, sb_name, weight, store_bill):
    store_bill = models.StoreBill.query.filter(models.StoreBill.id==store_bill.id).one()
    assert store_bill.weight == int(weight)
    assert store_bill.quantity == int(weight)

@step(u"该发货任务称重为30000公斤")
def _(step, delivery_task_id, user):
    from lite_mms.basemain import app
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.post(url_for("auth.login"), 
                        data=dict(username=user.username, 
                                  password='xm'))
            rv = c.post(url_for("delivery.task_modify"), 
                        data={"task_id": delivery_task_id, "weight": 30000}) # tare is 2000

@step(u"生成发货单, 未导入原系统")
def _(step, delivery_session, customer, user):
    from lite_mms.basemain import app

    with app.test_request_context():
        with app.test_client() as c:
            rv = c.post(url_for("auth.login"),
                        data=dict(username=user.username,
                                  password='xm'))
            assert 302 == rv.status_code

            rv = c.post(url_for('delivery.consignment'),
                        data={"customer": customer.id, "pay_mode": 0,
                              "delivery_session_id": delivery_session.id})

            assert 302 == rv.status_code

            import re

            id = re.search("\d+", rv.location.split("?")[0]).group(0)

            from lite_mms.apis.delivery import ConsignmentWrapper
            consignment = ConsignmentWrapper.get_consignment(id)
            consignment.model.MSSQL_ID = None
            do_commit(consignment.model) #强制未导入到原系统
            assert 1 == len(consignment.product_list)
            return consignment


@step(u"发货单中产品的重量已修改")
def _(step, consignment, weight):
    from lite_mms.apis import delivery
    consignment = delivery.get_consignment(consignment.id)
    assert 1 == len(consignment.product_list)
    assert weight == consignment.product_list[0]["weight"]
    assert weight == consignment.delivery_session.delivery_task_list[0].weight

@step(u"修改发货单")
def _(step, consignment, weight, user):
    from lite_mms.basemain import app

    with app.test_request_context():
        with app.test_client() as c:
            rv = c.post(url_for("auth.login"),
                        data=dict(username=user.username,
                                  password='xm'))
            assert 302 == rv.status_code
            rv = c.post("/delivery/consignment/%d" % consignment.id, data={str(
                consignment.delivery_session.delivery_task_list[
                    0].id): weight})
            assert 302 == rv.status_code
            from lite_mms.apis.delivery import ConsignmentWrapper
            consignment = ConsignmentWrapper.get_consignment(consignment.id)
            assert consignment.delivery_session.delivery_task_list[0].weight == weight

@step(u"发货单导入原系统")
def _(step, consignment):
    from lite_mms.apis.delivery import ConsignmentWrapper
    import random
    ConsignmentWrapper.update(consignment.id, MSSQL_ID=random.randint(1,500))



@step(u"修改发货单失败")
def _(step, consignment, weight, user):
    from lite_mms.basemain import app

    with app.test_request_context():
     with app.test_client() as c:
         rv = c.post(url_for("auth.login"),
                     data=dict(username=user.username,
                               password='xm'))
         assert 302 == rv.status_code
         rv = c.post("/delivery/ajax/consignment", data={"task_id":consignment.delivery_session.delivery_task_list[0].id, "weight":weight})
         assert 403 == rv.status_code
         assert u"已导入原系统的发货单不能再修改" == rv.data
