# -*- coding: UTF-8 -*-
"""
这里是test_cargo.py 的具体实现。
"""
from flask import g
from pyfeature import *

from lite_mms import models
from lite_mms.basemain import app, timeline_logger
from lite_mms.database import db
from lite_mms.utilities import do_commit

#patch logger
timeline_logger.handlers = []
app.config["CSRF_ENABLED"] = False


def refresh(obj):
    return db.session.query(obj.__class__).filter(obj.__class__.id == obj.id).one()


@step(u"收发员创建UnloadSession， 毛重是(\d+)公斤")
def _(step, weight, plate_):
    return do_commit(models.UnloadSession(plate_=plate_, gross_weight=weight))


@step(u"装卸工进行卸货，该货物来自(.+)")
def _(step, customer_name, customer, harbor, product, us, is_last):
    from lite_mms.constants.cargo import STATUS_WEIGHING

    us.status = STATUS_WEIGHING
    return do_commit(models.UnloadTask(customer=customer, unload_session=us, harbor=harbor, creator=None, pic_path="",
                                       product=product, is_last=is_last))


@app.before_request
def patch():
    """
    needn't login in
    """
    g.identity.can = lambda p: True


@step(u"收发员称重(\d+)公斤")
def _(step, weight, unload_task):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.post("/cargo/weigh-unload-task/%d" % unload_task.id,
                        data={"weight": weight, "product_type": 1, "product": 1})
            assert 302 == rv.status_code


@step(u"卸货任务的重量是(\d+)公斤")
def _(step, weight, ut):
    ut = refresh(ut)
    assert ut.weight == int(weight)


@step(u"卸货会话已经关闭")
def _(step, us):
    us = refresh(us)
    from lite_mms.constants.cargo import STATUS_CLOSED

    assert STATUS_CLOSED == us.status


@step(u"收发员生成收货单")
def _(step, us):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.post("/cargo/unload-session/%d" % us.id, data={"action": u"生成收货单"})
            assert 302 == rv.status_code
            return db.session.query(models.GoodsReceipt).filter(models.GoodsReceipt.unload_session_id == us.id).all()


@step(u"该收货单中包含一个项目，该项目的客户是(.+), 项目的重量是(\d+)公斤")
def _(step, customer_name, weight, gr_list):
    assert 1 == len(gr_list)
    assert customer_name == gr_list[0].customer.name
    assert int(weight) == sum(entry.weight for entry in gr_list[0].goods_receipt_entries)


@step(u"装卸工此时不能进行卸货")
def _(step, us):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.get("/cargo_ws/unload-session-list")
            from flask import json

            assert not [i for i in json.loads(rv.data)["data"] if not i["isLocked"]]


@step(u"卸货会话没有关闭")
def _(step, us):
    us = refresh(us)
    from lite_mms.constants.cargo import STATUS_CLOSED

    assert STATUS_CLOSED != us.status


@step(u"该会话中包含两个项目")
def _(step, gr_list):
    assert 2 == len(gr_list)


@step(u"项目的客户是(.+), 项目的重量是(\d+)公斤")
def _(step, customer_name, weight, gr):
    assert customer_name == gr.customer.name
    assert int(weight) == sum(entry.weight for entry in gr.goods_receipt_entries)