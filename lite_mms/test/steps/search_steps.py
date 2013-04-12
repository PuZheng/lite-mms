# -*- coding: UTF-8 -*-
"""
@author: Yangminghua
@version: $
"""
# -*- coding: UTF-8 -*-
import random
from flask import url_for
from hashlib import md5
from pyfeature import step
from lite_mms.basemain import app
from lite_mms import models, constants
from lite_mms.utilities.decorators import committed
from pyquery import PyQuery

@step(u"创建用户组'(.+)'")
@committed
def _(step, group_name):
    group = models.Group(name=group_name)
    group.id = constants.groups.CARGO_CLERK
    group.permissions = [models.Permission(name=u'order.view_order')]
    return group


@step(u"创建收发员'(.+)', 密码'(.+)'")
@committed
def _(step, username, password, group):
    return models.User(username=username, password=md5(password).hexdigest(),
                       groups=[group])


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


@step(u"创建新卸货会话,车牌号'(.+)', 毛重'(\d+)'KG")
@committed
def _(step, plate_name, weight):
    return models.UnloadSession(gross_weight=weight, plate=plate_name)


@step(u"创建卸货任务")
@committed
def _(step,  user, us, customer, harbor, product, weight):
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
def _(step, order, product, weight, harbor):
    return models.SubOrder(product=product, weight=weight, harbor=harbor,
                           order=order, quantity=weight, unit=u"KG")


@step(u"完善子订单信息")
@committed
def _(step, sub_order):
    import datetime

    sub_order.due_time = datetime.datetime.now()
    sub_order.tech_req = u"测试用技术"
    return sub_order


@step(u"下发订单")
@committed
def _(step, order):
    order.dispatched = True
    return order


@step(u"预排产")
@committed
def _(step, sub_order, weight, procedure):
    return models.WorkCommand(sub_order=sub_order, org_weight=weight,
                              procedure=procedure, org_cnt=weight)


@step(u"收发员登录，搜索'(.+)'")
def _(step, keywords, user, password):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.post(url_for("auth.login"),
                        data=dict(username=user.username, password=password))
            assert 302 == rv.status_code
            rv = c.get(url_for("search.search", content=keywords))
            assert 200 == rv.status_code
            return unicode(rv.data, 'utf-8')


@step(u"可以搜索卸货会话信息")
def _(step, us, rv):
    d = PyQuery(rv)
    content = u"卸货会话：%s" % us.id
    assert u"卸货会话(1)" == d("a[href='#unload_session_list']").text()
    assert content in d("a").text()


@step(u"可以搜索订单信息")
def _(step, order, rv):
    d = PyQuery(rv)
    assert u"订单(1)" == d("a[href='#order_list']").text()
    assert order.customer_order_number in d("a").text()


@step(u"不能搜索工单信息")
def _(step, wc, rv):
    from pyquery import PyQuery

    d = PyQuery(rv)
    assert not d("a[href='#work_command_list']")
