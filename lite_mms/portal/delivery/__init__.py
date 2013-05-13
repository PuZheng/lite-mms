# -*- coding: UTF-8 -*-

from flask import Blueprint

delivery_page = Blueprint("delivery", __name__, static_folder="static", 
    template_folder="templates")

consignment_page = Blueprint("consignment", __name__, static_folder="static", 
    template_folder="templates")

from lite_mms.portal.delivery import views, ajax

from lite_mms.portal.delivery.views import consigment_model_view, consigment_product_model_view

from lite_mms.basemain import data_browser, nav_bar

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
