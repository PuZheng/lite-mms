# -*- coding: utf-8 -*-
from flask import Blueprint, request, url_for
from flask.ext.principal import PermissionDenied
from lite_mms.permissions import CargoClerkPermission, AdminPermission

order2_page = Blueprint("order2", __name__, static_folder="static", template_folder="templates")

from .filters import category_filter

from flask.ext.databrowser import ModelView
from flask.ext.databrowser.column_spec import PlaceHolderColumnSpec


class OrderModelView(ModelView):

    list_template = "order2/order-list.html"

    def try_create(self):
        raise PermissionDenied

    __list_columns__ = ["id", "customer_order_number", "goods_receipt.customer", "net_weight","remaining_weight",
                        PlaceHolderColumnSpec(col_name="manufacturing_work_command_list", label=u"生产中重量", template_fname="order/todo-work-command-list-snippet.html", doc=u"若大于0,请敦促车间生产"),
                        PlaceHolderColumnSpec(col_name="qi_work_command_list", label=u"待质检重量", template_fname="order/qi-list-snippet.html"),
                        PlaceHolderColumnSpec(col_name="done_work_command_list", label=u"已完成重量", template_fname="order/done-work-command-list-snippet.html", doc=u"指订单下所有是最后一道工序的工单,这类工单的工序后质量之和"),
                        PlaceHolderColumnSpec(col_name="to_deliver_store_bill_list", label=u"待发货重量", template_fname="order/store-bill-list-snippet.html"),
                        "delivered_weight", "create_time", "goods_receipt", "urgent", "refined"]

    __sortable_columns__ = ["id", "customer_order_number", "goods_receipt.customer", "create_time", "goods_receipt"]

    __column_labels__ = {"customer_order_number": u"订单号", "goods_receipt.customer": u"客户", "create_time": u"创建时间",
                         "goods_receipt": u"收货单", "net_weight": u"收货重量", "remaining_weight": u"待调度重量",
                         "delivered_weight": u"已发货重量", "refined": u"完善", "urgent": u"加急",
                         "category": u"类型", }

    __column_docs__ = {"remaining_weight": u"若大于0,请敦促调度员排产"}

    __column_formatters__ = {"urgent": lambda v, obj: u"是" if v else u"否", 
        "customer_order_number": lambda v, obj: ("" if not obj.warning else '<i class="icon-exclamation-sign"></i>') + v + (u"<b>(退货)</b>" if any(so.returned for so in obj.sub_order_list) else ""), 
        "remaining_weight": lambda v, obj: unicode(v + obj.to_work_weight),
        "refined": lambda v, obj: u"是" if v else u"否",
        "create_time": lambda v, obj: v.strftime("%m-%d %H") + u"点", 
        }

    from flask.ext.databrowser import filters                             
    from datetime import datetime, timedelta                              
    today = datetime.today()                                              
    yesterday = today.date()                                                 
    week_ago = (today - timedelta(days=7)).date()                         
    _30days_ago = (today - timedelta(days=30)).date()      

    __column_filters__ = [filters.EqualTo("goods_receipt.customer", name=u"是"), 
                          filters.BiggerThan("create_time", name=u"在", 
                              options=[(yesterday, u'一天内'), (week_ago, u'一周内'), (_30days_ago, u'30天内')]),
                          category_filter]
    
    def preprocess(self, model):
        from lite_mms import apis
        return apis.order.OrderWrapper(model)


    def try_view(self, objs=None):
        from flask.ext.principal import Permission
        Permission.union(CargoClerkPermission, AdminPermission).test()

    from lite_mms.portal.order2.actions import dispatch_action, mark_refined_action, account_action
    __customized_actions__ = [dispatch_action, mark_refined_action, account_action]

    def patch_row_attr(self, idx, row):
        if not row.refined:
            return {"class":"alert alert-warning", "title":u"此订单没有完善，请先完善订单"}
        elif row.urgent and row.remaining_quantity:
            return {"class":"alert alert-error", "title": u"此订单请加急完成"}
        elif row.warning:
            return {"title": u"此订单的收货重量大于未分配重量，生产中重量，已发货重量，待发货重量之和"}

    def url_for_object(self, model, **kwargs):
        if model:
            return url_for("order.order", id_=model.id, **kwargs)
        else:
            return url_for("order2.order")

    # =================== FORM PARTS ===================================

    from flask.ext.databrowser.column_spec import (InputColumnSpec, 
        LinkColumnSpec, ColumnSpec, TableColumnSpec, ImageColumnSpec)
    #__form_columns__ = [InputColumnSpec("customer_order_number", read_only=lambda obj: not obj.dispatched), 
        #"goods_receipt.customer", ColumnSpec("goods_receipt", css_class="control-text", label=u"收货单"),
        #"net_weight", InputColumnSpec("create_time", read_only=True), 
        #TableColumnSpec("sub_order_list", label=u"子订单列表", sum_fields=["weight", "manufacturing_weight", "delivered_weight", "to_deliver_weight"],  
            #col_specs=[ColumnSpec("id", label=u"子订单号"), ColumnSpec("product", label=u"产品"), 
            #ColumnSpec("tech_req", label=u"技术要求"), ColumnSpec("due_time", label=u"交货日期", formatter=lambda v, model: v or ""), 
            #ColumnSpec("weight", label=u"净重", formatter=lambda v, model: unicode(v) + u"(公斤)"), 
            #ColumnSpec("harbor", label=u"装卸点"),
            #ColumnSpec("urgent", label=u"加急", formatter=lambda v, model: u"是" if v else u"否"), 
            #ColumnSpec("returned", label=u"退货", formatter=lambda v, model: u"是" if v else u"否"),
            #ColumnSpec("manufacturing_weight", label=u"生产中重量", formatter=lambda v, model: unicode(v)+u"(公斤)"), 
            #ColumnSpec("delivered_weight", label=u"已发货重量", formatter=lambda v, model: unicode(v)+u"(公斤)"), 
            #ColumnSpec("to_deliver_weight", label=u"待发货重量", formatter=lambda v, model: unicode(v)+u"(公斤)"), 
            #ImageColumnSpec("pic_url", label=u"图片")]), 
        #TableColumnSpec("work_command_list", label=u"工单列表", 
            #col_specs=["id", "sub_order.id", "product", "org_weight", "org_cnt", "processed_weight", 
            #"processed_cnt", "department", "team", "qi", "status"])] 

