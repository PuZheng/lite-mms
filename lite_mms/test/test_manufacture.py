# -*- coding: utf-8 -*-
"""
you file description here
"""
from hashlib import md5
import json
from flask import url_for
from test import BaseTest
from lite_mms.basemain import app
from lite_mms.utilities import fslice
from lite_mms.models import (GoodsReceipt, Group, Harbor, Department,\
                             UnloadSession, User, Order, SubOrder, Customer,
                             Team, Product, ProductType, WorkCommand,
                             Procedure)
from lite_mms import models
from lite_mms.database import db
from lite_mms import constants
from lite_mms.utilities import do_commit

class Test(BaseTest):
    def prepare_data(self):
        perm = do_commit(models.Permission(name="work_command.schedule_work_command"))
        dl_group = Group(name="department leader")
        dl_group.id = constants.groups.DEPARTMENT_LEADER
        tl_group = Group(name="team_leader")
        tl_group.id = constants.groups.TEAM_LEADER
        scheduler_group = Group(name="scheduler")
        scheduler_group.id = constants.groups.SCHEDULER
        scheduler_group.permissions = [perm]
        self.db.session.add_all([dl_group, scheduler_group, tl_group])
        self.db.session.commit()
        scheduler = User(username="s", password=md5("s").hexdigest(), groups=[scheduler_group])
        self.dl = User(username="dl", password="dl", groups=[dl_group])
        self.tl = User(username="tl", password="tl", groups=[tl_group])
        self.db.session.add_all([scheduler, self.dl, self.tl])
        self.db.session.commit()

        department = Department(name="foo", leader_list=[self.dl])
        self.db.session.add(department)
        self.db.session.commit()

        hr = Harbor(name="habor", department=department)
        c = Customer(name="foo", abbr="foo")
        us = UnloadSession(plate="foo", gross_weight=2000)
        self.team = Team(name="foo", department=department, leader=self.tl)
        self.db.session.add_all([hr, c, us, self.team])
        self.db.session.commit()

        gr = GoodsReceipt(customer=c, unload_session=us)
        o = Order(gr, creator=scheduler)
        pt = ProductType("foo")
        product = Product("foo", pt)
        so1 = SubOrder(product=product, spec="", type="", weight=1000,
                       harbor=hr, order=o, quantity=1000,
                       unit="KG", returned=True)
        so2 = SubOrder(product=product, spec="", type="", weight=1000,
                       harbor=hr, order=o, quantity=10,
                       unit=u"桶", order_type=constants.EXTRA_ORDER_TYPE)
        self.db.session.add_all([gr, o, pt, product, so1, so2])
        self.db.session.commit()

        d1 = Department(name="num1")
        d2 = Department(name="num2")
        procedure = Procedure(name="foo", department_list=[d1, d2])
        self.wc1 = WorkCommand(so1, 1000, procedure)
        self.wc2 = WorkCommand(so2, 1000, procedure, org_cnt=10)
        self.db.session.add_all([self.wc1, self.wc2])
        self.db.session.commit()

    def test(self):
        with app.test_request_context():
            with app.test_client() as c:
                app.preprocess_request()
                from lite_mms.apis import manufacture
                # log in as scheduler
                rv = c.post(url_for("auth.login"),
                            data=dict(username="s", password="s"))
                assert rv.status_code == 302
                # 调度员排产两个工单
                data = dict(procedure=1, tech_req="好好干",
                            urgent=1,
                            department_id=self.dl.department_list[0].id)
                data["id"] = self.wc1.id
                rv = c.post(url_for("manufacture.schedule"), data=data)
                data["id"] = self.wc2.id
                rv = c.post(url_for("manufacture.schedule"), data=data)
                wc1 = manufacture.get_work_command(self.wc1.id)
                wc2 = manufacture.get_work_command(self.wc2.id)
                assert wc1.id == self.wc1.id
                assert wc2.id == self.wc2.id
                assert wc1.org_weight == self.wc1.org_weight
                assert wc1.status == wc2.status == constants.work_command\
                .STATUS_ASSIGNING

                # 车间主任拒绝了第一个工单
                rv = c.put(url_for("manufacture_ws.work_command",
                                   work_command_id=self.wc1.id,
                                   actor_id=self.dl.id,
                                   action=constants.work_command.ACT_REFUSE))
                assert rv.status_code == 200

                # 那么工单一还是在待分配的状态下
                rv = c.get(url_for("manufacture_ws.work_command_list",
                                   status=str(
                                       constants.work_command.STATUS_REFUSED)))
                json_ret = json.loads(rv.data)
                assert json_ret["totalCnt"] == 1
                assert self.wc1.id == json_ret["data"][0]["id"]
                assert json_ret["data"][0]["rejected"] == 1

                # 调度员排产了工单一
                data = dict(procedure=1, tech_req="好好干",
                            urgent=1,
                            department_id=self.dl.department_list[0].id)
                data["id"] = self.wc1.id
                rv = c.post(url_for("manufacture.schedule"), data=data)

                # 车间主任分配了这两个工单
                rv = c.put(url_for("manufacture_ws.work_command",
                                   work_command_id=self.wc1.id,
                                   actor_id=self.dl.id,
                                   team_id=self.team.id,
                                   action=constants.work_command.ACT_ASSIGN))
                assert rv.status_code == 200
                rv = c.put(url_for("manufacture_ws.work_command",
                                   work_command_id=self.wc2.id,
                                   actor_id=self.dl.id,
                                   team_id=self.team.id,
                                   action=constants.work_command.ACT_ASSIGN))
                assert rv.status_code == 200

                # 班组长结转了工单一， 那么工单一回到车间主任处
                rv = c.put(url_for("manufacture_ws.work_command",
                                   work_command_id=self.wc1.id,
                                   actor_id=self.tl.id,
                                   action=constants.work_command
                                   .ACT_CARRY_FORWARD))
                assert rv.status_code == 200

                wc1 = manufacture.get_work_command(id_=self.wc1.id)
                assert wc1.department.name == self.wc1.department.name
                assert not wc1.team
                assert wc1.status == constants.work_command.STATUS_ASSIGNING
                assert wc1.org_cnt == self.wc1.org_cnt
                assert wc1.org_weight == self.wc1.org_weight

                # 车间主任分配工单一
                rv = c.put(url_for("manufacture_ws.work_command",
                                   work_command_id=self.wc1.id,
                                   actor_id=self.dl.id,
                                   team_id=self.team.id,
                                   action=constants.work_command.ACT_ASSIGN))
                assert rv.status_code == 200

                # 调度员回收两个工单
                rv = c.post(url_for("manufacture.retrieve"),
                            data=dict(work_command_id=self.wc1.id))
                rv = c.post(url_for("manufacture.retrieve"),
                            data=dict(work_command_id=self.wc2.id))

                # 车间主任拒绝回收
                rv = c.put(url_for("manufacture_ws.work_command",
                                   work_command_id=self.wc1.id,
                                   actor_id=self.dl.id,
                                   action=constants.work_command
                                   .ACT_REFUSE_RETRIEVAL))
                assert rv.status_code == 200

                rv = c.put(url_for("manufacture_ws.work_command",
                                   work_command_id=self.wc2.id,
                                   actor_id=self.dl.id,
                                   action=constants.work_command
                                   .ACT_REFUSE_RETRIEVAL))
                assert rv.status_code == 200

                # 那么这两个工单仍然在待结束状态
                rv = c.get(url_for("manufacture_ws.work_command_list",
                                   status=str(
                                       constants.work_command.STATUS_ENDING)))
                json_ret = json.loads(rv.data)
                assert json_ret["totalCnt"] == 2
                assert self.wc1.id in [json_wc["id"] for json_wc in
                                       json_ret["data"]]
                assert self.wc2.id in [json_wc["id"] for json_wc in
                                       json_ret["data"]]
                # we assert work command 1 is rejected while work command 2
                # is not,
                # since sub order 1 is rejected
                for json_wc in json_ret["data"]:
                    if json_wc["id"] == self.wc1.id:
                        assert json_wc["rejected"] == 1
                    else:
                        assert json_wc["rejected"] == 0

                # 调度员再次回收这两个工单
                rv = c.post(url_for("manufacture.retrieve"),
                            data=dict(work_command_id=self.wc1.id))
                rv = c.post(url_for("manufacture.retrieve"),
                            data=dict(work_command_id=self.wc2.id))

                # 车间主任确认回收工单一, 但已经完成了900公斤
                rv = c.put(url_for("manufacture_ws.work_command",
                                   work_command_id=self.wc1.id,
                                   actor_id=self.dl.id,
                                   action=constants.work_command
                                   .ACT_AFFIRM_RETRIEVAL,
                                   weight=900))
                print rv.data
                assert rv.status_code == 200
                # 车间主任确认回收工单二, 但已经完成了1100公斤, 完成了8件
                # note wc2 is count by piece
                rv = c.put(url_for("manufacture_ws.work_command",
                                   work_command_id=self.wc2.id,
                                   actor_id=self.dl.id,
                                   action=constants.work_command
                                   .ACT_AFFIRM_RETRIEVAL,
                                   weight=1100,
                                   quantity=8))
                assert rv.status_code == 200
                # we assert that the work commands retrieved should be in state

                rv = c.get(url_for("manufacture_ws.work_command_list",
                                   status=str(
                                       constants.work_command.STATUS_DISPATCHING)))
                assert rv.status_code == 200
                json_ret = json.loads(rv.data)
                assert json_ret["totalCnt"] == 2
                wc1, wc2 = fslice(json_ret["data"],
                                  lambda x: x["id"] == self.wc1.id)
                wc1, wc2 = wc1[0], wc2[0]
                assert wc1["orgWeight"] == wc1["orgCount"] == 100
                assert wc2["orgWeight"] == 1
                assert wc2["orgCount"] == 2
                for wc in [wc1, wc2]:
                    assert not wc["department"]
                    assert not wc["team"]
                # we assert there're 2 work commands waiting qi
                rv = c.get(url_for("manufacture_ws.work_command_list",
                                   status=str(
                                       constants.work_command
                                       .STATUS_QUALITY_INSPECTING)))
                assert rv.status_code == 200
                json_ret = json.loads(rv.data)
                assert json_ret["totalCnt"] == 2
                new_wc1, new_wc2 = fslice(json_ret["data"],
                                          lambda x: x[
                                                    "processedWeight"] == 900)
                new_wc1, new_wc2 = new_wc1[0], new_wc2[0]
                assert new_wc1["orgWeight"] == 900
                assert new_wc1["processedCount"] == 900
                assert new_wc2["processedWeight"] == 1100
                assert new_wc2["processedCount"] == 8
                assert new_wc2["orgWeight"] == 1100
                assert new_wc2["orgCount"] == 8

                fields = ["customerName", "handleType",
                          "isUrgent", "orderID", "orderType", "picPath",
                          "previousProcedure", "procedure", "productName",
                          "subOrderId", "technicalRequirements"]
                for field in fields:
                    assert new_wc1[field] == wc1[field]
                    assert new_wc2[field] == wc2[field]

                # 质检: 300 合格结束，200 合格转下道工序， 200返睹，200 返修
                rv = c.post(url_for("manufacture_ws.quality_inspection_report",
                                    actor_id=1, work_command_id=new_wc1["id"],
                                    quantity=300,
                                    result=constants.quality_inspection.FINISHED))
                assert 200 == rv.status_code

                rv = c.post(url_for("manufacture_ws.quality_inspection_report",
                                    actor_id=1, work_command_id=new_wc1["id"],
                                    quantity=200,
                                    result=constants.quality_inspection.NEXT_PROCEDURE))
                assert 200 == rv.status_code

                rv = c.post(url_for("manufacture_ws.quality_inspection_report",
                                    actor_id=1, work_command_id=new_wc1["id"],
                                    quantity=200,
                                    result=constants.quality_inspection.REPAIR))
                assert 200 == rv.status_code

                rv = c.post(url_for("manufacture_ws.quality_inspection_report",
                                    actor_id=self.dl.id, work_command_id=new_wc1["id"],
                                    quantity=200,
                                    result=constants.quality_inspection.REPLATE))
                assert 200 == rv.status_code
                qir_id = json.loads(rv.data)["id"]

                rv = c.delete(url_for("manufacture_ws.quality_inspection_report",
                                   id=qir_id,
                                   actor_id=self.dl.id))
                assert 200 == rv.status_code

                rv = c.post(url_for("manufacture_ws.quality_inspection_report",
                                    actor_id=self.dl.id, work_command_id=new_wc1["id"],
                                    quantity=200,
                                    result=constants.quality_inspection.REPLATE))
                assert 200 == rv.status_code
                qir_id = json.loads(rv.data)["id"]


                rv = c.put(url_for("manufacture_ws.work_command",
                                   work_command_id=new_wc1["id"],
                                   actor_id=self.dl.id,
                                   action=constants.work_command.ACT_QI,
                                   deduction=400))
                assert 200 == rv.status_code

                rv = c.delete(url_for("manufacture_ws.quality_inspection_report",
                                   id=qir_id,
                                   actor_id=self.dl.id))
                assert 403 == rv.status_code

                rv = c.get(url_for("manufacture_ws.work_command_list",
                                   status=str(
                                       constants.work_command
                                       .STATUS_DISPATCHING)))

                assert rv.status_code == 200
                json_ret = json.loads(rv.data)
                assert json_ret["totalCnt"] == 3
                new_wc3, x = fslice(json_ret["data"],
                                 lambda x: x["orgWeight"] == 200)
                new_wc3 = new_wc3[0]
                assert new_wc3["handleType"] == constants.work_command.HT_NORMAL
                assert new_wc3["procedure"] == ""
                assert new_wc3["previousProcedure"] == new_wc1["procedure"]
                assert new_wc3["department"] == new_wc3["team"] == ""

                rv = c.get(url_for("manufacture_ws.work_command_list",
                                   status=str(
                                       constants.work_command
                                       .STATUS_ASSIGNING)))
                assert rv.status_code == 200
                json_ret = json.loads(rv.data)
                assert json_ret["totalCnt"] == 2
                x, y = fslice(json_ret["data"],
                                          lambda x: x["orgWeight"] == 200)
                new_wc4 , new_wc5 = x
                assert new_wc4[
                           "handleType"] == constants.work_command.HT_REPAIRE
                assert new_wc5[
                           "handleType"] == constants.work_command.HT_REPLATE
                assert new_wc4["previousProcedure"] == new_wc5[
                    "previousProcedure"] == new_wc1["previousProcedure"]
                assert new_wc4["procedure"] == new_wc5["procedure"] == new_wc1[
                    "procedure"]
                assert new_wc4["department"] == new_wc5["department"] == new_wc1["department"] != ''
                assert new_wc4["team"] == new_wc5["team"] == ''

