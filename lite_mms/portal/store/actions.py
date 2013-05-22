#-*- coding:utf-8 -*-
from flask.ext.databrowser.action import ReadOnlyAction
from flask import redirect, url_for, request
class PreviewPrintAction(ReadOnlyAction):
    def op_upon_list(self, objs, model_view):
        if len(objs):
            return redirect(url_for("store_bill.store_bill_preview", id_=objs[0].id, url=request.url))
