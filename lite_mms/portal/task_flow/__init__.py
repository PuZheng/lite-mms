# -*- coding: UTF-8 -*-

from flask import Blueprint, render_template, request

task_flow_page = Blueprint("task_flow", __name__, static_folder="static",
                            template_folder="templates")

import lite_mms.portal.task_flow.views
