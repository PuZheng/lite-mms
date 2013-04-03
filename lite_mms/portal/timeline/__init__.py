#-*- coding:utf-8 -*-
from flask import Blueprint

time_line_page = Blueprint("timeline", __name__, static_folder="static",
                           template_folder="templates")

from lite_mms.portal.timeline import views
from lite_mms.basemain import data_browser, nav_bar

extra_params = {
    "list_view": {
        "nav_bar": nav_bar,
        #"sub_nav_bar": sub_nav_bar,
        "titlename": u"时间线",
    },
}
data_browser.register_model_view(views.time_line_model_view, time_line_page, extra_params=extra_params)
