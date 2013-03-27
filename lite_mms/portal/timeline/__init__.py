#-*- coding:utf-8 -*-
from flask import Blueprint

time_line_page = Blueprint("timeline", __name__, static_folder="static",
                           template_folder="templates")

import views