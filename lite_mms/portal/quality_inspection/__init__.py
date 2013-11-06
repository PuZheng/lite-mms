#-*- coding:utf-8 -*-
from flask import Blueprint
from flask.ext.login import login_required

from lite_mms.basemain import data_browser, nav_bar

from lite_mms.portal.quality_inspection.views import qir_model_view

qir_page = Blueprint("qir", __name__, static_folder="static", template_folder="templates")
data_browser.register_model_view(qir_model_view, qir_page, {"form_view": {"nav_bar": nav_bar, "titlename": u"质检报告"},
                                                            "list_view": {"nav_bar": nav_bar, "titlename": u"质检报告列表"}})


@qir_page.before_request
@login_required
def _():
    pass