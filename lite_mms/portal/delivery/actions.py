#-*- coding:utf-8 -*-
from flask import redirect, url_for, request
from flask.ext.databrowser.action import BaseAction, ReadOnlyAction

from lite_mms.utilities.decorators import committed
from lite_mms import constants


class CloseAction(BaseAction):
    def test_enabled(self, model):
        if model.status in [constants.delivery.STATUS_CLOSED, constants.delivery.STATUS_DISMISSED]:
            return -2
        if not all(task.weight for task in model.delivery_task_list):
            return -3
        return 0

    def op(self, obj):
        from lite_mms.portal.cargo.fsm import fsm
        from flask.ext.login import current_user

        fsm.reset_obj(obj)
        fsm.next(constants.delivery.ACT_CLOSE, current_user)

    def get_forbidden_msg_formats(self):
        return {-2: u"发货会话%s已经被关闭",
                -3: u"发货会话%s有发货任务没有称重，请确保所有的发货任务都已经称重！"}


class OpenAction(ReadOnlyAction):
    def test_enabled(self, model):
        if model.status != constants.delivery.STATUS_CLOSED:
            return -2
        if any(cn.MSSQL_ID for cn in model.consignment_list):
            return -3
        return 0

    def op(self, obj):
        from lite_mms.portal.cargo.fsm import fsm
        from flask.ext.login import current_user

        fsm.reset_obj(obj)
        fsm.next(constants.delivery.ACT_OPEN, current_user)

    def get_forbidden_msg_formats(self):
        return {-2: u"发货会话%s处在打开状态, 只有已经关闭的会话才能被打开",
                -3: u"发货会话%s存在已导入旧系统的发货单，无法重新打开"}


class CreateConsignmentAction(ReadOnlyAction):
    def test_enabled(self, model):
        if model.consignment_list:
            if all(not cn.stale for cn in model.consignment_list) and len(
                    model.consignment_list) == len(model.customer_list):
                return -2
            if any(cn.MSSQL_ID for cn in model.consignment_list):
                return -3
        elif not model.delivery_task_list:
            return -4
        return 0

    def op(self, obj):
        obj.clean_goods_receipts()

    def get_forbidden_msg_formats(self):
        return {-2: u"发货会话%s已生成发货单",
                -3: u"发货会话%s存在已导入旧系统的发货单，无法重新生成",
                -4: u"发货会话%s没有发货任务，请先生成发货任务"}

class PrintConsignment(ReadOnlyAction):
    pass

class PayAction(BaseAction):
    @committed
    def op(self, obj):
        obj.is_paid = True


class PreviewConsignment(ReadOnlyAction):
    def op_upon_list(self, objs, model_view):
        return redirect(url_for("delivery.consignment_preview", id_=objs[0].id, url=request.url))
