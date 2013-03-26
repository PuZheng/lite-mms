# -*- coding: UTF-8 -*-
"""
@author: Yangminghua
@version: $
"""
from flask import Blueprint
from lite_mms.permissions import QualityInspectorPermission

store_bill_page = Blueprint("store_bill", __name__, static_folder="static",
                            template_folder="templates")

@store_bill_page.before_request
def _():
    with QualityInspectorPermission.require():
        pass

from . import views, ajax
