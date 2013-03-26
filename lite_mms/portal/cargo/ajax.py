# -*- coding: UTF-8 -*-
from flask import request
from sqlalchemy.exc import SQLAlchemyError
from wtforms import Form, TextField, IntegerField
from lite_mms.portal.cargo import cargo_page
from lite_mms.utilities.decorators import ajax_call
import json
from lite_mms.utilities import _

@cargo_page.route("/ajax/receipts-list", methods=["GET"])
@ajax_call
def receipts_list():
    session_id = request.args.get("unload_session_id", type=int)
    if session_id is not None:
        import lite_mms.apis as apis

        receipts = apis.cargo.get_goods_receipts_list(session_id)
        if not receipts:
            return _(u"当前没有任何收货单"), 404
        return json.dumps([dict(id=r.id, receipt_id=str(r.receipt_id),
                                customer=r.customer.name)
                           for r in receipts])
    else:
        return u"未选择卸货会话", 403


@cargo_page.route("/ajax/goods-receipt", methods=["POST"])
@ajax_call
def ajax_receipt():
    class _POST_Form(Form):
        id = TextField("id")
        task_id = TextField("task_id")
        product_id = TextField("product_id")
        weight = IntegerField("weight")


    form = _POST_Form(request.form)
    receipt_id = form.id.data

    if receipt_id:
        try:
            import lite_mms.apis as apis

            apis.cargo.get_goods_receipt(receipt_id).update(
                printed=True)
            return _(u"更新成功")
        except SQLAlchemyError:
            return _(u"更新失败"), 403
        except AttributeError:
            return _(u"无此收货单"), 404
    else:
        task_id = form.task_id.data
        product_id = form.product_id.data
        weight = form.weight.data or '' #integer field默认值为None。所以需要将None设置为''
        import lite_mms.apis as apis

        ut = apis.cargo.get_unload_task(task_id)
        if not ut or not (product_id or weight):
            return _(u"数据错误"), 404
        try:
            if ut.sub_order:
                ut.sub_order.update(product_id=product_id, weight=weight)
            ut.update(product_id=product_id, weight=weight)
            return _(u"更新成功")
        except ValueError, e:
            return unicode(e), 403
        except SQLAlchemyError:
            return _(u"更新失败"), 403



