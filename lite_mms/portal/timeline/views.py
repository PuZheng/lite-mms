#-*- coding:utf-8 -*-
from flask import request
from . import time_line_page
from lite_mms.utilities.decorators import templated, nav_bar_set

@time_line_page.route("/")
@templated("timeline/timeline.html")
@nav_bar_set
def index():
    from lite_mms import apis

    user_id = request.args.get("user_id", type=int)
    create_time1 = create_time2 = None
    if request.args.getlist("create_time"):
        create_time1, create_time2 = request.args.getlist("create_time")
    days = request.args.get("days", type=int)
    log_list = apis.log.LogWrapper.get_log_list(user_id, create_time1,
                                                create_time2, days)
    user_list = apis.auth.get_user_list()
    return {"titlename": u"时间线", "log_list": log_list, "user_list": user_list}
