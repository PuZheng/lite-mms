#-*- coding:utf-8 -*-
from flask import request
from . import time_line_page
from lite_mms.utilities.decorators import templated, nav_bar_set
from lite_mms.apis import wraps
from lite_mms.models import Log

from flask.ext.databrowser import ModelView
from flask.ext.databrowser.filters import EqualTo, Between

#@time_line_page.route("/")
#@templated("timeline/timeline.html")
#@nav_bar_set
#def index():
    #from lite_mms import apis

    #user_id = request.args.get("user_id", type=int)
    #create_time1 = create_time2 = None
    #if request.args.getlist("create_time"):
        #create_time1, create_time2 = request.args.getlist("create_time")
    #log_list = apis.log.get_log_list(user_id, create_time1,
                                                #create_time2)
    #from lite_mms.models import User
    #user_list = User.query.all()
    #return {"titlename": u"时间线", "log_list": log_list, "user_list": user_list}

class TimeLineModelView(ModelView):

    def scaffold_list(self, objs):

        for obj in objs:
            yield wraps(obj)

    list_template = "timeline/timeline.html"

    __column_labels__ = {"actor": u"操作员", "create_time": u"创建时间"}

    class MyBetween(Between):

        @property
        def input_type(self):
            return ("date", "date")

    __column_filters__ = [EqualTo("actor", u"是"), Between("create_time", u"从", sep=u"到")]


time_line_model_view = TimeLineModelView(Log, u"日志")
