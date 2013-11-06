# -*- coding: UTF-8 -*-
from flask import Blueprint, redirect, url_for
from flask.ext.login import login_required
from lite_mms.basemain import data_browser, nav_bar

order_page = Blueprint("order", __name__, static_folder="static", template_folder="templates")


@order_page.route("/")
def index():
    return redirect(url_for("order.order_list"))


from lite_mms.portal.order import ajax, views, filters

extra_params = {"list_view": {"nav_bar": nav_bar, "sub_nav_bar": views.sub_nav_bar,
                              "hint_message": views.hint_message, "titlename": u"订单管理"},
                "form_view": {"nav_bar": nav_bar, "titlename": u"订单详情"}}
data_browser.register_model_view(views.order_model_view, order_page, extra_params=extra_params)

extra_params = {"list_view": {"nav_bar": nav_bar, "titlename": u"子订单管理"},
                "form_view": {"nav_bar": nav_bar, "titlename": u"子订单详情"}}
data_browser.register_model_view(views.sub_order_model_view, order_page, extra_params=extra_params)