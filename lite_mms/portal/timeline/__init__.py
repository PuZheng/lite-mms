#-*- coding:utf-8 -*-
from datetime import datetime, timedelta
from flask import Blueprint, request

time_line_page = Blueprint("timeline", __name__, static_folder="static",
                           template_folder="templates")

from lite_mms.portal.timeline import views
from lite_mms.basemain import data_browser, nav_bar

from nav_bar import NavBar
sub_nav_bar = NavBar()
sub_nav_bar.register(lambda: views.time_line_model_view.url_for_list(), u"所有", 
    enabler=lambda: not views.obj_cls_fltr.real_value)

def _register_obj_cls(id_, title):
    sub_nav_bar.register(lambda: views.time_line_model_view.url_for_list(obj_class=id_), title,
        enabler=lambda: views.obj_cls_fltr.real_value == str(id_))

_register_obj_cls(views.ObjClsFilter.UNLOAD_SESSION, u"卸货会话")
_register_obj_cls(views.ObjClsFilter.GOODS_RECEIPT, u"收货单")
_register_obj_cls(views.ObjClsFilter.ORDER, u"订单")
_register_obj_cls(views.ObjClsFilter.WORK_COMMAND, u"工单")

extra_params = {
    "list_view": {
        "nav_bar": nav_bar,
        "sub_nav_bar": sub_nav_bar,
        "titlename": u"时间线",
        "today": datetime.today().date(),
        "yesterday": datetime.today().date() - timedelta(days=1)
    },
}
data_browser.register_model_view(views.time_line_model_view, time_line_page, extra_params=extra_params)
