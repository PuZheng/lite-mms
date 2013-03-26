# -*- coding: UTF-8 -*-
"""
@author: Yangminghua
@version: $
"""
from flask import request
from lite_mms.portal.schedule import schedule_page
from lite_mms.utilities.decorators import ajax_call, templated
from lite_mms.utilities import _

@schedule_page.route("/ajax/sub-order/<int:id_>")
@templated("/schedule/work-command.html")
@ajax_call
def ajax_sub_order(id_):
    from lite_mms import apis

    sub_order = apis.order.SubOrderWrapper.get_sub_order(id_)
    if not sub_order:
        return _(u"无此子订单"), 404
    try:
        dep = apis.harbor.get_harbor_model(sub_order.harbor.name).department
    except AttributeError:
        return _(u"无此装货点"), 404
    return dict(sub_order=sub_order, procedure_list=dep.procedure_list,
                     department=dep)

