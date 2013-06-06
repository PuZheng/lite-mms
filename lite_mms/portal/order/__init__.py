# -*- coding: UTF-8 -*-
from flask import Blueprint
from flask.ext.login import login_required
from lite_mms.basemain import data_browser, nav_bar

order_page = Blueprint("order", __name__, static_folder="static", template_folder="templates")


@order_page.before_request
@login_required
def _():
    pass


from lite_mms.portal.order import ajax, views, filters, model_views

extra_params = {"list_view": {"nav_bar": nav_bar, "sub_nav_bar": model_views.sub_nav_bar,
                              "hint_message": model_views.hint_message, "titlename": u"订单管理"},
                "form_view": {"nav_bar": nav_bar, "titlename": u"订单详情"}}
data_browser.register_model_view(model_views.order_model_view, order_page, extra_params=extra_params)

extra_params = {"list_view": {"nav_bar": nav_bar, "titlename": u"子订单管理"},
                "form_view": {"nav_bar": nav_bar, "titlename": u"子订单详情"}}
data_browser.register_model_view(model_views.sub_order_model_view, order_page, extra_params=extra_params)