# -*- coding: UTF-8 -*-
"""
@author: Yangminghua
@version: $
"""
from flask import request, redirect, url_for, flash
from wtforms import TextField, Form, validators, IntegerField
from lite_mms import constants
from lite_mms.portal.store import store_bill_page
from lite_mms.utilities import decorators, Pagination
from lite_mms.utilities import _
from datetime import date, timedelta


@store_bill_page.route('/')
def index():
    return redirect(url_for("store_bill.store_bill_list"))


@store_bill_page.route("/store-bill/<int:id_>", methods=["GET", "POST"])
@decorators.templated("/store/store-bill.html")
@decorators.nav_bar_set
def store_bill(id_):
    import lite_mms.apis as apis

    store_bill = apis.delivery.get_store_bill(id_)
    if store_bill:
        if request.method == "GET":
            return dict(titlename=u'仓单详情', store_bill=store_bill,
                        harbors=apis.harbor.get_harbor_list())
        else:
            class StoreBillForm(Form):
                harbor = TextField("harbor", [validators.required()])
                weight = IntegerField("weight", [validators.required()])
                quantity = IntegerField("quantity")

            form = StoreBillForm(request.form)
            if form.validate():
                kwargs = dict(printed=True, weight=form.weight.data,
                              harbor=form.harbor.data)
                if form.quantity.data:
                    kwargs["quantity"] = form.quantity.data
                try:
                    apis.delivery.update_store_bill(store_bill.id, **kwargs)
                    flash(u"修改仓单%d成功" % id_)
                    return redirect(url_for("store_bill.store_bill", id_=id_,
                                            url=request.form.get("url")))
                except ValueError, e:
                    return unicode(e), 403
            else:
                return form.errors, 403
    else:
        return _("没有此仓单%(id)d" % {"id": id_}), 404


@store_bill_page.route("/store-bill-list")
@decorators.templated("/store/store-bill-list.html")
@decorators.nav_bar_set
def store_bill_list():
    import lite_mms.apis as apis

    time_span = request.args.get("time_span", "week")
    customer_id = request.args.get("customer_id", 0, type=int)
    unprinted_only = request.args.get("printed_plan", 1, type=int)
    if time_span not in ["unlimited", "week", "month"]:
        return "参数time_span非法", 403
    customer = apis.customer.get_customer(customer_id) if customer_id else None
    page = request.args.get("page", 1, type=int)
    page_size = constants.STORE_BILL_PER_PAGE
    if time_span == "week":
        should_after = date.today() - timedelta(7)
    elif time_span == "month":
        should_after = date.today() - timedelta(30)
    else:
        should_after = None
    store_bills, total_cnt = apis.delivery.get_store_bill_list(
        (page - 1) * page_size,
        page_size, unlocked_only=False, should_after=should_after,
        customer_id=customer.id if customer else None,
        unprinted_only=unprinted_only)
    pagination = Pagination(page, constants.STORE_BILL_PER_PAGE, total_cnt)
    customer_list = apis.store.get_customer_list(time_span)
    return dict(titlename=u"仓单列表", store_bills=store_bills,
                time_span=time_span, customer_list=customer_list,
                printed_plan=unprinted_only,
                pagination=pagination)


@store_bill_page.route("/store-bill-preview/<int:id_>",
                       methods=["GET", "POST"])
@decorators.templated("/store/store-bill-preview.html")
@decorators.nav_bar_set
def store_bill_preview(id_):
    import lite_mms.apis as apis

    store_bill = apis.delivery.get_store_bill(id_)
    if store_bill:
        if request.method == "GET":
            return dict(titlename=u'仓单详情', store_bill=store_bill,
                        harbors=apis.harbor.get_harbor_list())
    else:
        return _("没有此仓单%(id)d" % {"id": id_}), 404