# -*- coding: UTF-8 -*-
from hashlib import md5
from datetime import datetime

from flask import url_for
from pyquery import PyQuery

from lite_mms.basemain import app
import lite_mms.apis as apis
from pyfeature import step, Twill
from lite_mms.utilities.decorators import committed
from lite_mms import models
from lite_mms.utilities import do_commit
import nose.tools as assert_tools

@step(u'创建一个车间(.*)')
@committed
def _(step, department_name):
    return models.Department(department_name)

@step(u"创建一个装卸点(.+)")
@committed
def _(step, harbor_name, department):
    return models.Harbor("harbor_name", department)

@step(u'创建一个订单, 毛重是(\d+)公斤, 客户是(.+)')
def _(step, gross_weight, customer_name):

    customer = do_commit(models.Customer(customer_name, abbr=customer_name))
    unload_session = do_commit(models.UnloadSession("foo", gross_weight))
    cargo_clerk_group = models.Group("cargo_clerk_group")
    import lite_mms.constants as constants
    cargo_clerk_group.id = constants.groups.CARGO_CLERK
    cargo_clerk_group = do_commit(cargo_clerk_group)
    goods_receipt = do_commit(models.GoodsReceipt(customer, unload_session))
    creator = do_commit(models.User("cc", md5("cc").hexdigest(), [cargo_clerk_group]))
    return do_commit(models.Order(goods_receipt, creator)), creator

@step(u'创建一个产品类型(.+)')
@committed
def _(step, product_type_name):
    return models.ProductType(product_type_name)

@step(u'创建一个计重子订单, 重量是(\d+)公斤, 产品是(.+)')
@committed
def _(step, weight, product_name, order, department, product_type, harbor):

    product = do_commit(models.Product(product_name, product_type))
    sub_order = models.SubOrder(product, weight, harbor, order, 
                                quantity=weight, unit="KG")
    return sub_order

@step(u'完善子订单')
@committed
def _(step, sub_order):
    sub_order.due_time = datetime.today()
    return sub_order

@step(u'创建一个调度员')
@committed
def _(step):
    scheduler_group = models.Group("scheduler_group")
    import lite_mms.constants as constants
    scheduler_group.id = constants.groups.SCHEDULER
    do_commit(scheduler_group)
    return models.User("s", md5("s").hexdigest(), [scheduler_group])

@step(u"订单列表为空")
def _(step): 
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.post(url_for("auth.login"), 
                        data=dict(username='s', 
                                  password="s"))
            rv = c.get(url_for("schedule.order_list"))
            from pyquery import PyQuery
            dom = PyQuery(rv.data)
            tr_list = dom("#order_list_table > tbody > tr")
            assert not tr_list

@step(u'将订单下发')
def _(step, order):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.post(url_for("auth.login"), 
                        data=dict(username="cc",
                                  password="cc"))
            rv = c.post(url_for("order.order_list"), data=dict(order_id=order.id, act="dispatch")) 
    
