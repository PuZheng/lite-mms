# -*- coding: UTF-8 -*-
from flask import Blueprint, redirect, url_for

manufacture_page = Blueprint("manufacture", __name__, static_folder="static",
                             template_folder="templates")

from lite_mms.portal.manufacture import views

from lite_mms.basemain import data_browser, nav_bar

extra_params = {
    "list_view": {
        "nav_bar": nav_bar,
        "titlename": u"工单列表",
    },
    "form_view": {
        "nav_bar": nav_bar,
        "titlename": u"编辑工单"
    }

}
data_browser.register_model_view(views.work_command_view, manufacture_page, extra_params)


@manufacture_page.route("/")
def index():
    return redirect(url_for("manufacture.work_command_list", status__in_ex="(1, 8)"))
