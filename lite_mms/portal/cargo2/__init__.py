# -*- coding: utf-8 -*-
from flask import Blueprint, request, url_for, render_template
from flask.ext.principal import PermissionDenied
from wtforms import Form, IntegerField, validators, ValidationError
from sqlalchemy.orm.exc import NoResultFound

from lite_mms.basemain import app, data_browser, nav_bar


cargo2_page = Blueprint("cargo2", __name__, static_folder="static", 
                       template_folder="templates")

from lite_mms.portal.cargo2.views import (goods_receipt_model_view, 
                                          unload_session_model_view, vehicle_model_view, 
                                          unload_task_model_view)

from lite_mms.portal.cargo2 import ajax

extra_params = {
    "list_view": {
        "nav_bar": nav_bar,
        "titlename": u"卸货会话列表",
    },
    "form_view": {
        "nav_bar": nav_bar,
        "titlename": u"卸货会话",
    }

}

data_browser.register_model_view(unload_session_model_view, cargo2_page, extra_params=extra_params)

extra_params = {
    "form_view": {
        "nav_bar": nav_bar,
        "titlename": u"车辆管理",
    }
}

data_browser.register_model_view(vehicle_model_view, cargo2_page, extra_params=extra_params)
data_browser.register_model_view(goods_receipt_model_view, cargo2_page, extra_params=extra_params)
data_browser.register_model_view(unload_task_model_view, cargo2_page, extra_params=extra_params)

