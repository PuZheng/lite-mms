# -*- coding: UTF-8 -*-
"""
关于订单的集成测试
"""
from hashlib import md5
from flask import url_for
from lite_mms import constants
from lite_mms.basemain import app
from lite_mms.test import BaseTest
from lite_mms.constants import groups
from lite_mms.apis import order, manufacture, quality_inspection, cargo
from datetime import datetime
from lite_mms.models import *
import time

class TestOrder(BaseTest):
    def prepare_data(self):
        session = self.db.session
        product_type = ProductType(name=u"测试类型")
        session.add(product_type)
        session.commit()
        product1 = Product(name=u'产品1', product_type=product_type)
        product2 = Product(name=u'产品2', product_type=product_type)
        product3 = Product(name=u'产品3', product_type=product_type)
        self.product = Product(name=u'测试用', product_type=product_type)
        session.add_all([product1, product2, product3, self.product])
        session.commit()

        schedule_group = Group("schedule_group")
        schedule_group.id = groups.SCHEDULER
        cargo_group = Group("cargo")
        cargo_group.id = groups.CARGO_CLERK
        department_leader_group = Group("department_leader_group")
        department_leader_group.id = groups.DEPARTMENT_LEADER
        team_leader_group = Group("team_leader_group")
        team_leader_group.id = groups.TEAM_LEADER
        qi_group = Group("qi")
        qi_group.id = groups.QUALITY_INSPECTOR
        session.add_all(
            [schedule_group, department_leader_group, team_leader_group,
             qi_group, cargo_group])
        self.department = Department("department_foo")
        session.add(self.department)
        session.commit()

        self.procedure = Procedure("procedure", [self.department])
        self.db.session.add(self.procedure)
        self.db.session.commit()
        self.cargo = User(username="cc", password=md5("cc").hexdigest(),
                          groups=[cargo_group])
        self.scheduler = User(username="s", password=md5("s").hexdigest(),
                              groups=[schedule_group])
        self.department_leader = User(username="dl",
                                      password=md5("dl").hexdigest(),
                                      groups=[department_leader_group],
                                      tag=str(self.department.id))
        self.team_leader = User(username="tl", password=md5("tl").hexdigest(),
                                groups=[team_leader_group])
        self.qi = User(username="qi", password=md5("qi").hexdigest(),
                       groups=[qi_group])
        session.add_all([self.scheduler, self.department_leader, self.qi])
        session.commit()

        self.team = Team("team_foo", self.department, self.team_leader)
        session.add(self.team)
        session.commit()

        self.customer1 = Customer(name=u"客户001", abbr="c1")
        self.customer2 = Customer(name=u"客户002", abbr="c2")
        session.add_all([self.customer1, self.customer2])
        session.commit()

        self.us1 = UnloadSession(plate=u"浙B 11111", gross_weight=5000)
        session.add(self.us1)
        session.commit()

        harbor = Harbor(u"卸货点1", self.department)
        session.add(harbor)
        session.commit()
        self.unload_task1 = UnloadTask(self.us1, harbor, self.customer1, None,
                                       product1, pic_path="", weight=1000)
        unload_task2 = UnloadTask(self.us1, harbor, self.customer2, None,
                                  product2, pic_path="", weight=2000)
        unload_task3 = UnloadTask(self.us1, harbor, self.customer1, None,
                                  product3, pic_path="", weight=2000)

        session.add_all([self.unload_task1, unload_task2, unload_task3])
        session.commit()

    def test(self):
        with app.test_request_context():
            with app.test_client() as c:
                app.preprocess_request()
                rv = c.post(url_for("auth.login"),
                            data=dict(username="cc", password="cc"))
                assert rv.status_code == 302

                rv = c.post("/cargo/goods-receipt",
                            data=dict(customer=self.customer1.id,
                                      unload_session_id=self.us1.id,
                                      order_type=STANDARD_ORDER_TYPE))
                assert 302 == rv.status_code
                rv = c.post("/cargo/goods-receipt",
                            data=dict(customer=self.customer2.id,
                                      unload_session_id=self.us1.id,
                                      order_type=STANDARD_ORDER_TYPE))
                assert 302 == rv.status_code
                _list = cargo.get_goods_receipts_list(self.us1.id)
                assert 2 == len(_list)
                self.goods_receipt1 = _list[0]
                self.goods_receipt2 = _list[1]
                ord_list, count = order.get_order_list()
                assert count == 2
                order1, order2 = ord_list
                assert self.product.id not in [s.product_id for s in
                                               order1.sub_order_list]
                rv = c.post("/cargo/ajax/goods-receipt",
                            data=dict(task_id=self.unload_task1.id,
                                      product_id=self.product.id))
                assert 200 == rv.status_code
                ord_list, count = order.get_order_list()
                assert count == 2
                order1, order2 = ord_list
                assert self.product.id in [s.product_id for s in
                                           order1.sub_order_list]
                assert order1.customer_order_number == self.goods_receipt1\
                .receipt_id
                assert order2.customer_order_number == self.goods_receipt2\
                .receipt_id
                assert order1.customer.name == self.customer1.name
                assert order2.customer.name == self.customer2.name
                assert order1.net_weight == order1.remaining_weight ==\
                       order1.remaining_quantity == 3000
                assert order2.net_weight == order2.remaining_weight ==\
                       order2.remaining_quantity == 2000
                assert order1.manufacturing_weight == order1\
                .delivered_weight == order1.to_deliver_weight == 0
                assert order2.manufacturing_weight == order2\
                .delivered_weight == order2.to_deliver_weight == 0

                # let order1 be refined
                assert len(order1.sub_order_list) == 2
                sub_order1 = order1.sub_order_list[0]
                assert sub_order1.unload_task.product == sub_order1.product

                sub_order2 = order1.sub_order_list[1]
                assert sub_order2.unload_task.product == sub_order2.product

                assert 1000 == sub_order1.weight == sub_order1.unload_task.weight
                assert 2000 == sub_order2.weight == sub_order2.unload_task.weight
                sub_order1.update(
                    due_time=datetime.fromtimestamp(time.time()).strftime(
                        "%Y-%m-%d"))
                sub_order2.update(
                    due_time=datetime.fromtimestamp(time.time()).strftime(
                        "%Y-%m-%d"))
                order1.update(dispatched=1)
                order_list, count = order.get_order_list(
                    undispatched_only=True)
                assert count == 1
                assert order1.id not in [o.id for o in order_list]

                # * let order1 be manufactured
                #     - pre schedule
                procedure = self.db.session.query(Procedure).first()
                wc = manufacture.new_work_command(sub_order_id=sub_order1.id,
                                                  org_weight=1000,
                                                  org_cnt=1000,
                                                  procedure_id=procedure.id,
                                                  urgent=False)
                wc2 = manufacture.new_work_command(sub_order_id=sub_order2.id,
                                                   org_weight=2000,
                                                   org_cnt=2000,
                                                   procedure_id=procedure.id,
                                                   urgent=True)
                order_list, count = order.get_order_list()
                order_to_check = order_list[0]
                assert order_to_check.id == order1.id
                assert order_to_check.manufacturing_weight == 3000
                assert order_to_check.remaining_weight == order_to_check\
                .remaining_quantity == 3000 - 3000

                #     - dispatch
                wc.go(actor_id=self.scheduler.id,
                      action=constants.work_command.ACT_DISPATCH,
                      department_id=self.department.id)
                #     - assign
                wc.go(actor_id=self.department_leader.id,
                      action=constants.work_command.ACT_ASSIGN,
                      team_id=self.team.id)
                #     - add weight
                wc.go(actor_id=self.team_leader.id,
                      action=constants.work_command.ACT_ADD_WEIGHT,
                      weight=1000)
                #     - end
                wc.go(actor_id=self.team_leader.id,
                      action=constants.work_command.ACT_END)
                #     - qi
                quality_inspection.new_QI_report(actor_id=self.qi.id,
                                                 work_command_id=wc.id,
                                                 quantity=1000,
                                                 result=constants
                                                 .quality_inspection.FINISHED,
                                                 pic_path="")
                wc.go(actor_id=self.qi.id,
                      action=constants.work_command.ACT_QI)

                # assert order1 could be delivered
                order_list, count = order.get_order_list(deliverable_only=True)
                assert count == 1
                order_to_check = order_list[0]
                assert order_to_check.id == order_to_check.id
                assert order_to_check.to_deliver_weight == 1000
                assert order_to_check.manufacturing_weight == 2000

                wc2.go(actor_id=self.scheduler.id,
                       action=constants.work_command.ACT_DISPATCH,
                       department_id=self.department.id)
                #     - assign
                wc2.go(actor_id=self.department_leader.id,
                       action=constants.work_command.ACT_ASSIGN,
                       team_id=self.team.id)
                #     - add weight
                wc2.go(actor_id=self.team_leader.id,
                       action=constants.work_command.ACT_ADD_WEIGHT,
                       weight=2000)
                #     - end
                wc2.go(actor_id=self.team_leader.id,
                       action=constants.work_command.ACT_END)
                #     - qi
                quality_inspection.new_QI_report(actor_id=self.qi.id,
                                                 work_command_id=wc2.id,
                                                 quantity=2000,
                                                 result=constants
                                                 .quality_inspection.FINISHED,
                                                 pic_path="")
                wc2.go(actor_id=self.qi.id,
                       action=constants.work_command.ACT_QI)
                # assert order1 is accountable either
                order_list, count = order.get_order_list(accountable_only=True)
                assert count == 1
                order_to_check = order_list[0]
                assert order_to_check.id == order1.id
                assert order_to_check.to_deliver_weight == 3000
