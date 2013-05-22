# -*- coding: UTF-8 -*-
"""
@author: Yangminghua
@version: $
"""
from flask import Blueprint
from lite_mms.permissions import QualityInspectorPermission

store_bill_page = Blueprint("store_bill", __name__, static_folder="static",
                            template_folder="templates")

from . import views, ajax

from .view import store_bill_view

from lite_mms.basemain import data_browser,nav_bar

data_browser.register_model_view(store_bill_view, store_bill_page,
                                 extra_params={"list_view": {"nav_bar": nav_bar, "titlename": u"仓单列表"},
                                               "form_view": {"nav_bar": nav_bar, "titlename": u"编辑仓单"}})