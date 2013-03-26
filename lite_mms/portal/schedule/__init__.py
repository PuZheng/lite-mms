# -*- coding: UTF-8 -*-
"""
@author: Yangminghua
@version: $
"""
from flask import Blueprint
from lite_mms.permissions import SchedulerPermission

schedule_page = Blueprint("schedule", __name__, static_folder="static",
                            template_folder="templates")
@schedule_page.before_request
def _():
    with SchedulerPermission.require():
        pass

from lite_mms.portal.schedule import views, ajax

