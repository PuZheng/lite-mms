# -*- coding: utf-8 -*-
"""
@author: Yangminghua
"""
from datetime import date
from flask import request, url_for, render_template, abort, flash, redirect, json
from wtforms import Form, TextField, IntegerField, validators, BooleanField, DateField
from lite_mms.portal.order import order_page
from lite_mms.utilities import decorators


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
        if order.dispatched or order.refined:
            return render_template("result.html",
                                   error_content=u"已下发或已标记完善的订单不能新增子订单",
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
            sb = apis.order.SubOrderWrapper.new_sub_order(order_id=order_id, product_id=form.product.data,
                                                          spec=form.spec.data, type=form.type.data,
                                                          tech_req=form.tech_req.data, due_time=str(due_time),
                                                          urgent=form.urgent.data, weight=form.weight.data,
                                                          harbor_name=form.harbor.data, returned=form.returned.data,
                                                          unit=form.unit.data, quantity=form.quantity.data)
            flash(u"新建成功！")
        except ValueError, e:
            flash(unicode(e), "error")
        return redirect(url_for('order.order', id_=order_id))
