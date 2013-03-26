# -*- coding: UTF-8 -*-
"""
@author: Yangminghua
@version: $
"""
from flask import Blueprint
from lite_mms.basemain import app
from lite_mms.permissions import AdminPermission

import_data_page = Blueprint("import_data", __name__, static_folder="static",
                             template_folder="templates")

from . import views