from pyfeature import Feature, Scenario, given, and_, when, then
from lite_mms.database import db

def test():
    from pyfeature import flask_sqlalchemy_setup
    flask_sqlalchemy_setup(app, db, create_step_prefix=u"创建")

    with Feature(u"质检报告提交以后，生成的仓单是打印过的，并根据生产车间自动关联装卸点", 
        ["lite_mms.test.steps.manufacture"]):

        with Scenario(u"准备数据"):
            # prepare data
            unload_session = given(u"创建UnloadSession", plate=u"浙A 12345", gross_weight=2000)
            product_type = and_(u"创建ProductType(紧固件)") 
            product = and_(u"创建Product(螺丝)", product_type=product_type)
            customer = and_(u"创建Customer(宁力)", abbr="nl")
            from lite_mms import constants
            cargo_clerk_group = and_(u"创建Group(收发员)")
            cargo_clerk = and_(u"创建User, 他是一个收发员", username="cc", password="cc", groups=[cargo_clerk_group])
            scheduler_group = and_(u"创建Group(调度员)")
            scheduler = and_(u"创建User, 他是一个调度员", username="s", password="s", groups=[scheduler_group])
            dl_group = and_(u"创建Group(车间主任)")
            dl = and_(u"创建User, 他是一个车间主任", username="dl", password="dl", groups=[dl_group])
            tl_group = and_(u"创建Group(班组长)")
            tl = and_(u"创建User, 他是一个班组长", username=u"tl", password="tl", 
                                groups=[tl_group])
            qi_group = and_(u"创建Group(质检员)")
            qi = and_(u"创建User, 他是一个质检员", username=u"qi", password="qi",
                                groups=[qi_group])
            department = and_(u"创建Department(车间一)")
            team = and_(u"创建Team(班组一)", department=department, leader=tl)
            harbor = and_(u"创建Harbor(装卸点一)", department=department)
            and_(u"创建UnloadTask", unload_session, harbor, customer, cargo_clerk, product, "", weight=10000)
            goods_receipt = and_(u"创建GoodsReceipt", customer, unload_session)
            order = and_(u"创建Order", goods_receipt, cargo_clerk)
            so = and_(u"创建SubOrder-计重类型", product=product, weight=10000, 
                       harbor=harbor, order=order, quantity=10000, unit="KG")
            and_(u"完善子订单", so)
            procedure = and_(u"创建Procedure(镀金)", department_list=[department])
            wc = and_(u"创建WorkCommand", sub_order=so, org_weight=10000, procedure=procedure)
            when(u"下发工单到车间一", wc, cargo_clerk, department)
            and_(u"指派工单到班组一", wc, team, dl)
            and_(u"将工单生产完毕", wc, tl)
            then(u"没新工单完成", wc)

        with Scenario(u"最简单场景"):
            and_(u"质检员将工单全部通过", wc, qi)
            qir = then(u"生成一个新的质检报告", wc)
            sb = and_(u"生成一个新的仓单", qir)
            and_(u"该仓单已经打印过", sb)
            and_(u"该仓单的装卸点是装卸点一", sb, harbor)
        
    from pyfeature import clear_hooks
    clear_hooks()

if __name__ == "__main__":
    test()