@step(u"可以获取一个(.+)类型的订单, 这个订单有两个子订单")
def _(step, order_type, order, user):
    order = apis.order.OrderWrapper(order)
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.post(url_for("auth.login"), 
                        data=dict(username="s",
                                  password="s"))
            rv = c.get(url_for("schedule.order", id_=order.id))
            assert_tools.assert_equal(rv.status_code, 200)
            pq = PyQuery(unicode(rv.data, "utf-8"))
            order_fields = [PyQuery(div) for div in pq("#order_info > div")]
            assert_tools.assert_equal(order_fields[0].children("span").text(), 
                                      order.customer_order_number)  
            assert_tools.assert_equal(order_fields[1].children("span").text(),
                                     order.customer.name)
            assert_tools.assert_equal(order_fields[2].children("span").text(), 
                                      str(order.create_time))
            assert_tools.assert_equal(int(order_fields[3].children("span").text()),
                                     order.net_weight)
            assert_tools.assert_equal(int(order_fields[4].children("span").text()),
                                     order.remaining_weight)
            assert_tools.assert_equal(int(order_fields[5].children("span").text()),
                                     order.todo_work_cnt)
            assert_tools.assert_equal(order_fields[6].children("span").text(),
                                      u"是" if order.urgent else u"否")
            tr_list = [PyQuery(tr) for tr in pq("#sub_order_table > tbody > tr")]
            assert len(tr_list) == 2
            # 检查子订单 
            if order_type == u"计重":
                for tr, sub_order in zip(tr_list, order.sub_order_list):
                    td_list = [PyQuery(td) for td in tr.children("td")]
                    assert int(td_list[0].text()) == sub_order.id
                    assert td_list[1].text() == sub_order.product.name
                    assert td_list[2].text() == u"是" if sub_order.urgent else u"否"
                    assert td_list[3].text() == str(sub_order.due_time.date())
                    assert int(td_list[4].text()) == sub_order.weight
                    assert td_list[5].text() == u"否"
                    assert int(td_list[6].text()) == 0
                    assert td_list[7].text() == "%d(%s)" % (sub_order.remaining_quantity, sub_order.unit)
                    assert td_list[8].text() == sub_order.tech_req
                    assert td_list[9].text() == sub_order.harbor.name
                    assert td_list[10].children("a").text().strip() == u"预排产"
            else: # 计件
                for tr, sub_order in zip(tr_list, order.sub_order_list):
                    td_list = [PyQuery(td) for td in tr.children("td")]
                    assert int(td_list[0].text()) == sub_order.id
                    assert td_list[1].text() == sub_order.product.name
                    assert td_list[2].text() == u"是" if sub_order.urgent else u"否"
                    assert td_list[3].text() == str(sub_order.due_time.date())
                    assert int(td_list[4].text()) == sub_order.weight
                    assert int(td_list[5].text()) == sub_order.quantity
                    assert td_list[6].text() == sub_order.unit
                    assert td_list[7].text() == u"否"
                    assert int(td_list[8].text()) == 0
                    assert td_list[9].text() == "%d(%s)" % (sub_order.remaining_quantity, sub_order.unit)
                    assert td_list[10].text() == sub_order.tech_req
                    assert td_list[11].text() == sub_order.harbor.name
                    assert td_list[12].children("a").text().strip() == u"预排产"

@step(u"订单列表中包含此订单")
def _(step, order, user):
    from lite_mms.basemain import app
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.post(url_for("auth.login"), 
                        data=dict(username=user.username, 
                                  password="s"))
            rv = c.get(url_for("schedule.order_list"))
            pq = PyQuery(unicode(rv.data, "utf-8"))
            tr_list = pq("#order_list_table > tbody > tr")
            assert len(tr_list) == 1
            td_list = PyQuery(tr_list[0]).find("td")
            # order number
            assert PyQuery(td_list[0]).children("a").text() == order.customer_order_number
            # customer name
            assert td_list[1].text == order.goods_receipt.customer.name
            assert td_list[2].text == str(order.create_time)
            # net weight
            order = apis.order.OrderWrapper(order)
            assert int(td_list[3].text) == order.net_weight
            # remainning weight
            assert int(td_list[4].text) == order.remaining_weight

@step(u'创建一个工序(.+)')
@committed
def _(step, procedure_name, department):
    return models.Procedure(procedure_name, [department])

@step(u'对子订单(\d+)进行预排产(\d+)公斤')
def _(step, sub_order_seq, weight, sub_order, procedure):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.post(url_for("auth.login"), 
                        data=dict(username="s", 
                                  password="s"))
            param_dict = dict(id=sub_order.id,
                              order_id=sub_order.order.id,
                              schedule_weight=weight,
                              procedure=procedure.id, 
                              tech_req=u"good good study", 
                              urgent=1)
            rv = c.post(url_for("schedule.work_command"), data=param_dict, follow_redirects=True)
            assert rv.status_code == 200

@step(u'子订单(\d+)未预排产的重量是(\d+)公斤')
def _(step, sub_order_seq, weight, sub_order):
    assert apis.order.SubOrderWrapper(sub_order).remaining_weight == int(weight)

@step(u"子订单(\d+)生产中的重量是(\d+)公斤")
def _(step, sub_order_seq, weight, sub_order):
    assert apis.order.SubOrderWrapper(sub_order).manufacturing_weight == int(weight)

@step(u'生成了新工单, 这个工单的状态是([^,]+), 重量(\d+)公斤')
def _(step, status_name, weight, sub_order, procedure):
    """
    测试了工单排产的页面
    """
    sub_order = apis.order.SubOrderWrapper(sub_order)
    with app.test_request_context():
        with Twill(app) as t:
            t.browser.go(t.url(url_for("manufacture.work_command_list")))
            pq = PyQuery(t.browser.get_html().decode("utf-8"))
            tr_list = pq("table > tbody > tr")
            assert len(tr_list) == 1
            tr = PyQuery(tr_list[0])
            td_list = [PyQuery(td) for td in tr.children("td")]
            assert int(td_list[2].text()) == sub_order.id
            assert td_list[3].text() == sub_order.order.customer_order_number
            assert td_list[4].text() == sub_order.product.name
            assert td_list[6].text() == "%s(%s)" % (weight, sub_order.unit)
            assert td_list[7].text() == sub_order.customer.name
            assert td_list[8].text() == sub_order.harbor.name
            assert td_list[9].text() == u'是'
            assert td_list[10].text() == procedure.name
            assert not td_list[11].text()
            assert td_list[12].text() == status_name
            assert not td_list[13].text()
            assert not td_list[14].text()
            assert td_list[15].text() == u"正常加工"

