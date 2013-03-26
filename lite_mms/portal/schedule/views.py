# -*- coding: UTF-8 -*-
"""
@author: Yangminghua
@version: $
"""
from wtforms import Form, IntegerField, validators, HiddenField, TextField,\
    BooleanField
from flask import request, redirect, url_for, abort, flash
from lite_mms.portal.schedule import schedule_page
from lite_mms.utilities import decorators, _
from lite_mms import constants
from lite_mms.utilities.pagination import Pagination

@schedule_page.route('/')
def index():
    return redirect(url_for("schedule.order_list"))


@schedule_page.route('/order-list')
@decorators.templated('/schedule/order-list.html')
@decorators.nav_bar_set
def order_list():
    page = request.args.get('page', 1, type=int)
    from lite_mms.apis import order, customer

    customer_id = request.args.get("customer_id", type=int)
    params = dict(unfinished=True, desc=True)
    c = None
    if customer_id:
        params.update(customer_id=customer_id)
        c = customer.get_customer(customer_id)
        if not c:
            return _(u"ID为%s的客户不存在" % customer_id), 404

    orders, total_cnt = order.get_order_list(
        (page - 1) * constants.ORDER_PER_PAGE, constants.ORDER_PER_PAGE,
        **params)
    customer_list = order.get_customer_list("unlimited", dispatched=True)
    pagination = Pagination(page, constants.ORDER_PER_PAGE, total_cnt)
    param_dic = {'titlename': u'订单列表', 'order_list': orders,
                 'pagination': pagination, 'customer_list': customer_list}
    if c:
        param_dic.update(customer=c)
    return param_dic


@schedule_page.route('/work-command', methods=['POST'])
def work_command():
    """
    生成一个新的工单
    """
    from lite_mms.apis import manufacture

    class PreScheduleForm(Form):
        id = HiddenField('id', [validators.required()])
        order_id = HiddenField('order_id', [validators.required()])
        schedule_weight = IntegerField('schedule_weight',
                                       [validators.required()])
        procedure = IntegerField('procedure')
        tech_req = TextField('tech_req')
        schedule_count = IntegerField('schedule_count')
        urgent = BooleanField('urgent')

    form = PreScheduleForm(request.form)
    if form.validate():
        try:
            inst = manufacture.new_work_command(
                sub_order_id=form.id.data,
                org_weight=form.schedule_weight.data,
                procedure_id=form.procedure.data,
                org_cnt=form.schedule_count.data,
                urgent=form.urgent.data,
                tech_req=form.tech_req.data)
            if inst:
                if inst.sub_order.returned:
                    flash(u"成功创建工单（编号%d），请提醒质检员赶快处理" % inst.id)
                else:
                    flash(u"成功创建工单（编号%d）" % inst.id)
        except ValueError as a:
            flash(a.message)
            return redirect(url_for('schedule.order',
                                    id_=form.order_id.data)), 403
        return redirect(url_for('schedule.order',
                                id_=form.order_id.data))
    else:
        abort(404)


@schedule_page.route('/order/<int:id_>', methods=['GET'])
@decorators.templated('/schedule/order.html')
@decorators.nav_bar_set
def order(id_):
    from lite_mms.apis import order as apis_order

    inst = apis_order.get_order(id_)
    if not inst:
        abort(404)
    return {'titlename': u'订单详情', 'order': inst}


@schedule_page.route('/work_command_list', methods=['GET'])
@decorators.templated('/schedule/work-command-list.html')
@decorators.nav_bar_set
def work_command_list():
    from lite_mms.apis import order as apis_order, manufacture

    status = request.args.get('status')

    order = apis_order.get_order(request.args.get('id', type=int))
    if not order:
        abort(404)

    work_list = []
    if status == 'todo':
        for sub_order in order.sub_order_list:
            work_list.extend(sub_order.pre_work_command_list)
    elif status == 'doing':
        for sub_order in order.sub_order_list:
            work_list.extend(sub_order.manufacturing_work_command_list)
    elif status == 'done':
        for sub_order in order.sub_order_list:
            work_list.extend(sub_order.done_work_command_list)
    return {'work_list': work_list}
