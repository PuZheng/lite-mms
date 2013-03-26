# -*- coding: UTF-8 -*-
"""
@author: Yangminghua
@version: $
"""
from flask import request
from lite_mms.permissions import CargoClerkPermission
from lite_mms.permissions.order import view_order, schedule_order
from lite_mms.permissions.work_command import view_work_command
from lite_mms.utilities import decorators
from lite_mms.portal.search import search_page

@search_page.route("/search")
@decorators.templated("/search/search-result.html")
@decorators.nav_bar_set
def search():
    # TODO only order supported now
    import lite_mms.apis as apis

    keywords = request.args.get("content")
    wc_list = order_list = unload_session_list = \
    delivery_session_list = None
    if keywords:
        if view_order.can() or schedule_order.can():
            order_list = apis.order.get_order_list(
                customer_order_number=keywords)[0]
        if view_work_command.can():
            wc_list = apis.manufacture.get_work_command_list(
                keywords=keywords, status_list=0)[0]
        if CargoClerkPermission.can():
            unload_session_list = apis.cargo.get_unload_session_list(
                keywords=keywords)[0]
            delivery_session_list = apis.delivery.get_delivery_session_list(
                keywords=keywords)[0]
    return dict(titlename=u'搜索结果',
                order_list=order_list,
                keywords=keywords,
                work_command_list=wc_list,
                unload_session_list=unload_session_list,
                delivery_session_list=delivery_session_list
    )
