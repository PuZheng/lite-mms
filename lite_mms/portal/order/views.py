# -*- coding: utf-8 -*-
"""
@author: Yangminghua
"""
from datetime import datetime, date
import json
from flask import request, url_for, render_template, abort, flash
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.utils import redirect
from wtforms import Form, TextField, IntegerField, validators, BooleanField,\
    DateField, HiddenField
from lite_mms import constants
from lite_mms.exceptions import PropertyError
from lite_mms.portal.order import order_page
from lite_mms.utilities import decorators, _
from lite_mms.utilities.pagination import Pagination

@order_page.route('/')
@order_page.route("/order-list", methods=["POST", "GET"])
@decorators.templated("/order/order-list.html")
@decorators.nav_bar_set
def order_list():
    from lite_mms import apis

    if request.method == "GET":
        page = request.args.get("page", 1, type=int)
        category = request.args.get("category", default="undispatched")
        time_span = request.args.get("time_span", "unlimited").lower()
        customer_id = request.args.get("customer_id", 0, type=int)

        def check_category(category):
            return category in ["all",
                                "accountable",
                                "undispatched",
                                "deliverable"]

        if not check_category(category):
            return _(u"参数category错误"), 403

        accountable_only = False
        undispatched_only = False
        deliverable_only = False
        desc = False
        if category == "accountable":
            accountable_only = True
        elif category == "undispatched":
            undispatched_only = True
        elif category == "deliverable":
            deliverable_only = True
        else:
            desc = True
        orders, total_cnt = apis.order.OrderWrapper.get_list(
            (page - 1) * constants.ORDER_PER_PAGE,
            constants.ORDER_PER_PAGE,
            after=apis.order.get_should_after_date(time_span),
            customer_id=customer_id,
            accountable_only=accountable_only,
            undispatched_only=undispatched_only,
            deliverable_only=deliverable_only,
            desc=desc)

        # 获取在时间段内，有订单的客户
        customer_list = apis.order.get_customer_list(time_span)

        pagination = Pagination(page, constants.ORDER_PER_PAGE, total_cnt)
        return {'titlename': u'订单列表',
                'order_list': orders,
                'pagination': pagination,
                "customer_list": customer_list, "category": category,
                'time_span': time_span}
    else: # POST
        order_id_list = request.form.getlist('order_id')
        act = request.form.get("act")
        category = request.args.get("category", default="undispatched")
        customer = request.args.get("customer", "").lower()
        time_span = request.args.get("time_span", "day").lower()
        if act not in ["dispatch", "account"]:
            return _(u"act参数错误"), 403

        if act == "dispatch":
            dispatched_orders = []
            for order_id in order_id_list:
                try:
                    order = apis.order.get_order(order_id)
                    order.update(dispatched=True)
                    dispatched_orders.append(order)
                except (PropertyError, NoResultFound) as e:
                    return e.description, 403
            message = _(u"订单%(order_list)s已经被下发" % {"order_list": ",".join(
                order.customer_order_number for order in dispatched_orders)})
        else:
            accounted_orders = []
            for order_id in order_id_list:
                try:
                    order = apis.order.get_order(order_id)
                    for sub_order in order.sub_order_list:
                        for store_bill in sub_order.store_bill_list:
                            fake_delivery_task = apis.delivery.fake_delivery_task()
                            if not store_bill.delivery_task:
                                apis.delivery.update_store_bill(store_bill.id,
                                                                delivery_session_id=fake_delivery_task.delivery_session.id,
                                                                delivery_task_id=fake_delivery_task.id)
                        sub_order.end()
                    order.update(
                        finish_time=datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"))
                    accounted_orders.append(order)
                except (PropertyError, NoResultFound) as e:
                    return e.description, 403
            message = _(u"订单%s已经被盘点" % ",".join(
                order.customer_order_number for order in accounted_orders))

        flash(message)
        return redirect(url_for('order.order_list', customer=customer,
                                category=category, time_span=time_span,
                                message=message))


@order_page.route("/order/<int:id_>", methods=("GET", "POST"))
@decorators.templated("/order/order.html")
@decorators.nav_bar_set
def order(id_):
    from lite_mms import apis

    inst = apis.order.get_order(id_)
    if not inst:
        abort(404)
    if request.method == "GET":
        url = request.args.get("url")
        return {'titlename': u'订单详情', 'order': inst, 'url': url}
    else:
        method = request.form.get("method", "save")
        if "save" == method:
            inst.update(customer_order_number=request.form["customer_order_number"])
        else:
            inst.update(refined=True)
        url = request.form.get("url")
        return redirect(url_for("order.order", id_=id_, _method="GET", url=url))

@order_page.route("/sub-order/<int:id_>", methods=["GET","POST"])
@decorators.templated("order/sub-order.html")
@decorators.nav_bar_set
def sub_order(id_):
    from lite_mms import apis

    inst = apis.order.SubOrderWrapper.get_sub_order(id_)
    if not inst:
        abort(404)
    if request.method == "GET":

        from lite_mms.constants import DEFAULT_PRODUCT_NAME

        param_dict = {'titlename': u'子订单详情', 'sub_order': inst,
                      'DEFAULT_PRODUCT_NAME': DEFAULT_PRODUCT_NAME}
        param_dict.update(product_types=apis.product.get_product_types())
        param_dict.update(products=json.dumps(apis.product.get_products()))
        param_dict.update(harbor_list=apis.harbor.get_harbor_list())
        return param_dict
    else:
        #sub_order的get由ajax实现
        frm = SubOrderForm(request.form)
        if frm.validate():
            inst.update(product_id=frm.product.data, tech_req=frm.tech_req.data,
                        spec=frm.spec.data, type=frm.type.data,
                        due_time=str(frm.due_time.data), urgent=frm.urgent.data,
                        weight=frm.weight.data, harbor_name=frm.harbor.data,
                        returned=frm.returned.data, unit=frm.unit.data,
                        quantity=frm.weight.data if inst.order_type == constants
                        .STANDARD_ORDER_TYPE else frm.quantity.data)
            flash(u"修改成功！")
            return redirect(
                frm.url.data or url_for('order.order', id_=inst.order_id,
                                        url=frm.url.data))
        else:
            return str(frm.errors), 403


@order_page.route("/new-sub-order", methods=["GET", "POST"])
@decorators.templated("/order/new-extra-sub-order.html")
@decorators.nav_bar_set
def new_sub_order():
    """
    创建新的计件类型的子订单（只有计件类型的订单能够增加子订单）
    """
    from lite_mms import apis
    if request.method == "GET":
        from lite_mms import apis

        order = apis.order.get_order(request.args.get("order_id", type=int))
        if not order:
            abort(404)
        if order.dispatched:
            return render_template("result.html",
                                   error_content=u"已下发的订单不能新增子订单",
                                   back_url=url_for("order.order",
                                                    id=order.id))
        from lite_mms.constants import DEFAULT_PRODUCT_NAME

        return dict(titlename=u'新建子订单', order=order,
                    DEFAULT_PRODUCT_NAME=DEFAULT_PRODUCT_NAME,
                    product_types=apis.product.get_product_types(),
                    products=json.dumps(apis.product.get_products()),
                    harbor_list=apis.harbor.get_harbor_list(),
                    team_list=apis.manufacture.get_team_list())
    else:
        class NewSubOrderForm(Form):
            order_id = IntegerField('order_id', [validators.required()])
            product = IntegerField('product', [validators.required()])
            spec = TextField('spec', [validators.required()])
            type = TextField('type', [validators.required()])
            tech_req = TextField('tech_req')
            due_time = DateField('due_time',
                                 [validators.required()])
            urgent = BooleanField('urgent')
            returned = BooleanField('returned')
            unit = TextField('unit')
            quantity = IntegerField('quantity')
            weight = IntegerField('weight', [validators.required()])
            harbor = TextField('harbor', [validators.required()])

        form = NewSubOrderForm(request.form)
        order_id = form.order_id.data
        due_time = form.due_time.data
        if date.today() > due_time:
            return render_template("result.html",
                                   error_content=u"错误的交货日期",
                                   back_url=url_for("order.order",
                                                    id_=order_id))
        from lite_mms import apis
        try:
            sb = apis.order.SubOrderWrapper.new_sub_order(order_id=order_id,
                                                     product_id=form.product.data,
                                                     spec=form.spec.data,
                                                     type=form.type.data,
                                                     tech_req=form.tech_req.data,
                                                     due_time=str(due_time),
                                                     urgent=form.urgent.data,
                                                     weight=form.weight.data,
                                                     harbor_name=form.harbor.data,
                                                     returned=form.returned.data,
                                                     unit=form.unit.data,
                                                     quantity=form.quantity.data)
            flash(u"新建成功！")
        except ValueError, e:
            flash(unicode(e), "error")
        return redirect(url_for('order.order', id_=order_id))

class SubOrderForm(Form):
    product = IntegerField('product', [validators.required()])
    spec = TextField('spec')
    type = TextField('type')
    tech_req = TextField('tech_req')
    due_time = DateField('due_time', [validators.required()])
    urgent = BooleanField('urgent')
    returned = BooleanField('returned')
    unit = TextField('unit')
    quantity = IntegerField('quantity')
    weight = IntegerField('weight', [validators.required()])
    harbor = TextField('harbor', [validators.required()])
    url = HiddenField("purl")
