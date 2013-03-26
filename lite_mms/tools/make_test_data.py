# -*- coding: UTF-8 -*-

from hashlib import md5
from random import randint
from datetime import datetime
from flask import url_for
from lite_mms.basemain import app
from lite_mms.permissions import permissions
from lite_mms.constants import groups, work_command as wc_const, \
    quality_inspection, DEFAULT_PRODUCT_NAME, DEFAULT_PRODUCT_TYPE_NAME
from setuptools import Command
from lite_mms.models import *
from lite_mms.utilities import do_commit
from lite_mms.database import db, init_db


class InitializeTestDB(Command):
    def initialize_options(self):
        """init options"""
        pass


    def finalize_options(self):
        """finalize options"""
        pass


    def run(self):
        db.drop_all()
        init_db()
        product_type4 = do_commit(ProductType(name=DEFAULT_PRODUCT_TYPE_NAME))
        product_type1 = do_commit(ProductType(name=u"铁件"))
        product_type2 = do_commit(ProductType(name=u"折扣"))
        product_type3 = do_commit(ProductType(name=u"三角"))

        product4 = do_commit(
            Product(name=DEFAULT_PRODUCT_NAME, product_type=product_type4))
        product1 = do_commit(Product(name=u'紧固件', product_type=product_type1))
        product2 = do_commit(Product(name=u'三角铁', product_type=product_type2))
        product3 = do_commit(Product(name=u'螺丝', product_type=product_type3))

        #init permission
        for perm in permissions.keys():
            do_commit(Permission(name=perm))

        with app.test_request_context():
            app.preprocess_request()
            #init group
            cargo_clerk = Group(u"收发员", url_for("cargo.index"))
            cargo_clerk.id = groups.CARGO_CLERK
            cargo_clerk.permissions = Permission.query.filter(
                Permission.name.like("%view_order%")).all()
            cargo_clerk = do_commit(cargo_clerk)

            scheduler = Group(u"调度员", url_for("schedule.index"))
            scheduler.id = groups.SCHEDULER
            scheduler.permissions = Permission.query.filter(
                Permission.name.like(
                    "%schedule_order%")).all() + Permission.query.filter(
                Permission.name.like("work_command%")).all()
            scheduler = do_commit(scheduler)

            department_leader = Group(u"车间主任", url_for(
                "manufacture.QI_work_command_list"))
            department_leader.id = groups.DEPARTMENT_LEADER
            department_leader = do_commit(department_leader)

            team_leader = Group(u"班组长")
            team_leader.id = groups.TEAM_LEADER
            team_leader = do_commit(team_leader)

            quality_inspector = Group(u"质检员", url_for("store_bill.index"))
            quality_inspector.id = groups.QUALITY_INSPECTOR
            quality_inspector.permissions = Permission.query.filter(
                Permission.name.like("%view_work_command")).all() + Permission.query.filter(Permission.name.like("%deduction")).all()
            quality_inspector = do_commit(quality_inspector)

            loader = Group(u"装卸工")
            loader.id = groups.LOADER
            loader = do_commit(loader)

            accountant = Group(u"财会人员", url_for("delivery.consignment_list"))
            accountant.permissions = [Permission.query.filter(
                Permission.name.like("%export_consignment%")).one()]
            accountant.id = groups.ACCOUNTANT
            accountant = do_commit(accountant)

