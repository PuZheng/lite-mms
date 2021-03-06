# -*- coding: UTF-8 -*-
import json
from flask import request, render_template, abort, flash
from socket import error
from wtforms import Form, IntegerField, BooleanField, TextField
from lite_mms.portal.delivery import delivery_page
from lite_mms.utilities.decorators import ajax_call
from lite_mms.utilities import _


@delivery_page.route("/ajax/consignment-list", methods=["GET"])
@ajax_call
def consignment_list():
    session_id = request.args.get("delivery_session_id", type=int)
    if session_id is not None:
        import lite_mms.apis as apis

        consignments, totalcnt = apis.delivery.get_consignment_list(session_id)
        if not consignments:
            return _(u"当前没有任何发货单"), 404
        return json.dumps(
            [dict(id=c.id, customer=c.customer.name,
                  consignment_id=c.consignment_id) for c in consignments])
    else:
        return _(u"未选择发货会话"), 403


@delivery_page.route("/ajax/consignment", methods=["POST"])
@ajax_call
def ajax_consignment():
    class _ConsignmentForm(Form):
        id = IntegerField("id")

    form = _ConsignmentForm(request.form)
    consignment_id = form.id.data
    if consignment_id:
        import lite_mms.apis as apis
        cons = apis.delivery.get_consignment(consignment_id)
        if not cons:
            return _(u"不存在该发货单%d" % consignment_id), 404
        elif not cons.MSSQL_ID:
            try:
                cons.persist()
            except ValueError, error:
                return unicode(error.message), 403
            return _(u"更新成功")
    else:
        return _(u"数据错误"), 404


@delivery_page.route("/ajax/customer-list")
@ajax_call
def customer_list():
    """
    return the customers, params include:
    * delivery_session_id
    """
    delivery_session_id = request.args.get("delivery_session_id", type=int)
    customers = []
    if delivery_session_id is not None:
        import lite_mms.apis as apis

        delivery_session = apis.delivery.get_delivery_session(
            delivery_session_id)
        if not delivery_session.finish_time:
            return _(u"发货会话尚未结束"), 403
        if any(task.weight == 0 for task in delivery_session.delivery_task_list):
            return _(u"请先对所有的发货任务进行称重"), 403

        acked_customer_id_list = set([gr.customer_id for gr in
                                      delivery_session.consignment_list])
        customers = [c for c in delivery_session.customer_list if
                     c.id not in acked_customer_id_list]
        if not customers:
            return _(u"已经对所有的客户生成了发货单"), 403

    return json.dumps([{"id": c.id, "name": c.name} for c in customers])

@delivery_page.route("/ajax/delivery-task/<int:id_>", methods=["POST"])
@ajax_call
def delivery_task(id_):
    from lite_mms import apis
    task = apis.delivery.get_delivery_task(id_)
    if not task:
        abort(404)
    if task.weight:
        return _(u"已称重的发货任务不能删除"), 403
    try:
        task.delete()
        flash(u"删除成功")
        return "success"
    except Exception, e:
        return unicode(e), 403