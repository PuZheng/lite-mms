# -*- coding: UTF-8 -*-

from flask import Blueprint, redirect
from flask.ext.login import login_required

delivery_page = Blueprint("delivery", __name__, static_folder="static", template_folder="templates")

consignment_page = Blueprint("consignment", __name__, static_folder="static", template_folder="templates")

from lite_mms.portal.delivery import views, ajax

from lite_mms.basemain import data_browser, nav_bar

from view import delivery_session_view, delivery_task_view, consigment_model_view, consigment_product_model_view

extra_params = {
    "list_view": {
        "nav_bar": nav_bar,
        "titlename": u"发货单列表",
    },
    "form_view": {
        "nav_bar": nav_bar,
        "titlename": u"编辑发货单",
    }
}
data_browser.register_model_view(consigment_model_view, consignment_page, extra_params)

extra_params = {
    "form_view": {
        "nav_bar": nav_bar,
        "titlename": u"编辑发货单项",
    }
}
data_browser.register_model_view(consigment_product_model_view, consignment_page, extra_params)

from lite_mms.apis import delivery
get_customer_list = delivery.get_store_bill_customer_list

data_browser.register_model_view(delivery_session_view, delivery_page,
                                 extra_params={"list_view": {"nav_bar": nav_bar, "titlename": u"发货会话列表"},
                                               "create_view": {"nav_bar": nav_bar, "titlename": u"新建发货会话", "get_customer_list": get_customer_list},
                                               "form_view": {"nav_bar": nav_bar, "titlename": u"编辑发货会话"}})

data_browser.register_model_view(delivery_task_view, delivery_page,
                                 extra_params={"form_view": {"nav_bar": nav_bar, "titlename": u"编辑任务会话"}})

@consignment_page.route("/")
def index():
    return redirect(consigment_model_view.url_for_list(order_by="create_time", desc=1))

@consignment_page.before_request
@login_required
def _():
    pass

@delivery_page.before_request
@login_required
def _():
    pass