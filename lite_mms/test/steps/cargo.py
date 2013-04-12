# -*- coding: UTF-8 -*-
import random
from flask import url_for
from hashlib import md5

from pyfeature import step
from lite_mms.basemain import app
from lite_mms import models, constants
from lite_mms.utilities.decorators import committed

@step(u"创建用户组'(.+)'")
@committed
def _(step, group_name):
    group = models.Group(name=group_name)
    group.id = constants.groups.CARGO_CLERK
    return group

@step(u"创建收发员'(.+)', 密码'(.+)'")
@committed
def _(step, username, password, group):
    return models.User(username=username, password=md5(password).hexdigest(),
                       groups=[group])

@step(u"登录失败")
def _(step, login_result):
    assert False == login_result


@step(u"登录成功")
def _(step, login_result):
    assert True == login_result


@step(u"创建默认产品")
@committed
def _(step):
    p = models.ProductType(name=constants.DEFAULT_PRODUCT_TYPE_NAME)
    return models.Product(name=constants.DEFAULT_PRODUCT_NAME, product_type=p,
                          MSSQL_ID=random.randint(1, 500))


@step(u"创建产品类型'(.+)'")
@committed
def _(step, type_name):
    return models.ProductType(name=type_name, MSSQL_ID=random.randint(1, 500))


@step(u"创建产品'(.+)'")
@committed
def _(step, product_name, product_type):
    return models.Product(name=product_name, product_type=product_type,
                          MSSQL_ID=random.randint(1, 500))


@step(u"创建车间'(.+)'")
@committed
def _(step, depart_name):
    return models.Department(name=depart_name)


@step(u"创建装卸点'(.+)'")
@committed
def _(step, harbor_name, department):
    return models.Harbor(name=harbor_name, department=department)


@step(u"创建工序'(.+)'")
@committed
def _(step, procedure_name, department):
    return models.Procedure(name=procedure_name, department_list=[department])


@step(u"创建客户'(.+)'")
@committed
def _(step, customer_name):
    return models.Customer(name=customer_name, abbr=customer_name)


@step(u"收发员生成新卸货会话,车牌号'(.+)', 毛重'(\d+)'KG")
def _(step, plate_name, weight, username, password):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.post(url_for("auth.login"), data={"username":username, "password":password})
            assert 302 == rv.status_code

            rv = c.post(url_for("cargo.unload_session"),
                        data=dict(plateNumber=plate_name, grossWeight=weight))
            assert rv.status_code == 302

    us = step.feature.db.session.query(models.UnloadSession).order_by(
        models.UnloadSession.id.desc()).first()
    assert us.plate == plate_name
    assert us.gross_weight == int(weight)
    return us


@step(u"创建新卸货会话,车牌号'(.+)', 毛重'(\d+)'KG")
@committed
def _(step, plate_name, weight):
    return models.UnloadSession(gross_weight=weight, plate=plate_name)


@step(u"装卸工生成新卸货任务")
def _(step, user, us, customer, harbor, is_finished):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.post(url_for("cargo_ws.unload_task", session_id=us.id,
                                harbour=harbor, customer_id=customer.id,
                                is_finished=is_finished, actor_id=user.id))
            if rv.status_code != 200:
                return rv.status_code
    return step.feature.db.session.query(
        models.UnloadTask).filter(
        models.UnloadTask.id == rv.data).one()


@step(u"生成卸货任务成功")
def _(step, result):
    assert isinstance(result, models.UnloadTask)


@step(u"生成卸货任务失败")
def _(step, result_code):
    assert result_code == 403


@step(u"创建卸货任务")
@committed
def _(step, user, us, customer, harbor, product, weight):
    return models.UnloadTask(unload_session=us, harbor=harbor,
                             customer=customer, creator=user, product=product,
                             pic_path="", weight=weight)


@step(u"生成收货单")
@committed
def _(step, unload_session, customer):
    return models.GoodsReceipt(customer=customer,
                               unload_session=unload_session)


@step(u"生成订单")
@committed
def _(step, goods_receipt, user):
    return models.Order(goods_receipt=goods_receipt, creator=user)


@step(u"生成计重类型的子订单")
@committed
def _(step, order, product, weight, harbor, unload_task):
    return models.SubOrder(product=product, weight=weight, harbor=harbor,
                           order=order, quantity=weight, unit=u"KG", unload_task=unload_task)


@step(u"完善子订单信息")
@committed
def _(step, sub_order):
    import datetime

    sub_order.due_time = datetime.datetime.now()
    sub_order.tech_req = u"测试用技术"
    return sub_order


@step(u"收发员修改收货单内产品的重量成功")
def _(step, product, weight, unload_task, username, password):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.post(url_for("auth.login"),
                        data={"username": username, "password": password})
            assert 302 == rv.status_code
            rv = c.post("/cargo/ajax/goods-receipt",
                        data={"task_id": unload_task.id,
                              "product_id": product.id, "weight": weight})
            assert 200 == rv.status_code
            from lite_mms.apis import cargo
            unload_task = cargo.get_unload_task(unload_task.id)
            assert unload_task.product == unload_task.sub_order.product


@step(u"收货单内产品ID为'(\d+)'的产品重量为'(\d+)'")
def _(step, product_id, weight, goods_receipt):
    from  lite_mms.apis import cargo

    goods_receipt = cargo.get_goods_receipt(goods_receipt.id)
    ut = goods_receipt.unload_task_list.next()
    assert ut.product.id== int(product_id)
    assert ut.weight == int(weight)


@step(u"子订单内产品ID为'(\d+)'的产品重量为'(\d+)'")
def _(step, product_id, weight, sub_order):
    from  lite_mms.apis import order

    sub_order = order.get_sub_order(sub_order.id)
    assert sub_order.product.id == int(product_id)
    assert sub_order.weight == int(weight)
    assert sub_order.unload_task.weight == int(weight)


@step(u"下发订单")
@committed
def _(step, order):
    order.dispatched = True
    return order


@step(u"收发员修改收货单内产品的重量失败")
def _(step, product, weight, unload_task, username, password):
    with app.test_request_context():
        with app.test_client() as c:
            #新传入的product不能为原来的product，否则本次修改不意义
            from lite_mms.apis import cargo
            ut = cargo.get_unload_task(unload_task.id)
            assert ut.product.id != product.id, u"新传入的product不能为原来的product，否则本次修改不意义"

            rv = c.post(url_for("auth.login"),
                        data={"username": username, "password": password})
            assert 302 == rv.status_code
            rv = c.post("/cargo/ajax/goods-receipt",
                        data={"task_id": unload_task.id,
                              "product_id": product.id, "weight": weight})
            assert 403 == rv.status_code
            assert u"已下发的订单不能再修改" == unicode(rv.data, "utf-8")

            ut = cargo.get_unload_task(unload_task.id)
            assert ut.product.id != product.id