#            administrator = Group(u"管理员", url_for("admin.index"))
#            administrator.id = groups.ADMINISTRATOR
#            administrator.permissions = Permission.query.all()
#            administrator = do_commit(administrator)

            # init user
            # admin = do_commit(
                # User('admin', md5('admin').hexdigest(), [administrator]))
            cc = do_commit(User('cc', md5('cc').hexdigest(), [cargo_clerk]))
            s = do_commit(User('s', md5('s').hexdigest(), [scheduler]))
            #    -  一号车间
            cj1_dl = do_commit(
                User('cj1', md5('cj1').hexdigest(), [department_leader]))
            #    -  二号车间
            cj2_dl = do_commit(
                User('cj2', md5('cj2').hexdigest(), [department_leader]))
            #    -  三号车间
            cj3_dl = do_commit(
                User('cj3', md5('cj3').hexdigest(), [department_leader]))
            #    -  抛砂车间
            pscj_dl = do_commit(
                User('pscj', md5('pscj').hexdigest(), [department_leader]))
            #    -  整修车间
            zxcj_dl = do_commit(
                User('zxcj', md5('zxcj').hexdigest(), [department_leader]))
            #    -  超级车间主任
            cjcj_dl = do_commit(
                User('cjcj', md5('cjcj').hexdigest(), [department_leader]))
            #    -  101
            _101_tl = do_commit(
                User('101', md5('101').hexdigest(), [team_leader]))
            #    -  201
            _201_tl = do_commit(
                User('201', md5('201').hexdigest(), [team_leader]))
            #    -  202
            _202_tl = do_commit(
                User('202', md5('202').hexdigest(), [team_leader]))
            #    -  203
            _203_tl = do_commit(
                User('203', md5('203').hexdigest(), [team_leader]))
            #    -  301
            _301_tl = do_commit(
                User('301', md5('301').hexdigest(), [team_leader]))
            #    -  302
            _302_tl = do_commit(
                User('302', md5('302').hexdigest(), [team_leader]))
            #    -  401
            _401_tl = do_commit(
                User('401', md5('401').hexdigest(), [team_leader]))
            #    -  501
            _501_tl = do_commit(
                User('501', md5('501').hexdigest(), [team_leader]))

            qi = do_commit(
                User('qi', md5('qi').hexdigest(), [quality_inspector]))
            l = do_commit(User('l', md5('l').hexdigest(), [loader]))
            a = do_commit(User('a', md5('a').hexdigest(), [accountant]))

            # init departments
            d1 = do_commit(Department(u"一号车间", [cj1_dl, cjcj_dl]))
            d2 = do_commit(Department(u"二号车间", [cj2_dl, cjcj_dl]))
            d3 = do_commit(Department(u"三号车间", [cj3_dl, cjcj_dl]))
            d4 = do_commit(Department(u"抛砂车间", [pscj_dl, cjcj_dl]))
            d5 = do_commit(Department(u"整修车间", [zxcj_dl, cjcj_dl]))

            # init teams
            team1 = do_commit(Team(u"101", d1, _101_tl))
            team2 = do_commit(Team(u"201", d2, _201_tl))
            team3 = do_commit(Team(u"202", d2, _202_tl))
            team4 = do_commit(Team(u"203", d2, _203_tl))
            team5 = do_commit(Team(u"301", d3, _301_tl))
            team6 = do_commit(Team(u"302", d3, _302_tl))
            team7 = do_commit(Team(u"401", d4, _401_tl))
            team8 = do_commit(Team(u"501", d5, _501_tl))

            # init procedure
            normal_procedure = do_commit(Procedure(u"一般工序", [d1, d2, d3]))
            paosha_procedure = do_commit(Procedure(u"抛砂", [d4]))
            zhengxiu_procedure = do_commit(Procedure(u"整修", [d5]))

            # init harbors
            hr1 = do_commit(Harbor(u"装卸点1", d1))
            hr2 = do_commit(Harbor(u"装卸点2", d2))
            hr3 = do_commit(Harbor(u"装卸点3", d3))
            hr4 = do_commit(Harbor(u"装卸点4", d4))
            hr5 = do_commit(Harbor(u"装卸点5", d5))

            #init customer
            customer1 = do_commit(Customer(u"宁波机床场", "nbjcc"))
            customer2 = do_commit(Customer(u"宁力紧固件", "nljgj"))
            customer3 = do_commit(Customer(u"宁波造船场", "nbzcc"))
            customer4 = do_commit(Customer(u"宁波飞机场", "nbfjc"))

            plate1 = do_commit(Vehicle(plate=u"浙A 12345"))
            plate2 = do_commit(Vehicle(plate=u"浙A 12344"))
            plate3 = do_commit(Vehicle(plate=u"浙A 12343"))
            plate4 = do_commit(Vehicle(plate=u"浙A 12342"))

            unload_session1 = do_commit(UnloadSession(vehicle=plate1, gross_weight=10000, with_person=True,
                                                      finish_time=datetime.now()))
            unload_task1 = UnloadTask(unload_session1, hr1, customer1, l, product1, "",
                                       weight=300)
            unload_task1 = do_commit(
                UnloadTask(unload_session1, hr1, customer1, l, product1, "",
                           weight=300))

            unload_session2 = do_commit(
                UnloadSession(vehicle=plate2, gross_weight=10000, with_person=False,
                              finish_time=datetime.now()))
            unload_session3 = do_commit(
                UnloadSession(vehicle=plate3, gross_weight=10000, with_person=False,
                              finish_time=datetime.now()))
            unload_session4 = do_commit(
                UnloadSession(vehicle=plate4, gross_weight=10000, with_person=False,
                              finish_time=datetime.now()))
            unload_task1 = do_commit(
                UnloadTask(unload_session1, hr1, customer1, l, product1, "0.png",
                           weight=300))
            unload_task2 = do_commit(
                UnloadTask(unload_session1, hr1, customer1, l, product2, "1.png",
                           weight=600))
            unload_task3 = do_commit(
                UnloadTask(unload_session1, hr1, customer1, l, product3, "2.png",
                           weight=1000))
            unload_task4 = do_commit(
                UnloadTask(unload_session2, hr2, customer2, l, product1, "3.png",
                           weight=4000))
            unload_task5 = do_commit(
                UnloadTask(unload_session2, hr2, customer2, l, product2, "4.png",
                           weight=500))
            unload_task6 = do_commit(
                UnloadTask(unload_session2, hr2, customer2, l, product3, "5.png",
                           weight=500))
            unload_task7 = do_commit(
                UnloadTask(unload_session3, hr1, customer3, l, product1, "6.png",
                           weight=800))
            unload_task8 = do_commit(
                UnloadTask(unload_session3, hr1, customer3, l, product2, "7.png",
                           weight=800))
            unload_task9 = do_commit(
                UnloadTask(unload_session3, hr1, customer3, l, product3, "8.png",
                           weight=800))
            unload_task10 = do_commit(UnloadTask(unload_session4,hr1,customer3,l,product3,"9.png",weight=800))

            goods_receipt1 = do_commit(
                GoodsReceipt(customer1, unload_session1))
            goods_receipt2 = do_commit(
                GoodsReceipt(customer2, unload_session2))
            goods_receipt3 = do_commit(
                GoodsReceipt(customer3, unload_session3))

            order1 = do_commit(
                Order(goods_receipt1, creator=cc, dispatched=True))
            order2 = do_commit(
                Order(goods_receipt2, creator=cc, dispatched=True))
            order3 = do_commit(
                Order(goods_receipt3, creator=cc, dispatched=True))

            sub_order1 = do_commit(
                SubOrder(product1, 300, hr1, order1, 300, "KG",
                         due_time=datetime.today(), unload_task=unload_task1, returned=True))
            sub_order2 = do_commit(
                SubOrder(product2, 600, hr1, order1, 600, "KG",
                         due_time=datetime.today(), unload_task=unload_task2))
            sub_order3 = do_commit(
                SubOrder(product3, 1000, hr1, order1, 1000, "KG",
                         due_time=datetime.today(), unload_task=unload_task3))

            sub_order4 = do_commit(
                SubOrder(product1, 4000, hr2, order2, 4000, "KG",
                         due_time=datetime.today(), unload_task=unload_task4))
            sub_order5 = do_commit(
                SubOrder(product2, 500, hr2, order2, 500, "KG",
                         due_time=datetime.today(), unload_task=unload_task5))
            sub_order6 = do_commit(
                SubOrder(product3, 500, hr2, order2, 500, "KG",
                         due_time=datetime.today(), unload_task=unload_task6))

            sub_order7 = do_commit(
                SubOrder(product1, 800, hr1, order3, 800, "KG",
                         due_time=datetime.today(), unload_task=unload_task7))

            order1.refined = order2.refined = order3.refined = True


            work_command1 = do_commit(WorkCommand(sub_order=sub_order1,
                                                  org_weight=150,
                                                  procedure=normal_procedure,
                                                  tech_req=str(
                                                      randint(1, 10000)),
                                                  urgent=False, org_cnt=150,
                                                  pic_path=""))
            work_command2 = do_commit(WorkCommand(sub_order=sub_order1,
                                                  org_weight=50,
                                                  procedure=normal_procedure,
                                                  tech_req=str(
                                                      randint(1, 10000)),
                                                  urgent=False, org_cnt=50,
                                                  pic_path=""))
            work_command3 = do_commit(WorkCommand(sub_order=sub_order1,
                                                  org_weight=100,
                                                  procedure=normal_procedure,
                                                  tech_req=str(
                                                      randint(1, 10000)),
                                                  urgent=False, org_cnt=100,
                                                  pic_path="",
                                                  status=wc_const
                                                  .STATUS_ASSIGNING,
                                                  department=d1))
            sub_order1.remaining_quantity = 0
            do_commit(sub_order1)

            work_command4 = do_commit(WorkCommand(sub_order=sub_order2,
                                                  org_weight=100,
                                                  procedure=normal_procedure,
                                                  tech_req=str(
                                                      randint(1, 10000)),
                                                  urgent=False, org_cnt=100,
                                                  pic_path="",
                                                  status=wc_const
                                                  .STATUS_ASSIGNING,
                                                  department=d1))
            work_command5 = do_commit(WorkCommand(sub_order=sub_order2,
                                                  org_weight=100,
                                                  procedure=normal_procedure,
                                                  tech_req=str(
                                                      randint(1, 10000)),
                                                  urgent=False, org_cnt=100,
                                                  pic_path="",
                                                  status=wc_const
                                                  .STATUS_ENDING,
                                                  department=d1,
                                                  team=team1))
            work_command6 = do_commit(WorkCommand(sub_order=sub_order2,
                                                  org_weight=150,
                                                  procedure=paosha_procedure,
                                                  tech_req=str(
                                                      randint(1, 10000)),
                                                  urgent=False, org_cnt=150,
                                                  pic_path="",
                                                  status=wc_const
                                                  .STATUS_ENDING,
                                                  department=d4,
                                                  team=team7))
            sub_order2.remaining_quantity = 250
            do_commit(sub_order2)

            work_command7 = do_commit(WorkCommand(sub_order=sub_order3,
                                                  org_weight=200,
                                                  procedure=normal_procedure,
                                                  tech_req=str(
                                                      randint(1, 10000)),
                                                  urgent=False, org_cnt=200,
                                                  pic_path="",
                                                  status=wc_const
                                                  .STATUS_QUALITY_INSPECTING,
                                                  department=d1,
                                                  team=team1,
                                                  processed_cnt=200,
                                                  processed_weight=200))
            work_command8 = do_commit(WorkCommand(sub_order=sub_order3,
                                                  org_weight=400,
                                                  procedure=normal_procedure,
                                                  tech_req=str(
                                                      randint(1, 10000)),
                                                  urgent=False, org_cnt=400,
                                                  pic_path="",
                                                  status=wc_const
                                                  .STATUS_QUALITY_INSPECTING,
                                                  department=d1,
                                                  team=team1,
                                                  processed_cnt=400,
                                                  processed_weight=400))
            sub_order3.remaining_quantity = 400
            do_commit(sub_order3)

            work_command9 = do_commit(WorkCommand(sub_order=sub_order4,
                                                  org_weight=1000,
                                                  procedure=normal_procedure,
                                                  tech_req=str(
                                                      randint(1, 10000)),
                                                  urgent=False, org_cnt=1000,
                                                  pic_path="",
                                                  status=wc_const
                                                  .STATUS_FINISHED,
                                                  department=d1,
                                                  team=team1,
                                                  processed_weight=1000,
                                                  processed_cnt=1000))

            work_command10 = do_commit(WorkCommand(sub_order=sub_order4,
                                                   org_weight=1500,
                                                   procedure=normal_procedure,
                                                   tech_req=str(
                                                       randint(1, 10000)),
                                                   urgent=False, org_cnt=1500,
                                                   pic_path="",
                                                   status=wc_const
                                                   .STATUS_FINISHED,
                                                   department=d1,
                                                   team=team1,
                                                   processed_weight=1500,
                                                   processed_cnt=1500))
            work_command11 = do_commit(WorkCommand(sub_order=sub_order4,
                                                   org_weight=500,
                                                   procedure=normal_procedure,
                                                   tech_req=str(
                                                       randint(1, 10000)),
                                                   urgent=False, org_cnt=500,
                                                   pic_path="",
                                                   status=wc_const
                                                   .STATUS_REFUSED,
                                                   processed_weight=500,
                                                   processed_cnt=500))
            work_command12 = do_commit(WorkCommand(sub_order=sub_order4,
                                                   org_weight=1000,
                                                   procedure=normal_procedure,
                                                   tech_req=str(
                                                       randint(1, 10000)),
                                                   urgent=False, org_cnt=1000,
                                                   pic_path="",
                                                   status=wc_const
                                                   .STATUS_FINISHED,
                                                   department=d1,
                                                   team=team1,
                                                   processed_weight=1000,
                                                   processed_cnt=1000))
            sub_order4.remaining_quantity = 0
            do_commit(sub_order4)
            work_command13 = do_commit(WorkCommand(sub_order=sub_order7,
                                                   org_weight=800,
                                                   procedure=normal_procedure,
                                                   tech_req=str(
                                                       randint(1, 10000)),
                                                   urgent=False, org_cnt=800,
                                                   pic_path="",
                                                   status=wc_const
                                                   .STATUS_FINISHED,
                                                   department=d1,
                                                   team=team1,
                                                   processed_weight=850,
                                                   processed_cnt=850))
            sub_order7.remaining_quantity = 0
            do_commit(sub_order7)

            qir1 = do_commit(QIReport(work_command10, 1000, 1000,
                                      quality_inspection.FINISHED, qi.id))
            qir2 = do_commit(
                QIReport(work_command10, 300, 300, quality_inspection.REPAIR,
                         qi.id))
            qir3 = do_commit(
                QIReport(work_command10, 200, 200, quality_inspection.REPLATE,
                         qi.id))
            qir4 = do_commit(QIReport(work_command9, 1000, 1000,
                                      quality_inspection.FINISHED, qi.id))

            qir5 = do_commit(
                QIReport(work_command12, 600, 600, quality_inspection.FINISHED,
                         qi.id))
            qir6 = do_commit(
                QIReport(work_command12, 200, 200, quality_inspection.REPAIR,
                         qi.id))
            qir7 = do_commit(
                QIReport(work_command12, 200, 200, quality_inspection.REPLATE,
                         qi.id))
            do_commit(Deduction(400, qi, team1, work_command12))

            qir8 = do_commit(
                QIReport(work_command13, 850, 850, quality_inspection.FINISHED,
                         qi.id))

            do_commit(
                WorkCommand(sub_order=work_command12.sub_order,
                            org_weight=qir6.weight,
                            status=wc_const.STATUS_DISPATCHING,
                            tech_req=work_command12.tech_req,
                            org_cnt=qir6.quantity,
                            procedure=work_command12.procedure,
                            previous_procedure=work_command12
                            .previous_procedure,
                            pic_path=qir6.pic_path,
                            handle_type=wc_const.HT_REPAIRE))

            do_commit(
                WorkCommand(sub_order=work_command12.sub_order,
                            org_weight=qir7.weight,
                            status=wc_const.STATUS_DISPATCHING,
                            tech_req=work_command12.tech_req,
                            org_cnt=qir7.quantity,
                            procedure=work_command12.procedure,
                            previous_procedure=work_command12
                            .previous_procedure,
                            pic_path=qir7.pic_path,
                            handle_type=wc_const.HT_REPLATE))
            do_commit(
                WorkCommand(sub_order=work_command10.sub_order,
                            org_weight=qir2.weight,
                            status=wc_const.STATUS_DISPATCHING,
                            tech_req=work_command10.tech_req,
                            org_cnt=qir2.quantity,
                            procedure=work_command10.procedure,
                            previous_procedure=work_command10.previous_procedure,
                            pic_path=qir2.pic_path,
                            handle_type=wc_const.HT_REPLATE))
            do_commit(
                WorkCommand(sub_order=work_command10.sub_order,
                            org_weight=qir3.weight,
                            status=wc_const.STATUS_DISPATCHING,
                            tech_req=work_command10.tech_req,
                            org_cnt=qir3.quantity,
                            procedure=work_command10.procedure,
                            previous_procedure=work_command10.previous_procedure,
                            pic_path=qir3.pic_path,
                            handle_type=wc_const.HT_REPLATE))

            store_bill1 = StoreBill(qir1)
            store_bill2 = StoreBill(qir4)
            store_bill4 = StoreBill(qir8)
            store_bill5 = StoreBill(qir8)
            store_bill3 = do_commit(StoreBill(qir5))
            store_bill1.printed = True
            store_bill1.harbor = hr1
            store_bill2.printed = True
            store_bill2.harbor = hr2
            store_bill4.printed = True
            store_bill4.harbor = hr1

            do_commit([store_bill1, store_bill2, store_bill4, store_bill5])

            team_list = Team.query.all()
            wc_list = [work_command11, work_command8, work_command7]
            for i in range(1, 51):
                do_commit(Deduction(randint(1, 100), qi,
                                    team_list[i % len(team_list)],
                                    wc_list[i % len(wc_list)],
                                    remark=u"第{:d}条deduction".format(i)))

            delivery_session = do_commit(DeliverySession(plate1.plate, 2300))
            delivery_task = do_commit(DeliveryTask(delivery_session, 1))
            store_bill4.harbor = store_bill5.harbor = hr1
            store_bill5.delivery_task = delivery_task
            store_bill5.delivery_session = delivery_session
            store_bill5.quantity = store_bill5.weight = 100
            store_bill4.quantity = store_bill4.weight = 750
            delivery_task.weight = store_bill5.weight
            delivery_task.finish_time = datetime.now()
            do_commit(Consignment(order3.goods_receipt.customer, delivery_session, True))
            do_commit(store_bill4)

        print "=====finish======"


if __name__ == "__main__":
    from distutils.dist import Distribution

    InitializeTestDB(Distribution()).run()
