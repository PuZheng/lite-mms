# -*- coding: UTF-8 -*-
import json
from flask import request, render_template, url_for
from lite_mms.utilities import _
from lite_mms.portal.order import order_page
from lite_mms.utilities import decorators
from lite_mms.utilities.decorators import ajax_call

@order_page.route("/ajax/customer-list")
@ajax_call
def customer_list():
    """
    return the customers, params include:
    * unload_session_id
    """
    unload_session_id = request.args.get("unload_session_id", None)
    customers = []
    if unload_session_id:
        unload_session_id = int(unload_session_id)
        from lite_mms import apis
        unload_session = apis.cargo.get_unload_session(unload_session_id)
        if not unload_session.finish_time:
            return _(u"卸货会话尚未结束"), 403
        if any(task.weight == 0 for task in unload_session.task_list):
            return _(u"请先对所有的卸货任务进行称重"), 403
        acked_customer_id_list = set([gr.customer_id for gr in
                                      unload_session.goods_receipt_list])
        customers = [c for c in unload_session.customer_list if
                     c.id not in acked_customer_id_list]
    if not customers:
        return _(u"已经对所有的用户生成了收货单"), 403
    return json.dumps([{"id": c.id, "name": c.name} for c in customers])


@order_page.route("/ajax/order-modify", methods=["POST"])
@ajax_call
def order_modify():
    from lite_mms import apis
    order = apis.order.get_order(request.form["order_id"])
    if not order:
        return _(u"不存在订单ID为%s的订单" % request.form["order_id"]), 403
    if any(
        sub_order.work_command_list for sub_order in order.sub_order_list):
        return _(u"该订单已排产，请勿修改"), 500
    try:
        order.update(customer_order_number=request.form["customer_order_number"])
        return _(u"修改成功")
    except ValueError:
        return _(u"修改失败"), 403


@order_page.route("/ajax/sub-order", methods=["GET"])
@ajax_call
def ajax_sub_order():
    sub_order_id = request.args.get('id', type=int)
    if not sub_order_id:
        return _(u"不存在该订单"), 404
    from lite_mms import apis
    inst = apis.order.get_sub_order(sub_order_id)
    if not inst:
        return "no sub order with id " + str(sub_order_id), 404
    from lite_mms.basemain import nav_bar
    from lite_mms.constants import DEFAULT_PRODUCT_NAME

    param_dict = {'titlename': u'子订单详情', 'sub_order': inst, 'nav_bar': nav_bar,
                  'DEFAULT_PRODUCT_NAME': DEFAULT_PRODUCT_NAME}
    param_dict.update(product_types=apis.product.get_product_types())
    param_dict.update(products=json.dumps(apis.product.get_products()))
    param_dict.update(harbor_list=apis.harbor.get_harbor_list())
    purl = request.args.get("purl")
    if purl is None or purl == "None":
        purl = url_for("order.order_list")
    param_dict.update(purl=purl)
    return render_template("order/sub-order.html", **param_dict)
