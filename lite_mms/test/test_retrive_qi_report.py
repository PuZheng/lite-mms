# -*- coding: UTF-8 -*-
__author__ = 'wangjiali'
from pyfeature import Feature, Scenario, given, and_, when, then
from lite_mms.basemain import app
from lite_mms.database import db

def test():
    from pyfeature import flask_sqlalchemy_setup
    flask_sqlalchemy_setup(app, db)
    with Feature(u"质检员取消质检结果测试", ['lite_mms.test.steps.retrive_qi_report']):

        with Scenario(u"取消生成的工单已经分配的质检结果"):
            values = prepare_data()
            values['work_command'] = and_(u"提交质检单，扣重为1500", actor=values['qi'], work_command=values['work_command'])

            when(u"质检报告生成的新工单任意一个已经分配",values['work_command'].qir_list, values['team'])
            then(u"取消质检结果失败", actor=values['qi'], work_command=values['work_command'])
            and_(u"工单扣重量还是1500", work_command=values['work_command'])

    with Feature(u"质检员取消生成的工单已排产未分配的质检结果测试", ['lite_mms.test.steps.retrive_qi_report']):

        with Scenario(u"取消生成的工单已排产未分配的质检结果"):
            values = prepare_data("next")
            values['work_command'] = and_(u"提交质检单，扣重为1500", actor=values['qi'], work_command=values['work_command'])

            wc_id_list = when(u"质检报告生成的新工单都未分配", values['work_command'].qir_list)
            then(u"取消质检结果成功", actor=values['qi'], work_command=values['work_command'])
            and_(u"质检报告生成的工单被删除",values['work_command'].qir_list, wc_id_list)
            and_(u"工单状态变回待质检,扣重为0", work_command=values['work_command'])
            and_(u"质检报告还关联着工单",qi_report_list=[values['qi_report_next'], values['qi_report_repair'], values['qi_report_rework']], work_command=values['work_command'])

    with Feature(u"质检员取消生成的仓单已经发货的质检结果测试", ['lite_mms.test.steps.retrive_qi_report']):

        with Scenario(u"取消生成的仓单已经发货的质检结果"):
            values = prepare_data()

            values['work_command'] = and_(u"提交质检单，扣重为500", actor=values['qi'], work_command=values['work_command'])
            store_bill, new_wc = then(u"生成一个新的仓单和一个新的工单", qi_report_over=values['qi_report_over'], qi_report_repair=values['qi_report_repair'])

            when(u"仓单已经发货", store_bill=store_bill, work_command=new_wc, delivery_session=values['delivery_session'])
            then(u"取消质检结果失败", actor=values['qi'], work_command=values['work_command'])

    with Feature(u"质检员取消生成的仓单未发货的质检结果测试", ['lite_mms.test.steps.retrive_qi_report']):

        with Scenario(u"取消生成的仓单未发货的质检结果"):
            values = prepare_data()

            values['work_command'] = and_(u"提交质检单，扣重为500", actor=values['qi'], work_command=values['work_command'])
            store_bill, new_wc = then(u"生成一个新的仓单和一个新的工单", qi_report_over=values['qi_report_over'], qi_report_repair=values['qi_report_repair'])

            when(u"仓单未发货，且工单未排产", store_bill=store_bill, work_command=new_wc)
            then(u"取消质检结果成功", actor=values['qi'], work_command=values['work_command'])
            and_(u"质检报告生成的工单被删除", qi_report_list=[values['qi_report_repair']],
                 wc_id_list=[qir.generated_work_command_id for qir in
                             values['work_command'].qir_list])
            and_(u"仓单被删除", store_bill=store_bill)
            and_(u"工单状态变回待质检,扣重为0", work_command=values['work_command'])
            and_(u"质检报告还关联着工单", qi_report_list=[values['qi_report_repair'], values['qi_report_over']], work_command=values['work_command'])

    with Feature(u"质检员取消前一天的质检结果测试", ['lite_mms.test.steps.retrive_qi_report']):

        with Scenario(u"取消前一天的质检报告"):
            values = prepare_data()
            values['work_command'] = and_(u"提交质检单，扣重为500", actor=values['qi'], work_command=values['work_command'])

            values['work_command'] = when(u"质检结果是前一天提交", work_command=values['work_command'])
            then(u"取消质检结果失败", actor=values['qi'], work_command=values['work_command'])

    from pyfeature import clear_hooks
    clear_hooks()

def prepare_data(name=None):
    values = {}
    qi_group = given(u"创建小组-质检员")
    cc_group = and_(u"创建小组-收发员")
    tl_group = and_(u"创建小组-班组长")
    s_group = and_(u"创建小组-调度员")
    values['qi'] = and_(u"创建一个用户-质检员", group=qi_group)
    cc = and_(u"创建一个用户-收发员", group=cc_group)
    tl = and_(u"创建一个用户-班组长", group=tl_group)
    s = and_(u"创建一个用户-调度员", group=s_group)

    values['department'] = and_(u"创建一个车间")
    values['team'] = team = and_(u"创建一个班组", values['department'], tl)

    customer = and_(u"创建一个客户")
    plate = and_(u"创建一个车牌号aA12345")
    unload_session = and_(u"创建一个卸货会话", plate)
    goods_receipt = and_(u"创建一个收获单", customer, unload_session)
    order = and_(u"创建一个订单1", cc, goods_receipt)
    product_type = and_(u"创建一个产品类型")
    product = and_(u"创建一个产品", product_type)
    harbor = and_(u"创建一个卸货点", values['department'])
    suborder = and_(u"生成一个订单1的子订单，重量为10000", order=order, product=product, harbor=harbor)
    procedure = and_(u"创建一个工序镀锌", values['department'])
    values['work_command'] = and_(u"生成一个待质检状态的工单，重量为3000", suborder=suborder, department=values["department"], team=team, procedure=procedure)
    if name == "next":
        values['qi_report_next'] = and_(u"生成一个合格转下道工序的质检报告，重量为1500", work_command=values['work_command'], actor=values['qi'])
        values['qi_report_repair'] = and_(u"生成一个返修的质检报告，重量为500", work_command=values['work_command'], actor=values['qi'])
        values['qi_report_rework'] = and_(u"生成一个返镀的质检报告，重量为1000", work_command=values['work_command'], actor=values['qi'])
    else:
        values['qi_report_over'] = and_(u"生成一个合格结束的质检报告，重量为1500", work_command=values['work_command'], actor=values['qi'])
        values['qi_report_repair'] = and_(u"生成一个返修的质检报告，重量为500", work_command=values['work_command'], actor=values['qi'])
    deliver_plate = and_(u"创建一个车牌号aA11111")
    values['delivery_session'] = and_(u"创建一个发货会话", deliver_plate)
    return values
