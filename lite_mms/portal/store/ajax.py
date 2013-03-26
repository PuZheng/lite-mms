# -*- coding: UTF-8 -*-
"""
@author: Yangminghua
@version: $
"""
from flask import request
from lite_mms.portal.store import store_bill_page
from lite_mms.utilities.decorators import ajax_call
import json
from lite_mms.utilities import _

@store_bill_page.route("/ajax/store-bill", methods=['PUT'])
@ajax_call
def ajax_store_bill():
    """
    return the customers, params include:
    * delivery_session_id
    """
    store_bill_id = request.form["id"]
    harbor = request.form["harbor"]
    if store_bill_id is not None:
        from lite_mms import apis

        try:
            apis.delivery.update_store_bill(int(store_bill_id), printed=True,
                                            harbor=harbor)
            return ""
        except ValueError, e:
            return unicode(e), 403
    return u"需要ID", 403


@store_bill_page.route("/ajax/customer-list", methods=['GET'])
@ajax_call
def customer_list():
    """
    返回一定时间段内，有仓单的客户列表
    """
    time_span = request.args.get("time_span", "unlimited")
    if time_span not in ["unlimited", "week", "month"]:
        raise _("参数time_span非法"), 403
    if time_span == "unlimited":
        time_span = ""
    from lite_mms import apis

    customers = apis.store.get_customer_list(time_span=time_span)
    return json.dumps(
        [dict(name=c.name, abbr=c.abbr, id=c.id) for c in customers])