@step(u'订单未预排产重量是(\d+)公斤')
def _(step, weight, order):
    order = apis.order.OrderWrapper(order)
    assert order.remaining_weight == int(weight)

@step(u'订单的生产中重量是(\d+)公斤')
def _(step, weight, order):
    order = apis.order.OrderWrapper(order)
    assert order.manufacturing_weight == int(weight)
    # 测试页面order.order_list
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.post(url_for("auth.login"), 
                        data=dict(username="cc", 
                                  password="cc"))
            rv = c.get(url_for("order.order_list", category="all"))
            pq = PyQuery(rv.data)
            tr_list = [PyQuery(tr) for tr in pq("#order_list_table > tbody > tr")] 
            tr = [tr for tr in tr_list if tr("td:first > a").text() == order.customer_order_number][0]
            td_list = [PyQuery(td) for td in tr("td")]
            td_list[6].children("a").text() == weight + u"(公斤)"

@step(u'创建一个计件子订单, 重量是(\d+)公斤, 个数是(\d+), 单位是(.+), 产品是(.+)')
@committed
def _(step, weight, quantity, unit, product_name, order, department, product_type, harbor):
    from lite_mms import constants
    product = do_commit(models.Product(product_name, product_type))
    sub_order = models.SubOrder(product, weight, harbor, order, 
                                order_type=constants.EXTRA_ORDER_TYPE,
                                quantity=quantity, unit=unit)
    return sub_order

@step(u'对子订单(\d+)进行预排产(\d+)件')
def _(step, sub_order_seq, quantity, sub_order, procedure):
    with app.test_request_context():
        with app.test_client() as c:
            rv = c.post(url_for("auth.login"), 
                        data=dict(username="s", 
                                  password="s"))
            param_dict = dict(id=sub_order.id,
                              order_id=sub_order.order.id,
                              schedule_weight=quantity * int(sub_order.weight / sub_order.quantity),
                              schedule_count=quantity,
                              procedure=procedure.id, 
                              tech_req=u"good good study", 
                              urgent=1)
            rv = c.post(url_for("schedule.work_command"), data=param_dict, follow_redirects=True)
            assert rv.status_code == 200

@step(u'子订单(\d+)未预排产的数量是(\d+)件, 重量是(\d+)公斤')
def _(step, sub_order_seq, quantity, weight, sub_order):
    pass

@step(u'子订单(\d+)生产中的数量是(\d+)件, 重量是(\d+)公斤')
def _(step, sub_order_seq, quantity, weight, sub_order):
    pass

@step(u'生成了新工单, 这个工单的状态是(.+), 数量是(\d+)件, 重量(\d+)公斤')
def _(step, status_name, quantity, weight, sub_order, procedure):
    """
    测试了工单排产的页面
    """
    sub_order = apis.order.SubOrderWrapper(sub_order)
    with app.test_request_context():
        with Twill(app) as t:
            t.browser.go(t.url(url_for("manufacture.work_command_list")))
            pq = PyQuery(t.browser.get_html().decode("utf-8"))
            tr_list = pq("table > tbody > tr")
            assert len(tr_list) == 1
            tr = PyQuery(tr_list[0])
            td_list = [PyQuery(td) for td in tr.children("td")]
            assert int(td_list[2].text()) == sub_order.id
            assert td_list[3].text() == sub_order.order.customer_order_number
            assert td_list[4].text() == sub_order.product.name
            assert int(td_list[5].text()) == int(weight)
            assert td_list[6].text() == "%s(%s)" % (quantity, sub_order.unit)
            assert td_list[7].text() == sub_order.customer.name
            assert td_list[8].text() == sub_order.harbor.name
            assert td_list[9].text() == u'是'
            assert td_list[10].text() == procedure.name
            assert not td_list[11].text()
            assert td_list[12].text() == status_name
            assert not td_list[13].text()
            assert not td_list[14].text()
            assert td_list[15].text() == u"正常加工"
