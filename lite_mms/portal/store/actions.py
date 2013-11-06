#-*- coding:utf-8 -*-
from flask.ext.databrowser.action import DirectAction
from flask import redirect, url_for, request, json


class PreviewPrintAction(DirectAction):
    def op_upon_list(self, objs, model_view):
        if objs:
            for obj in objs:
                obj.printed = True
            return redirect(
                url_for("store_bill.store_bill_preview", ids_=json.dumps([obj.id for obj in objs]), url=request.url))

    def test_enabled(self, model):
        if not model.harbor:
            return -2
        return 0

    def get_forbidden_msg_formats(self):
        return {-2: u"仓单%s没有存放点，请先修改"}