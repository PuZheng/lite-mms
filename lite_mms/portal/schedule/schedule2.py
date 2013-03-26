# -*- coding: UTF-8 -*-
"""
@author: Yangminghua
@version: $
"""
import json
from flask import Blueprint, url_for, render_template, abort, request
from lite_mms import constants
from lite_mms.permissions import SchedulerPermission
from lite_mms.utilities import get_or_404

schedule_page2 = Blueprint("schedule2", __name__, static_folder="static",
                          template_folder="templates")


@schedule_page2.before_request
def _():
    with SchedulerPermission.require():
        pass


from lite_mms.portal.schedule import views, ajax

from lite_mms.portal.schedule.filters import filter_

from flask.ext.databrowser import ModelView, filters

from lite_mms.basemain import app, data_browser, nav_bar


class OrderView(ModelView):
    def __list_filters__(self):
        if SchedulerPermission.can():
            return [filters.EqualTo("finish_time", value=None),
                    filters.EqualTo("refined", value=True),
                    filters.EqualTo("dispatched", value=True),
                    filter_]
        else:
            return []

    list_template = "schedule/order-list.haml"

    __list_columns__ = ["id", "customer_order_number",
                        "goods_receipt.customer", "net_weight",
                        "remaining_weight", "to_work_weight",
                        "manufacturing_weight",
                        "create_time", "goods_receipt.receipt_id",
                        "urgent"]
    __column_labels__ = {"customer_order_number": u"订单号",
                         "goods_receipt.customer": u"客户",
                         "create_time": u"创建时间", "goods_receipt.receipt_id": u"收货单",
                         "net_weight": u"收货", "remaining_weight": u"待排产",
                         "manufacturing_weight":u"生产中",
                         "to_work_weight": u"待分配", "urgent": u"加急"
    }
    __column_formatters__ = {
        "urgent": lambda v, obj: u"是" if v else u"否",
        "customer_order_number": lambda v, obj: v + (
                                                    u"<b>(退货)</b>" if any(
                                                        so.returned for so in
                                                        obj.sub_order_list) else ""),
        "create_time": lambda v, obj: v.strftime(
            "%m-%d %H") + u"点",
        "to_work_weight":lambda v, obj: v and (u'<a href="#" class="to-work-weight-link" >%d</a><input type="hidden" value="%d" />' % (v, obj.id)),
        "manufacturing_weight": lambda v, obj: v and (u'<a href="#" class="manufacturing-weight-link" >%d</a><input type="hidden" value="%d" />' % (v, obj.id)),
        }

    def preprocess(self, model):
        from lite_mms import apis

        return apis.OrderWrapper(model)

    from datetime import datetime, timedelta

    today = datetime.today()
    yesterday = today.date()
    week_ago = (today - timedelta(days=7)).date()
    _30days_ago = (today - timedelta(days=30)).date()
    __column_filters__ = [filters.EqualTo("goods_receipt.customer", name=u"是"),
                          filters.BiggerThan("create_time", name=u"在",
                                             options=[(yesterday, u'一天内'),
                                                      (week_ago, u'一周内'),
                                                      (_30days_ago, u'30天内')]),
                          filters.Contains("customer_order_number",
                                           name=u"包含")]

    def patch_row_attr(self, idx, row):
        if row.urgent and row.remaining_weight > 0:
            return {"class": "text-error", "title": u"该订单加急，请尽快处理"}

    can_create = can_edit = False

    __sortable_columns__ = ["id", "customer_order_number",
                            "goods_receipt.customer", "create_time"]

    __default_order__ = ("id", "desc")

    from .action import schedule_action

    __customized_actions__ = [schedule_action]

    def edit_view(self, id_):
        order = self.get_one(id_)
        if not order:
            abort(404)
        return render_template("schedule/order.html",
                               order=self.preprocess(order),
                               nav_bar=nav_bar)


from lite_mms.models import Order, Customer


def get_customer_abbr_map(model_view):
    return dict((c.name, c.abbr) for c in Customer.query.all())


extra_params = {
    "form_view": {
        "nav_bar": nav_bar,
        "titlename": u"订单详情"
    },
    "list_view": {
        "nav_bar": nav_bar,
        "titlename": u"订单列表",
        "customer_abbr_map": get_customer_abbr_map,
    }
}

data_browser.register_model_view(OrderView(Order), schedule_page2,
                                 extra_params=extra_params)

from lite_mms.utilities.decorators import ajax_call
from lite_mms.apis.manufacture import get_wc_status_list

@schedule_page2.route("/ajax/to_dispatch")
@ajax_call
def to_dispatch():
    order_id = request.args.get("order_id", type=int)
    order = get_or_404(Order, order_id)
    list_ = []
    for sub_order in order.sub_order_list:
        for wc in sub_order.work_command_list:
            if wc.status in [constants.work_command.STATUS_DISPATCHING,
                             constants.work_command.STATUS_REFUSED]:
                list_.append(dict(id=wc.id, weight=wc.org_weight,
                                  status=get_wc_status_list().get(wc.status)[
                                      0]))
    return json.dumps(list_)