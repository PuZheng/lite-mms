# -*- coding: utf-8 -*-
from flask.ext.databrowser.action import DeleteAction, BaseAction
from lite_mms.constants import cargo as cargo_const

class MyDeleteAction(DeleteAction):

    def test_enabled(self, model):
        if model.goods_receipt_list:
            return -2

    def get_forbidden_msg_formats(self):
        return {-2: u"发货会话%s已经生成了收货单，请先删除对应收货单以后再删除此发货会话!"}

class CloseAction(BaseAction):

    def test_enabled(self, model):
        if model.status in [cargo_const.STATUS_CLOSED, cargo_const.STATUS_DISMISSED]:
            return -2

    def op(self, obj):
        obj.status = cargo_const.STATUS_CLOSED

    def get_forbidden_msg_formats(self):
        return {-2: u"发货会话%s已经被关闭"}

class OpenAction(BaseAction):

    def test_enabled(self, model):
        if model.status != cargo_const.STATUS_CLOSED:
            return -2

    def op(self, obj):
        obj.status = cargo_const.STATUS_LOADING

    def get_forbidden_msg_formats(self):
        return {-2: u"只有已经关闭的会话才能被打开"}
