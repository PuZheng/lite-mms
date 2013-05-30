# -*- coding: UTF-8 -*-
from hashlib import md5
from flask import url_for
from bs4 import BeautifulSoup
from lite_mms.basemain import app
from lite_mms.constants import groups
from lite_mms import constants
from test import BaseTest
from lite_mms import models
from pyfeature import Feature, Scenario

class Test(BaseTest):
    def prepare_data(self):
        type = models.ProductType(name=u'测试用类型')
        product1 = models.Product(name=u'类型一', product_type=type)
        product2 = models.Product(name=u'类型二', product_type=type)
        product3 = models.Product(name=constants.DEFAULT_PRODUCT_NAME,
                                  product_type=models.ProductType(
                                      constants.DEFAULT_PRODUCT_TYPE_NAME))
        cargo_clerk = models.Group(name="cargo_clerk")
        cargo_clerk.id = groups.CARGO_CLERK
        d = models.Department(name=u'车间一')
        self.db.session.add(models.Customer(name=u'超级客户', abbr=u'joiasndf'))
        self.db.session.add(models.Harbor(name=u'卸货点一', department=d))
        self.db.session.add(product1)
        self.db.session.add(product2)
        self.db.session.add(product3)
        self.db.session.add(
            models.User(username=u'cc', password=md5(u'cc').hexdigest(),
                        groups=[cargo_clerk]))
        self.db.session.commit()

    def test_cargo(self):
        with app.test_request_context():
            with app.test_client() as c:
                app.preprocess_request()
                rv = c.post(url_for('auth.login'),
                            data=dict(username="cc", password="cc1"))
                assert 403 == rv.status_code

                rv = c.post(url_for("auth.login"),
                            data=dict(username="cc", password="cc"))
                assert 302 == rv.status_code

                plate = u'测试车辆'
                rv = c.post(url_for("cargo.plate"), data={"name": plate})
                assert 302 == rv.status_code

                rv = c.post(url_for('cargo.unload_session'),
                            data={'plate_': plate, 'gross_weight': 5000, "action": u"提交"})
                assert 302 == rv.status_code
                from lite_mms import apis

                assert plate in apis.plate.get_plate_list("unloading")

                unloadSession = apis.cargo.get_unload_session_list(unfinished_only=True)[0][0]
                customer = apis.customer.get_customer_list()[0]
                harbor = apis.harbor.get_harbor_list()[0]
                a = "/cargo_ws/unload-task?actor_id=1&customer_id=%d&harbour"\
                    "=%s&is_finished=1&session_id=%d" % (
                        customer.id, harbor.name, unloadSession.id)
                rv = c.post(a.encode("utf-8"))
                assert 200 == rv.status_code
                unloadSession = apis.cargo.get_unload_session(
                    session_id=unloadSession.id)
                task = unloadSession.task_list[0]
                assert 1 == task.id
                products = apis.product.get_products()
                pro = products["1"][0]
                rv = c.post(url_for('cargo.unload_task', id_=task.id),
                            data={'weight': 5500, 'product': pro["id"]})
                assert 500 == rv.status_code
                rv = c.post(url_for('cargo.unload_task', id_=task.id),
                            data={'weight': 3000, 'product': pro["id"]})
                assert 302 == rv.status_code
                task = apis.cargo.get_unload_task(task.id)
                assert 2000 == task.weight
                rv = c.post(url_for('goods_receipt.goods_receipt'),
                            data={"customer": customer.id, "order_type": 1,
                                  "unload_session_id": task.session_id})
                goods_receipt = apis.cargo.get_goods_receipts_list(task.session_id)[0]
                assert 302 == rv.status_code
                rv = c.post(url_for("goods_receipt.goods_receipt", id_=goods_receipt.id))
                assert 302 == rv.status_code
                ord_list, count = apis.order.get_order_list(
                    undispatched_only=True)
                print count
                assert count == 1
                assert 2000 == ord_list[0].net_weight


def test():
    pass

if __name__ == "__main__":
    test()


