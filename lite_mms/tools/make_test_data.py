# -*- coding: UTF-8 -*-
"""
本脚本用于创建测试数据，是为了帮助进行随意测试。本脚本基于数据库的初始化脚本
"""

from hashlib import md5
from random import randint
from datetime import datetime
from flask import url_for
from lite_mms.basemain import app
from lite_mms.permissions import permissions
from lite_mms.constants import groups, work_command as wc_const, \
    quality_inspection, DEFAULT_PRODUCT_NAME, DEFAULT_PRODUCT_TYPE_NAME
from lite_mms.constants import cargo as cargo_const
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
        from lite_mms.tools import build_db
        db.drop_all()
        init_db()
        build_db.build_db()

        # 创建产品类型以及产品
        product_type1 = do_commit(ProductType(name=u"A"))
        product_type2 = do_commit(ProductType(name=u"B"))
        product_type3 = do_commit(ProductType(name=u"C"))
        product1 = do_commit(Product(name=u'A01', product_type=product_type1))
        product2 = do_commit(Product(name=u'A02', product_type=product_type1))
        product3 = do_commit(Product(name=u'A03', product_type=product_type1))
        product4 = do_commit(Product(name=u'B01', product_type=product_type2))
        product5 = do_commit(Product(name=u'B02', product_type=product_type2))
        product4 = do_commit(Product(name=u'C01', product_type=product_type3))
        
        # 创建用户
        cargo_clerk = Group.query.get(groups.CARGO_CLERK)
        scheduler = Group.query.get(groups.SCHEDULER)
        department_leader = Group.query.get(groups.DEPARTMENT_LEADER)
        team_leader = Group.query.get(groups.TEAM_LEADER)
        quality_inspector = Group.query.get(groups.QUALITY_INSPECTOR)
        loader = Group.query.get(groups.LOADER)
        accountant = Group.query.get(groups.ACCOUNTANT)
        # 收发员
        cc = do_commit(User(username='cc', password=md5('cc').hexdigest(), groups=[cargo_clerk]))
        # 调度员
        s = do_commit(User(username='s', password=md5('s').hexdigest(), groups=[scheduler]))
        # 车间1主任
        d1_dl = do_commit(
            User(username='d1', password=md5('d1').hexdigest(), groups=[department_leader]))
        # 车间2主任
        d2_dl = do_commit(
            User(username='d2', password=md5('d2').hexdigest(), groups=[department_leader]))
        # 超级车间主任
        super_dl = do_commit(
            User(username='super_dl', password=md5('super_dl').hexdigest(), groups=[department_leader]))
        # 班组101班组长
        t101_tl = do_commit(
            User(username='t101', password=md5('t101').hexdigest(), groups=[team_leader]))
        # 班组201班组长
        t201_tl = do_commit(
            User(username='t201', password=md5('t201').hexdigest(), groups=[team_leader]))
        # 质检员
        qi = do_commit(
            User(username='qi', password=md5('qi').hexdigest(), groups=[quality_inspector]))
        # 装卸工
        l = do_commit(User(username='l', password=md5('l').hexdigest(), groups=[loader]))
        # 财会人员
        a = do_commit(User(username='a', password=md5('a').hexdigest(), groups=[accountant]))

        # 创建车间和班组
        department1 = do_commit(Department(name=u"车间1", leader_list=[d1_dl, super_dl])) 
        department2 = do_commit(Department(name=u"车间2", leader_list=[d2_dl, super_dl])) 
        team1 = do_commit(Team(name=u"班组101", department=department1, leader=t101_tl))
        team2 = do_commit(Team(name=u"班组201", department=department2, leader=t201_tl))

        # 创建工序
        procedure1 = do_commit(Procedure(name=u"工序1", department_list=[department1, department2]))
        procedure2 = do_commit(Procedure(name=u"工序2", department_list=[department2]))

        # 初始化装卸点
        harbor1 = do_commit(Harbor(name=u"装卸点1", department=department1))
        harbor2 = do_commit(Harbor(name=u"装卸点2", department=department2))
        
        # 初始化车辆
        vehicle1 = do_commit(Plate(name=u"浙A 00001"))
        vehicle2 = do_commit(Plate(name=u"浙A 00002"))

        # 初始化客户
        customer1 = do_commit(Customer(u"宁波机床场", "nbjcc"))
        customer2 = do_commit(Customer(u"宁力紧固件", "nljgj"))
        customer3 = do_commit(Customer(u"宁波造船场", "nbzcc"))
        customer4 = do_commit(Customer(u"宁波飞机场", "nbfjc"))

        # 收货环节
        #     - 车上有人, 有两个任务, 分别来自不同的客户, 并且都已经称重
        unload_session1 = do_commit(UnloadSession(plate_=vehicle1, gross_weight=10000, with_person=True,
                                                  finish_time=datetime.now(), status=cargo_const.STATUS_CLOSED))
        default_product = Product.query.get(DEFAULT_PRODUCT_NAME)
        unload_task1 = do_commit(UnloadTask(unload_session1, harbor1, customer1, l, default_product, "0.png",
                       weight=1000))
        unload_task2 = do_commit(UnloadTask(unload_session1, harbor2, customer2, l, product2, "1.png", weight=3000))
        #     - 车上无人， 有三个任务，来自两个客户, 有一个尚未称重
        unload_session2 = do_commit(
            UnloadSession(plate_=vehicle2, gross_weight=10000, with_person=False,
                          finish_time=datetime.now(), status=cargo_const.STATUS_WEIGHING))
        unload_task3 = do_commit(
            UnloadTask(unload_session2, harbor1, customer2, l, product2, "2.png",
                       weight=1000))
        unload_task4 = do_commit(
            UnloadTask(unload_session2, harbor2, customer3, l, product3, "3.png",
                       weight=4000))
        unload_task5 = do_commit(
            UnloadTask(unload_session2, harbor2, customer3, l, product4, "4.png"))
        #     - 车上无人，正在等待装货
        unload_session3 = do_commit(
            UnloadSession(plate_=vehicle2, gross_weight=10000, with_person=False,
                          status=cargo_const.STATUS_LOADING))

        # 生成收货会话, 注意这里故意不为某些客户生成收货单
        goods_receipt1 = do_commit(
            GoodsReceipt(customer1, unload_session1))
        goods_receipt2 = do_commit(
            GoodsReceipt(customer2, unload_session1))
        # 生成订单, 注意这里故意不为某些收货会话生成订单
        #     - 生成一个已经下发的订单
        order1 = do_commit(
            Order(goods_receipt1, creator=cc, dispatched=True, refined=True))
        #     - 生成一个尚未下发的订单
        order2 = do_commit(
            Order(goods_receipt2, creator=cc))
        # 生成子订单，注意这里故意不为某些订单生成子订单
        #     - 生成计重类型的子订单, 还有50公斤没有分配出去
        sub_order1 = do_commit(
            SubOrder(product1, 300, harbor1, order1, 300, "KG",
                     due_time=datetime.today(), unload_task=unload_task1, returned=True))
        sub_order2 = do_commit(
            SubOrder(product2, 1000, harbor2, order1, 1000, "KG",
                     due_time=datetime.today(), unload_task=unload_task1, returned=True))

        # 生成工单
        #     - DISPATCHING STATUS
        work_command1 = do_commit(WorkCommand(sub_order=sub_order1,
                                              org_weight=50,
                                              procedure=procedure1,
                                              tech_req=u"工单1的技术要求",
                                              urgent=False, org_cnt=50,
                                              pic_path="1.png"))
        #     - ASSIGNING STATUS 
        work_command2 = do_commit(WorkCommand(sub_order=sub_order1,
                                              org_weight=50,
                                              procedure=procedure1,
                                              tech_req=u"工单2的技术要求",
                                              urgent=False, org_cnt=50,
                                              department=department1,
                                              status=wc_const.STATUS_ASSIGNING,
                                              pic_path="1.png"))
        #     - ENDING STATUS
        work_command3 = do_commit(WorkCommand(sub_order=sub_order1,
                                              org_weight=50,
                                              procedure=procedure2,
                                              tech_req=u"工单3的技术要求",
                                              urgent=False, org_cnt=100,
                                              pic_path="1.png",
                                              status=wc_const.STATUS_ENDING,
                                              department=department1, 
                                              team=team1))
        #     - QUALITY INSPECTING STATUS
        work_command4 = do_commit(WorkCommand(sub_order=sub_order1,
                                              org_weight=50,
                                              procedure=procedure2,
                                              tech_req=u"工单4的技术要求",
                                              urgent=False, org_cnt=50,
                                              pic_path="1.png",
                                              status=wc_const.STATUS_QUALITY_INSPECTING,
                                              department=department1))
        #     - FINISHED STATUS
        work_command4 = do_commit(WorkCommand(sub_order=sub_order1,
                                              org_weight=50,
                                              procedure=procedure2,
                                              tech_req=u"工单5的技术要求",
                                              urgent=False, org_cnt=50,
                                              pic_path="1.png",
                                              status=wc_const.STATUS_FINISHED,
                                              department=department1))
        return


        # qir1 = do_commit(QIReport(work_command10, 1000, 1000,
        #                           quality_inspection.FINISHED, qi.id))
        # qir2 = do_commit(
        #     QIReport(work_command10, 300, 300, quality_inspection.REPAIR,
        #              qi.id))
        # qir3 = do_commit(
        #     QIReport(work_command10, 200, 200, quality_inspection.REPLATE,
        #              qi.id))
        # qir4 = do_commit(QIReport(work_command9, 1000, 1000,
        #                           quality_inspection.FINISHED, qi.id))
        #
        # qir5 = do_commit(
        #     QIReport(work_command12, 600, 600, quality_inspection.FINISHED,
        #              qi.id))
        # qir6 = do_commit(
        #     QIReport(work_command12, 200, 200, quality_inspection.REPAIR,
        #              qi.id))
        # qir7 = do_commit(
        #     QIReport(work_command12, 200, 200, quality_inspection.REPLATE,
        #              qi.id))
        # do_commit(Deduction(400, qi, team1, work_command12))
        #
        # qir8 = do_commit(
        #     QIReport(work_command13, 850, 850, quality_inspection.FINISHED,
        #              qi.id))
        #
        # do_commit(
        #     WorkCommand(sub_order=work_command12.sub_order,
        #                 org_weight=qir6.weight,
        #                 status=wc_const.STATUS_DISPATCHING,
        #                 tech_req=work_command12.tech_req,
        #                 org_cnt=qir6.quantity,
        #                 procedure=work_command12.procedure,
        #                 previous_procedure=work_command12
        #                 .previous_procedure,
        #                 pic_path=qir6.pic_path,
        #                 handle_type=wc_const.HT_REPAIRE))
        #
        # do_commit(
        #     WorkCommand(sub_order=work_command12.sub_order,
        #                 org_weight=qir7.weight,
        #                 status=wc_const.STATUS_DISPATCHING,
        #                 tech_req=work_command12.tech_req,
        #                 org_cnt=qir7.quantity,
        #                 procedure=work_command12.procedure,
        #                 previous_procedure=work_command12
        #                 .previous_procedure,
        #                 pic_path=qir7.pic_path,
        #                 handle_type=wc_const.HT_REPLATE))
        # do_commit(
        #     WorkCommand(sub_order=work_command10.sub_order,
        #                 org_weight=qir2.weight,
        #                 status=wc_const.STATUS_DISPATCHING,
        #                 tech_req=work_command10.tech_req,
        #                 org_cnt=qir2.quantity,
        #                 procedure=work_command10.procedure,
        #                 previous_procedure=work_command10.previous_procedure,
        #                 pic_path=qir2.pic_path,
        #                 handle_type=wc_const.HT_REPLATE))
        # do_commit(
        #     WorkCommand(sub_order=work_command10.sub_order,
        #                 org_weight=qir3.weight,
        #                 status=wc_const.STATUS_DISPATCHING,
        #                 tech_req=work_command10.tech_req,
        #                 org_cnt=qir3.quantity,
        #                 procedure=work_command10.procedure,
        #                 previous_procedure=work_command10.previous_procedure,
        #                 pic_path=qir3.pic_path,
        #                 handle_type=wc_const.HT_REPLATE))
        #
        # store_bill1 = StoreBill(qir1)
        # store_bill2 = StoreBill(qir4)
        # store_bill4 = StoreBill(qir8)
        # store_bill5 = StoreBill(qir8)
        # store_bill3 = do_commit(StoreBill(qir5))
        # store_bill1.printed = True
        # store_bill1.harbor = hr1
        # store_bill2.printed = True
        # store_bill2.harbor = hr2
        # store_bill4.printed = True
        # store_bill4.harbor = hr1
        #
        # do_commit([store_bill1, store_bill2, store_bill4, store_bill5])
        #
        # team_list = Team.query.all()
        # wc_list = [work_command11, work_command8, work_command7]
        # for i in range(1, 51):
        #     do_commit(Deduction(randint(1, 100), qi,
        #                         team_list[i % len(team_list)],
        #                         wc_list[i % len(wc_list)],
        #                         remark=u"第{:d}条deduction".format(i)))
        #
        # delivery_session = do_commit(DeliverySession(plate1.plate, 2300))
        # delivery_task = do_commit(DeliveryTask(delivery_session, 1))
        # store_bill4.harbor = store_bill5.harbor = hr1
        # store_bill5.delivery_task = delivery_task
        # store_bill5.delivery_session = delivery_session
        # store_bill5.quantity = store_bill5.weight = 100
        # store_bill4.quantity = store_bill4.weight = 750
        # delivery_task.weight = store_bill5.weight
        # delivery_task.finish_time = datetime.now()
        # do_commit(Consignment(order3.goods_receipt.customer, delivery_session, True))
        # do_commit(store_bill4)

        print "=====finish======"




if __name__ == "__main__":
    #import karnickel
    # karnickel.install_hook()
    from distutils.dist import Distribution

    InitializeTestDB(Distribution()).run()
