from flask import url_for
from hashlib import md5
from lite_mms.permissions import permissions
from lite_mms.test import BaseTest
import lite_mms.apis as apis
from lite_mms.constants.work_command import *
from lite_mms.basemain import app
from lite_mms.constants import groups
from lite_mms.models import *

class TestProcess(BaseTest):
    def prepare_data(self):
        product_type = ProductType(name=u"foo")
        self.db.session.add(product_type)
        self.db.session.commit()
        product1 = Product(name=u'foo1', product_type=product_type)
        product2 = Product(name=u'foo2', product_type=product_type)
        product3 = Product(name=u'foo3', product_type=product_type)
        self.db.session.add_all([product1, product2, product3])
        self.db.session.commit()

        for perm in permissions.keys():
            self.db.session.add(Permission(name=perm))
        self.db.session.commit()

        cargo_clerk_group = Group("cargo_clerk")
        cargo_clerk_group.id = groups.CARGO_CLERK
        schedule_group = Group("schedule_group")
        schedule_group.id = groups.SCHEDULER
        schedule_group.permissions = Permission.query.filter(
            Permission.name.like(
                "%schedule_order%")).all() + Permission.query.filter(
            Permission.name.like("work_command%")).all()

        department_leader_group = Group("department_leader_group")
        department_leader_group.id = groups.DEPARTMENT_LEADER
        team_leader_group = Group("team_leader_group")
        team_leader_group.id = groups.TEAM_LEADER
        qi_group = Group("qi")
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

        self.department = Department("department_foo", [self.department_leader])
        self.db.session.add(self.department)
        self.db.session.commit()
        self.team = Team("team_foo", self.department, self.team_leader)
        self.db.session.add(self.team)
        self.db.session.commit()

        self.procedure = Procedure("procedure", [self.department])
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

        harbor = Harbor("foo", self.department)

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

    def test(self):
        with app.test_request_context():
            with app.test_client() as c:
                app.preprocess_request()

                rv = c.post(url_for("auth.login"),
                    data=dict(username="s", password="s"))

                sub_order_list = self.db.session.query(SubOrder).all()
                count = len(sub_order_list)
                for suborder in sub_order_list:
                    rv = c.post(url_for("schedule.work_command"),
                        data=dict(id=suborder.id, order_id=suborder.order.id, schedule_weight=100,
                            procedure=self.procedure.id, urgent=False))
                    assert rv.status_code == 302

                wc_list = self.db.session.query(WorkCommand).filter_by(
                    status=STATUS_DISPATCHING).all()
                assert len(wc_list) == 3
                for workcommand in wc_list:
                    rv = c.post(url_for("manufacture.schedule"),
                        data={"id": workcommand.id,
                            "department_id": self.department.id})
                    assert rv.status_code == 302

                wc1 = wc_list[0]
                rv = c.put(url_for("manufacture_ws.work_command",
                    work_command_id=wc1.id,
                    actor_id=self.department_leader.id,
                    team_id=self.team.id, action=ACT_ASSIGN))
                self.db.session.expire_all()
                wc1 = self.db.session.query(WorkCommand).filter_by(id=wc1.id).one()
                assert wc1.status == STATUS_ENDING

                rv = c.put(url_for("manufacture_ws.work_command",
                    work_command_id=wc1.id,
                    actor_id=self.team_leader.id, weight=100,
                    action=ACT_ADD_WEIGHT, is_finished=1))
                assert rv.status_code == 200
                wc1 = apis.manufacture.WorkCommandWrapper.get_work_command(wc1.id)
                assert wc1.status == STATUS_QUALITY_INSPECTING

                rv = c.post(url_for("manufacture_ws.quality_inspection_report",
                    actor_id=self.qi.id, work_command_id=wc1.id, quantity=100, result=1))
                assert rv.status_code == 200

                rv = c.put(url_for("manufacture_ws.work_command",
                    work_command_id=wc1.id, actor_id=self.qi.id, action=ACT_QI))
                assert rv.status_code == 200

                assert wc1.status == STATUS_FINISHED
                assert wc1.sub_order.to_deliver_weight == 100

