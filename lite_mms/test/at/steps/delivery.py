#-*- coding:utf-8 -*-
import json
from flask import g, _request_ctx_stack
from pyfeature import step
from lite_mms import models, constants
from lite_mms.apis.delivery import DeliverySessionWrapper
from lite_mms.basemain import app, timeline_logger
from lite_mms.utilities import do_commit

timeline_logger.handlers = []

user = None


def generate(times=1):
    from random import choice
    import string

    temp = ""
    for i in range(times):
        temp += choice(string.letters)
    return temp


@app.before_request
def patch():
    """
    needn't login in
    """
    g.identity.can = lambda p: True
    global user
    if not user:
        from lite_mms.apis.auth import UserWrapper

        user = UserWrapper(models.User.query.first())
    _request_ctx_stack.top.user = user


@step(u"收发员创建发货会话")
def _(step, plate, tare):
    return do_commit(models.DeliverySession(plate_=plate, tare=tare))


@step(u"生成StoreBill")
def _(step, customer, harbor, order_type=constants.STANDARD_ORDER_TYPE):
    plate = do_commit(models.Plate(name=generate(5)))
    unload_session = do_commit(models.UnloadSession(plate_=plate, gross_weight=50000))
    product_type = do_commit(models.ProductType(name=generate(5)))
    product = do_commit(models.Product(name=generate(5), product_type=product_type))
    procedure = do_commit(models.Procedure(name=generate(5)))
    goods_receipt = do_commit(models.GoodsReceipt(customer=customer, unload_session=unload_session))
    order = do_commit(models.Order(creator=None, goods_receipt=goods_receipt))
    if order_type == constants.STANDARD_ORDER_TYPE:
        sub_order = do_commit(
            models.SubOrder(harbor=harbor, order=order, product=product, quantity=5000, weight=5000, unit="KG"))
        work_command = do_commit(
            models.WorkCommand(sub_order=sub_order, org_weight=5000, org_cnt=5000, procedure=procedure))
        qir = do_commit(models.QIReport(work_command=work_command, quantity=5000, weight=5000,
                                        result=constants.quality_inspection.FINISHED, actor_id=None))
    else:
        sub_order = models.SubOrder(harbor=harbor, order=order, product=product, quantity=500, weight=5000, unit=u"刀",
                                    order_type=constants.EXTRA_ORDER_TYPE)
        work_command = do_commit(
            models.WorkCommand(sub_order=sub_order, org_weight=5000, org_cnt=500, procedure=procedure))
        qir = do_commit(models.QIReport(work_command=work_command, quantity=500, weight=5000,
                                        result=constants.quality_inspection.FINISHED, actor_id=None))
    return do_commit(models.StoreBill(qir=qir))


@step(u"收发员选择仓单")
def _(step, delivery_session, store_bill_list):
    for store_bill in store_bill_list:
        store_bill.delivery_session = delivery_session
        do_commit(store_bill)


@step(u"装卸工全部装货、完全装货")
def _(step, delivery_session, store_bill):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.post("/delivery_ws/delivery-task?sid=%s&is_finished=1&remain=0&actor_id=1" % delivery_session.id,
                        data=json.dumps([{"store_bill_id": store_bill.id, "is_finished": 1}]))
            assert 200 == rv.status_code


@step(u"收发员生成发货单")
def _(step, delivery_session):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.post("/delivery/create-consignment-list/%s" % delivery_session.id,
                        data={"customer-pay_mod": json.dumps({customer.id: 0 for customer in
                                                   DeliverySessionWrapper(delivery_session).customer_list})})

            assert 302 == rv.status_code