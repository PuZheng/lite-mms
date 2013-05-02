# -*- coding: UTF-8 -*-
from flask import Blueprint, redirect, url_for, json

manufacture_page = Blueprint("manufacture", __name__, static_folder="static",
                             template_folder="templates")

from lite_mms.portal.manufacture import views, ajax

from lite_mms.apis.manufacture import get_department_list

from lite_mms.basemain import data_browser, nav_bar

department_list = dict((d.id, [dict(id=p.id, text=p.name) for p in d.procedure_list]) for d in get_department_list())

def _do_register(model_view):
    extra_params = {
        "list_view": {
            "nav_bar": nav_bar,
            "titlename": model_view.model_name + u"列表",
        },
        "form_view": {
            "nav_bar": nav_bar,
            "titlename": u"编辑" + model_view.model_name,
            "department_list": department_list
        }

    }
    data_browser.register_model_view(model_view, manufacture_page, extra_params)

_do_register(views.work_command_view)

@manufacture_page.route("/")
def index():
    return redirect(url_for("manufacture.work_command_list"))