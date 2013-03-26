# -*- coding: UTF-8 -*-

from datetime import datetime
from pyfeature import step
from lite_mms import models
from lite_mms.utilities.decorators import committed
from lite_mms import apis
from lite_mms import constants


@step(u"完善子订单(.*)")
@committed
def _(step, desc, so):
    so.due_time = datetime.now()
    so.refined = True
    return so

@step(u"下发订单")
@committed
def _(step, order):
    order.dispatched = True
    return order

@step(u"下发工单到车间(.*)")
def _(step, _department_name, wc, actor, department):
    return apis.WorkCommandWrapper(wc).go(actor.id, action=constants.work_command.ACT_DISPATCH,
        department_id=department.id) 

@step(u"指派工单到班组(.*)")
def _(step, _team_name, wc, team, actor):
    apis.WorkCommandWrapper(wc).go(actor.id, action=constants.work_command.ACT_ASSIGN,
        team_id=team.id) 

@step(u"将工单生产完毕")
def _(step, wc, actor):
    apis.WorkCommandWrapper(wc).go(actor.id, action=constants.work_command.ACT_ADD_WEIGHT, 
        weight=wc.org_weight)
    apis.WorkCommandWrapper(wc).go(actor.id, action=constants.work_command.ACT_END)

@step(u"没新工单完成")
def _(step, wc):
    wc_list,count = apis.WorkCommandWrapper.get_list(status_list=None)
    assert wc_list[-1].id == wc.id

@step(u"质检员将工单全部通过")
def _(step, wc, actor):
    apis.quality_inspection.new_QI_report(actor.id, wc.id, wc.processed_cnt, 1, "")
    apis.WorkCommandWrapper(wc).go(actor.id, action=constants.work_command.ACT_QI)

@step(u"生成一个新的质检报告")
def _(step, wc):
    from lite_mms.utilities import get_or_404
    from lite_mms.models import WorkCommand
    wc = get_or_404(WorkCommand, wc.id)
    assert len(wc.qir_list) == 1
    return wc.qir_list[0]

@step(u"生成一个新的仓单")
def _(step, qir):
    assert len(qir.store_bill_list) == 1
    return qir.store_bill_list[0]

@step(u"该仓单已经打印过")
def _(step, sb):
    assert sb.printed

@step(u"该仓单的装卸点是装卸点一")
def _(step, sb, harbor):
    assert sb.harbor.name == harbor.name

