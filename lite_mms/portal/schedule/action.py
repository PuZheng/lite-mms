#-*- coding:utf-8 -*-
from flask.ext.databrowser.action import BaseAction
from flask import render_template

class ScheduleAction(BaseAction):
    def test_enabled(self, model):
        if sum(sb.remaining_weight for sb in model.sub_order_list) > 0:
            return 0
        else:
            return -2

    def get_forbidden_msg_formats(self):
        return {
            -2: u"订单[%s]已全部排产"
        }

    def op(self, model):
        return render_template("schedule/order.html", order=model)


schedule_action = ScheduleAction(u"排产")