from lite_mms.basemain import app, data_browser, nav_bar as main_nav_bar
from lite_mms.database import db
from lite_mms.models import Order, GoodsReceipt, Customer
from lite_mms import constants
from nav_bar import NavBar

order_model_view = OrderModelView(Order, u"订单")
sub_nav_bar = NavBar()
sub_nav_bar.register(lambda: order_model_view.url_for_list(order_by="id", desc="1", category=""), u"所有订单", 
    enabler=lambda: category_filter.unfiltered(request.args.get("category", None)))
sub_nav_bar.register(lambda: order_model_view.url_for_list(order_by="id", desc="1", category=str(category_filter.UNDISPATCHED_ONLY)), 
        u"仅展示待下发订单", enabler=lambda: request.args.get("category", "")==str(category_filter.UNDISPATCHED_ONLY))
sub_nav_bar.register(lambda: order_model_view.url_for_list(order_by="id", desc="1", category=category_filter.DELIVERABLE_ONLY),
        u"仅展示可发货订单", enabler=lambda: request.args.get("category", "")==str(category_filter.DELIVERABLE_ONLY))
sub_nav_bar.register(lambda: order_model_view.url_for_list(order_by="id", desc="1", category=category_filter.ACCOUNTABLE_ONLY),
        u"仅展示可盘点订单", enabler=lambda: request.args.get("category", "")==str(category_filter.ACCOUNTABLE_ONLY))
# sub_nav_bar.register(lambda: url_for("order2.warning_order_list"), u"仅展示告警订单", enabler=lambda: request.path=="warning-order-list")


def hint_message(model_view):
    
    filter = [filter for filter in model_view.parse_filters() if filter.col_name=="category"][0]
    if not filter.has_value():
        return ""
    filter.value = int(filter.value)

    if filter.value == category_filter.UNDISPATCHED_ONLY:
        return u"未下发订单未经收发员下发，调度员不能排产，请敦促收发员完善订单并下发"
    elif filter.value == category_filter.DELIVERABLE_ONLY:
        return u"可发货订单中全部或部分产品可以发货，注意请催促质检员及时打印仓单"
    elif filter.value == category_filter.ACCOUNTABLE_ONLY:
        return u"可盘点订单已经生产完毕（指已经全部分配给车间生产，最终生产完成，并通过质检），但是仍然有部分仓单没有发货。盘点后，这部分仓单会自动关闭"
    return ""


def get_customer_abbr_map(model_view):
    return dict((c.name, c.abbr) for c in Customer.query.all())

extra_params = {
    "list_view": {
        "nav_bar": main_nav_bar,
        "sub_nav_bar": sub_nav_bar,
        "hint_message": hint_message,
        "titlename": u"订单管理",
        "customer_abbr_map": get_customer_abbr_map,
    }
}
data_browser.register_model_view(order_model_view, order2_page, extra_params=extra_params)


from lite_mms.portal.order2 import ajax, views
