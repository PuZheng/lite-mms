# -*- coding: UTF-8 -*-
import json
from datetime import datetime
from flask import request
from lite_mms.utilities import _
from werkzeug.exceptions import BadRequest
from lite_mms.portal.delivery_ws import delivery_ws
from lite_mms.utilities import to_timestamp
from lite_mms.utilities.decorators import webservice_call 
from lite_mms.apis.delivery import DeliverySessionWrapper

@delivery_ws.route("/delivery-session-list", methods=["GET"])
@webservice_call("json")
def delivery_session_list():
    """
    get **unfinished** delivery sessions from database, accept no arguments
    """
    import lite_mms.apis as apis
    try:
        delivery_sessions, total_cnt = apis.delivery.get_delivery_session_list(unfinished_only=True)
    except BadRequest as inst:
        return str(inst), 403 
    data = [{'plateNumber': ds.plate, 'sessionID': ds.id, 'isLocked': int(ds.is_locked)} for ds in 
        delivery_sessions]
    return json.dumps(data)

@delivery_ws.route("/delivery-session", methods=["GET"])
@webservice_call("json")
def delivery_session():
    """
    get delivery session from database
    """
    _id = request.args.get("id", type=int)
    if not _id:
        return _(u"需要id字段"), 403
    import lite_mms.apis as apis
    ds = apis.delivery.get_delivery_session(_id)
    if not ds:
        return _(u"没有如下发货会话") + str(_id), 404
    ret = dict(id=ds.id, plate=ds.plate)
    # store_bills是个两层结构，第一层是order，第二层主键是suborder
    store_bills = {}
    for sb in ds.store_bill_list:
        if not sb.delivery_task: # not delivered yet
            sub_order_2_store_bill = store_bills.setdefault(str(sb.sub_order.order.customer_order_number), {})
            sb_list = sub_order_2_store_bill.setdefault(sb.sub_order.id, [])
            sb_list.append(dict(id=sb.id, harbor=sb.harbor.name,
                                product_name=sb.product_name,
                                spec=sb.sub_order.spec,
                                type=sb.sub_order.type,
                                customer_name=sb.customer.name,
                                pic_url=sb.pic_url, unit=sb.sub_order.unit,
                                weight=sb.weight))
    ret.update(store_bills=store_bills)
    return json.dumps(ret)

@delivery_ws.route("/delivery-task", methods=["POST"])
@webservice_call("json")
def delivery_task():
    actor_id = request.args.get("actor_id", type=int)
    is_finished = request.args.get("is_finished", type=int)
    remain = request.args.get("remain", type=int)

    if not actor_id:
        return _(u"需要actor_id字段"), 403
    
    json_sb_list = json.loads(request.data)
    if len(json_sb_list) == 0:
        return _(u"至少需要一个仓单"), 403
    finished_sb_list = []
    unfinished_sb_list = [] 
    for json_sb in json_sb_list:
        if json_sb["is_finished"]:
            finished_sb_list.append(json_sb["store_bill_id"])
        else:
            unfinished_sb_list.append(json_sb["store_bill_id"])
    if len(unfinished_sb_list) > 1:
        return _(u"最多只有一个仓单可以部分完成"), 403
    if unfinished_sb_list:
        if not remain:
            return _(u"需要remain字段"), 403

    import lite_mms.apis as apis
    try:
        dt = apis.delivery.new_delivery_task(actor_id,
                finished_sb_list, unfinished_sb_list[0] if unfinished_sb_list else None, 
                remain)
    except BadRequest, e:
        return str(e), 403

    if is_finished: # 卸货会话结束
       apis.delivery.get_delivery_session(
            dt.delivery_session_id).update(finish_time=to_timestamp(datetime.now()))

    ret = dict(id=dt.actor_id, actor_id=dt.actor_id,
            store_bill_id_list=dt.store_bill_id_list)
    return json.dumps(ret)
        

