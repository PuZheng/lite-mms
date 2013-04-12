# -*- coding: UTF-8 -*-
"""
关于订单的集成测试
"""
from hashlib import md5
from lite_mms import constants
from lite_mms.basemain import app
from lite_mms.models import *
from lite_mms.test import BaseTest
from lite_mms.constants import groups
from lite_mms.apis import order, manufacture, quality_inspection
from flask import url_for
from datetime import  date

class TestOrder(BaseTest):
    def prepare_data(self):
        product_type = ProductType(name=u"foo")
        self.db.session.add(product_type)
        self.db.session.commit()
        product1 = Product(name=u'foo1', product_type=product_type)
        product2 = Product(name=u'foo2', product_type=product_type)
        product3 = Product(name=u'foo3', product_type=product_type)
        self.db.session.add_all([product1, product2, product3])
        self.db.session.commit()

        cargo_clerk_group = Group(name="cargo_clerk")
        cargo_clerk_group.id = groups.CARGO_CLERK
        schedule_group = Group(name="schedule_group")
        schedule_group.id = groups.SCHEDULER
        department_leader_group = Group(name="department_leader_group")
        department_leader_group.id = groups.DEPARTMENT_LEADER
        team_leader_group = Group(name="team_leader_group")
        team_leader_group.id = groups.TEAM_LEADER
        qi_group = Group(name="qi")
        qi_group.id = groups.QUALITY_INSPECTOR
        self.db.session.add_all([cargo_clerk_group, schedule_group, department_leader_group, team_leader_group,
                        qi_group])
        self.db.session.commit()
        self.cargo_clerk = User(username="cc", password=md5("cc").hexdigest(), 
                                groups=[cargo_clerk_group])
        self.scheduler = User(username="s", password=md5("s").hexdigest(), 
                         groups=[schedule_group])
        self.department_leader = User(username="dl", password=md5("dl").hexdigest(),
                                      groups=[department_leader_group])
        self.team_leader = User(username="tl", password=md5("tl").hexdigest(), 
                                groups=[team_leader_group])
        self.qi = User(username="qi", password=md5("qi").hexdigest(),
                       groups=[qi_group])
        self.db.session.add_all([self.scheduler, self.department_leader, self.qi])
        self.db.session.commit()

        self.department = Department(name="department_foo",leader_list= [self.department_leader])
        self.db.session.add(self.department)
        self.db.session.commit()
        self.team = Team(name="team_foo", department=self.department, leader=self.team_leader)
        self.db.session.add(self.team)
        self.db.session.commit()

        self.procedure = Procedure(name="procedure", department_list=[self.department])
        self.db.session.add(self.procedure)
        self.db.session.commit()

        customer1 = Customer(name=u"foo1", abbr="foo1")
        customer2 = Customer(name=u"foo2", abbr="foo2")
        customer3 = Customer(name=u"foo3", abbr="foo3")
        self.db.session.add_all([customer1, customer2, customer3])
        self.db.session.commit()

        unload_session1 = UnloadSession(plate="foo1", gross_weight=999)
        unload_session2 = UnloadSession(plate="foo2", gross_weight=999)
        unload_session3 = UnloadSession(plate="foo3", gross_weight=999)
        self.db.session.add_all([unload_session1, unload_session2, unload_session3])
        self.db.session.commit()

        harbor = Harbor(name="foo", department=self.department)
        #unload_task1 = UnloadTask(unload_session1, harbor, customer1, None, 
                                 #product1, pic_path="", weight=300)
        #unload_task2 = UnloadTask(unload_session2, harbor, customer2, None, 
                                 #product2, pic_path="", weight=300)
        #unload_task3 = UnloadTask(unload_session3, harbor, customer3, None, 
                                 #product3, pic_path="", weight=300)
        #self.db.session.add_all([unload_task1, unload_task2, unload_task3])
        #self.db.session.commit()

        self.goods_receipt1 = GoodsReceipt(customer1, unload_session1)
        self.goods_receipt2 = GoodsReceipt(customer2, unload_session2)
        self.goods_receipt3 = GoodsReceipt(customer3, unload_session3)
        self.db.session.add_all([self.goods_receipt1, self.goods_receipt2, self.goods_receipt3])

        order1 = Order(self.goods_receipt1, creator=self.cargo_clerk)
        order2 = Order(self.goods_receipt2, creator=self.cargo_clerk)
        order3 = Order(self.goods_receipt3, creator=self.cargo_clerk)
        self.db.session.add_all([order1, order2, order3])
        self.db.session.commit()

        sub_order1 = SubOrder(product1, 300, harbor, order1, 300, "KG")
        sub_order2 = SubOrder(product2, 300, harbor, order2, 300, "KG")
        sub_order3 = SubOrder(product3, 300, harbor, order3, 300, "KG")
        self.db.session.add_all([sub_order1, sub_order2, sub_order3])
        self.db.session.commit()

    def _test_get_list(self, c):
        ord_list, count = order.get_order_list()
        assert count == 3
        order1, order2, order3 = ord_list
        assert len(ord_list) == 3
        assert order1.customer_order_number == self.goods_receipt1.receipt_id
        assert order2.customer_order_number == self.goods_receipt2.receipt_id
        assert order3.customer_order_number == self.goods_receipt3.receipt_id
        assert order1.customer.name ==  "foo1"
        assert order2.customer.name ==  "foo2"
        assert order3.customer.name == "foo3"
        assert order1.net_weight == order1.remaining_weight == order1.remaining_quantity == 300
        assert order2.net_weight == order2.remaining_weight == order2.remaining_quantity == 300
        assert order3.net_weight == order3.remaining_weight == order3.remaining_quantity == 300
        assert order1.manufacturing_weight == order1.delivered_weight == order1.to_deliver_weight == 0
        assert order2.manufacturing_weight == order2.delivered_weight == order2.to_deliver_weight == 0
        assert order3.manufacturing_weight == order3.delivered_weight == order3.to_deliver_weight == 0
        assert len(order1.sub_order_list) == len(order2.sub_order_list) == len(order3.sub_order_list) == 1
        
        # 尝试获取未完成订单
        ord_list, count = order.get_order_list(unfinished=True)
        assert count == 0

    def _test_refine(self, c):
        ord_list, count = order.get_order_list()
        order1 = ord_list[0]

        sub_order = order1.sub_order_list[0]
        rv = c.post(url_for("order.sub_order", id_=sub_order.id),
                    data=dict(product=self.db.session.query(Product).first().id,
                              spec="foo_spec",  type="foo_model",
                              tech_req="foo_tech_req", due_time=str(date.today()), 
                              urgent=True, unit="bucket",
                              weight=500, harbor=self.db.session.query(Harbor).first().name))
        assert 302 == rv.status_code

        #sub_order.update(due_time=datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d"))
        order_list, count = order.get_order_list(undispatched_only=True) 
        assert count == 3
        assert order1.id in [o.id for o in order_list]
        rv = c.post(url_for("order.order", id_=order1.id), data=dict(method="refine"))

        # 只有order1是完善的
        for _order in order_list:
            if _order.id == order1.id:
                assert _order.refined
            else:
                assert not _order.refined
        sub_order = order_list[0].sub_order_list[0]
        assert sub_order.product.id == self.db.session.query(Product).first().id
        assert sub_order.spec == "foo_spec"
        assert sub_order.type == "foo_model"
        assert sub_order.tech_req == "foo_tech_req"
        assert sub_order.due_time.date() == date.today()
        assert sub_order.urgent
        assert sub_order.returned is False
        assert sub_order.unit == "bucket"
        assert sub_order.weight == 500
        assert sub_order.harbor.name == self.db.session.query(Harbor).first().name

    def _test_dispatch(self, c):
        ord_list, count = order.get_order_list(undispatched_only=True)
        order1, order2, order3 = ord_list
        # let's dispatch the order
        rv = c.post(url_for("order.order_list"), 
                    data={"order_id": order1.id, 
                          "act": "dispatch", "customer": "foo1"})
        rv = c.post(url_for("order.order_list"), 
                    data={"order_id": order2.id, 
                          "act": "dispatch", "customer": "foo2"})
        rv = c.post(url_for("order.order_list"), 
                    data={"order_id": order3.id, 
                          "act": "dispatch", "customer": "foo3"})
        ord_list, count = order.get_order_list(unfinished=True)
        assert len(ord_list) == 3 and count == 3
        ord_list, count = order.get_order_list(undispatched_only=True)
        assert len(ord_list) == 0 and count == 0

    def _test_schedule(self, c):
        ord_list, count = order.get_order_list()
        order1 = ord_list[0]
        rv = c.post(url_for('auth.login'), data=dict(username="s", password="s"))
        rv = c.post(url_for("schedule.work_command"),
                    data=dict(sub_order_id=order1.sub_order_list[0].id,
                              schedule_weight=100, schedule_count=100,
                              procedure=self.procedure.id,
                              tech_req="not so foo"))
        assert 302 == rv.status_code
        wc_list, total_cnt = manufacture.get_work_command_list(status_list=[constants.work_command.STATUS_DISPATCHING])
        assert total_cnt == 1
        assert len(wc_list) == 1
        self.wc = wc_list[0]
        assert self.wc.org_weight == self.wc.org_cnt == 100
        assert self.wc.unit == "bucket"
        assert self.wc.tech_req == "not so foo"
        assert not self.wc.urgent
        assert self.wc.procedure.name == self.procedure.name
        ord_list, count = order.get_order_list(unfinished=True)
        order1 = ord_list[0]
        print order1.remaining_weight, order1.remaining_quantity
        assert order1.to_work_weight == 100
        assert order1.manufacturing_weight == 0
        assert order1.delivered_weight == 0
        assert order1.to_deliver_weight == 0
        assert order1.remaining_weight == order1.remaining_quantity == 400

    def _test_delivered(self, c):
        #     - dispatch
        self.wc.go(actor_id=self.scheduler.id,
                      action=constants.work_command.ACT_DISPATCH, department_id=self.department.id) 
        #     - assign
        self.wc.go(actor_id=self.department_leader.id, action=constants.work_command.ACT_ASSIGN, 
                      team_id=self.team.id)
        #     - add weight
        self.wc.go(actor_id=self.team_leader.id, action=constants.work_command.ACT_ADD_WEIGHT,
                       weight=300)
        #     - end
        self.wc.go(actor_id=self.team_leader.id, action=constants.work_command.ACT_END) 
        #     - qi
        rv = quality_inspection.new_QI_report(actor_id=self.qi.id, work_command_id=self.wc.id,
                                         quantity=300, result=constants.quality_inspection.FINISHED, pic_path="")
        self.wc.go(actor_id=self.qi.id, action=constants.work_command.ACT_QI)

        # assert order1 could be delivered
        order_list, count = order.get_order_list(deliverable_only=True)
        assert count == 1
        order_to_check = order_list[0]
        for suborder in order_to_check.sub_order_list:
            print suborder.to_deliver_weight
            print len(suborder.store_bill_list)
            for store_bill in suborder.store_bill_list:
                print store_bill.weight
        assert order_to_check.to_deliver_weight == 300
        assert order_to_check.manufacturing_weight == 0

    def test(self):
        with app.test_request_context():
            with app.test_client() as c:
                app.preprocess_request()
                rv = c.post(url_for("auth.login"),
                            data=dict(username="cc", password="cc"))
                assert 302 == rv.status_code

                self._test_get_list(c)
                self._test_refine(c)
                self._test_dispatch(c)
                self._test_schedule(c)
                self._test_delivered(c)
                return


        

