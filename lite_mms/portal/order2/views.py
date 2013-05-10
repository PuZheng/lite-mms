# -*- coding: utf-8 -*-

from flask import request
from lite_mms.portal.order2 import order2_page
from lite_mms.utilities.decorators import templated

@order2_page.route("warning-order-list", methods=["GET"])
@templated("/order2/warning-order-list.html")
def warning_order_list():
    from lite_mms.apis.order import OrderWrapper
    from lite_mms.models import Order
    ret = {"order_list": [], "title_name": u"警告订单列表"}
    for o in Order.query.order_by(-Order.id).all():
        o = OrderWrapper(o)
        if o.warning:
            ret["order_list"].append(o)
    return ret
            
