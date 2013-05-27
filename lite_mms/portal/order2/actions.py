# -*- coding: utf-8 -*-
from flask.ext.databrowser.action import BaseAction

class DispatchAction(BaseAction):
    
    def op(self, model):
        model.update(dispatched=True)

    def test_enabled(self, model):
        if model.dispatched:
            return -2
        elif not model.refined:
            return -3
        return 0 
    
    def get_forbidden_msg_formats(self):
        return {
            -2: u"订单[%s]已经下发,不能重复下发",
            -3: u"订单[%s]没有完善，请先完善"
        }
    
    def try_(self, preprocessed_objs):
        from lite_mms.permissions import CargoClerkPermission,AdminPermission
        from flask.ext.principal import Permission
        Permission.union(CargoClerkPermission, AdminPermission).test()
    
class AccountAction(BaseAction):
    def op(self, order):
        for sub_order in order.sub_order_list:
            for store_bill in sub_order.store_bill_list:
                fake_delivery_task = apis.delivery.fake_delivery_task()
                if not store_bill.delivery_task:
                    apis.delivery.update_store_bill(store_bill.id,
                                                    delivery_session_id=fake_delivery_task.delivery_session.id,
                                                    delivery_task_id=fake_delivery_task.id)
            sub_order.end()
        order.update(
            finish_time=datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"))


    def try_(self, preprocessed_objs):
        from lite_mms.permissions import CargoClerkPermission,AdminPermission
        from flask.ext.principal import Permission
        Permission.union(CargoClerkPermission, AdminPermission).test()

    def test_enabled(self, model):
        if not model.can_account:
            return -1

    def get_forbidden_msg_formats(self):
        return {
            -1: u"该订单不能盘点，原因可能是：没有排产完毕，正在生产，或者已经完全发货"
        }

class MarkRefinedAction(BaseAction):
    def op(self, model):
        model.update(refined=True)
    
    def test_enabled(self, model):
        if model.refined:
            return -2
        elif not model.can_refine:
            return -3
        return 0

    def get_forbidden_msg_formats(self):
        return {
            -2: u"订单[%s]已经标记为完善", 
            -3: u"请先完善订单[%s]内容（添加子订单或者填写子订单的产品信息，完成时间），才能标记为完善",
        }

    def try_(self, preprocessed_objs):
        from lite_mms.permissions import CargoClerkPermission,AdminPermission
        from flask.ext.principal import Permission
        Permission.union(CargoClerkPermission, AdminPermission).test()

dispatch_action = DispatchAction(u"下发")
account_action = AccountAction(u"盘点")
mark_refined_action = MarkRefinedAction(u"标记为完善")
