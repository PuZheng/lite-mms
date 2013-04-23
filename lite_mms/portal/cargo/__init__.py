# -*- coding: UTF-8 -*-

from flask import Blueprint
from lite_mms.permissions import CargoClerkPermission

cargo_page = Blueprint("cargo", __name__, static_folder="static",
                       template_folder="templates")


@cargo_page.before_request
def _():
    with CargoClerkPermission.require():
        pass

from lite_mms.portal.cargo.views import (unload_session_model_view, plate_model_view, goods_receipt_entry_view)
from lite_mms.basemain import data_browser, nav_bar


def _do_register(model_view):
    extra_params = {
        "list_view": {
            "nav_bar": nav_bar,
            "titlename": model_view.model_name + u"列表",
        },
        "create_view": {
            "nav_bar": nav_bar,
            "titlename": u"创建" + model_view.model_name,
        },
        "form_view": {
            "nav_bar": nav_bar,
            "titlename": u"编辑" + model_view.model_name,
        }

    }
    data_browser.register_model_view(model_view, cargo_page, extra_params)


for model_view in [unload_session_model_view, goods_receipt_entry_view,
                   plate_model_view]:
    _do_register(model_view)

from . import views, ajax
