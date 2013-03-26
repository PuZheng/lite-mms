# -*- coding: utf-8 -*-
from flask import request
from lite_mms.portal.order2 import order2_page
from lite_mms.utilities.decorators import ajax_call
from lite_mms.utilities import get_or_404, dictview
import json
from lite_mms.models import Order

@order2_page.route("/ajax/team-work-reports", methods=["GET"])
@ajax_call
def team_work_reports():
    order_id = request.args.get("order_id")
    ret = {}
    order = get_or_404(Order, int(order_id))
    for wc in order.done_work_command_list:
        try:
            ret[wc.team.name] += wc.processed_weight
        except KeyError:
            ret[wc.team.name] = wc.processed_weight
    return json.dumps(ret.items())

@order2_page.route("/ajax/team-manufacturing-reports", methods=["GET"])
@ajax_call
def team_manufacturing_reports():
    order_id = request.args.get("order_id")
    ret = {}
    order = get_or_404(Order, int(order_id))
    d = {}
    for so in order.sub_order_list:
        for wc in so.manufacturing_work_command_list:
            try:
                d[wc.department.name+u"车间:"+(wc.team.name if wc.team else u"尚未分配")+ u"班组"] += wc.org_weight
            except KeyError:
                d[wc.department.name+u"车间:"+(wc.team.name if wc.team else u"尚未分配")+ u"班组"] = wc.org_weight
    return json.dumps(sorted([dict(team=k, weight=v) for k, v in d.items()], key=lambda v: v["team"]))

@order2_page.route("/ajax/store-bill-list", methods=["GET"])
@ajax_call
def store_bill_list():
    order_id = request.args.get("order_id")
    order = get_or_404(Order, int(order_id)) 
    ret = []
    for so in order.sub_order_list:
        for sb in so.store_bill_list:
            ret.append(dict(id=sb.id, product=so.product.name, spec=so.spec, type=so.type, weight=sb.weight))
    return json.dumps(ret)
