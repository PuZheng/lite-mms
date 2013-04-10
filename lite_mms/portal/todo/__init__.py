#-*- coding:utf-8 -*-
from flask import Blueprint, request
from lite_mms.basemain import data_browser, nav_bar

from .views import to_do_view

to_do_page = Blueprint("todo", __name__, static_folder="static",
                       template_folder="templates")

data_browser.register_model_view(to_do_view, to_do_page, extra_params={
    "list_view": {"nav_bar": nav_bar, "titlename": u"待办事项"}})
