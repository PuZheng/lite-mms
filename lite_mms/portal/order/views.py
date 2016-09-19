# -*- coding: utf-8 -*-
"""
@author: Yangminghua
"""
from collections import OrderedDict
from datetime import date

from flask import request, url_for, render_template, abort, flash, redirect, json
from flask.ext.login import current_user, login_required
from flask.ext.principal import PermissionDenied, Permission
from flask.ext.databrowser import ModelView, filters
from flask.ext.databrowser.column_spec import (InputColumnSpec, LinkColumnSpec, ColumnSpec, TableColumnSpec,
                                               ImageColumnSpec, PlaceHolderColumnSpec)
from wtforms import Form, TextField, IntegerField, validators, BooleanField, DateField, HiddenField

from lite_mms import constants
from lite_mms.portal.order import order_page
from lite_mms.utilities import decorators
from lite_mms.permissions import SchedulerPermission, CargoClerkPermission
from lite_mms.models import Order, SubOrder, Product
from lite_mms.portal.order.filters import category_filter, only_unfinished_filter


class OrderModelView(ModelView):
    list_template = "order/order-list.html"

    def try_create(self):
        raise PermissionDenied

    can_batchly_edit = False

    @login_required
    def try_view(self, processed_objs=None):
        pass

    def __list_filters__(self):
        if SchedulerPermission.can():
            return [filters.EqualTo("finish_time", value=None),
                    filters.EqualTo("refined", value=True),
                    filters.EqualTo("dispatched", value=True),
                    only_unfinished_filter
            ]
        else:
            return []

    __list_columns__ = ["id", "customer_order_number", "goods_receipt.customer", "net_weight", "remaining_weight",
                        PlaceHolderColumnSpec(col_name="manufacturing_work_command_list", label=u"生产中重量",
                                              template_fname="order/todo-work-command-list-snippet.html",
                                              doc=u"若大于0,请敦促车间生产"),
                        PlaceHolderColumnSpec(col_name="qi_work_command_list", label=u"待质检重量",
                                              template_fname="order/qi-list-snippet.html"),
                        PlaceHolderColumnSpec(col_name="done_work_command_list", label=u"已完成重量",
                                              template_fname="order/done-work-command-list-snippet.html",
                                              doc=u"指订单下所有是最后一道工序的工单,这类工单的工序后质量之和"),
                        PlaceHolderColumnSpec(col_name="to_deliver_store_bill_list", label=u"待发货重量",
                                              template_fname="order/store-bill-list-snippet.html"),
                        "delivered_weight", "create_time", "dispatched_time", "goods_receipt",
                        ColumnSpec("urgent",
                                   formatter=lambda v, obj: u"<span class='text-danger'>是</span>" if v else u"否"),
                        ColumnSpec("refined",
                                   formatter=lambda v, obj: u"<span class='text-danger'>否</span>" if not v else u"是")]

    def repr_obj(self, obj):
        return unicode(obj) + "<br /><p class='text-center'><small class='muted'>" + unicode(
            obj.goods_receipt.customer) + "</small></p>"

    __sortable_columns__ = ["id", "customer_order_number", "goods_receipt.customer", "create_time", "goods_receipt"]

    __column_labels__ = {"customer_order_number": u"订单号", "goods_receipt.customer": u"客户", "create_time": u"创建时间",
                         "goods_receipt": u"收货单", "net_weight": u"收货重量", "remaining_weight": u"待调度重量",
                         "delivered_weight": u"已发货重量", "refined": u"完善", "urgent": u"加急", "product": u"产品",
                         "category": u"类型", "dispatched_time": u"下发时间"}

    __column_docs__ = {"remaining_weight": u"若大于0,请敦促调度员排产"}

    __column_formatters__ = {
        "urgent": lambda v, obj: u"是" if v else u"否",
        "customer_order_number": lambda v, obj: v.join(
            ["" if not obj.warning else '<i class=" fa fa-exclamation-triangle"></i>',
             u"<b>(退货)</b>" if any(so.returned for so in obj.sub_order_list) else ""]),
        "remaining_weight": lambda v, obj: unicode(v + obj.to_work_weight),
        "refined": lambda v, obj: u"是" if v else u"否",
        "create_time": lambda v, obj: v.strftime("%m-%d %H") + u"点",
        "dispatched_time": lambda v, obj: v.strftime("%m-%d %H") + u"点" if v and obj.dispatched else ""}

    def get_column_filters(self):
        from datetime import datetime, timedelta

        today = datetime.today()
        yesterday = today.date()
        week_ago = (today - timedelta(days=7)).date()
        _30days_ago = (today - timedelta(days=30)).date()
        ret = [filters.EqualTo("goods_receipt.customer", name=u"是"),
               filters.BiggerThan("create_time", name=u"在", options=[
                   (yesterday, u'一天内'), (week_ago, u'一周内'), (_30days_ago, u'30天内')]),
               category_filter]
        if not SchedulerPermission.can():
            ret.append(only_unfinished_filter)
        return ret

    def preprocess(self, model):
        from lite_mms.apis.order import OrderWrapper

        return OrderWrapper(model)

    def get_customized_actions(self, processed_objs=None):
        __customized_actions__ = []
        if CargoClerkPermission.can():
            from lite_mms.portal.order.actions import dispatch_action, mark_refined_action, account_action, \
                new_extra_order_action

            if processed_objs:
                if not processed_objs[0].refined:
                    __customized_actions__.append(mark_refined_action)
                    if not processed_objs[0].dispatched and not processed_objs[0].measured_by_weight:
                        __customized_actions__.append(new_extra_order_action)
                elif not processed_objs[0].dispatched:
                    __customized_actions__.append(dispatch_action)
                if processed_objs[0].can_account:
                    __customized_actions__.append(account_action)
            else:
                __customized_actions__ = [dispatch_action, mark_refined_action, account_action]
        return __customized_actions__

    def patch_row_attr(self, idx, row):
        if not row.refined:
            return {"class": "warning", "title": u"此订单没有完善，请先完善订单"}
        elif row.urgent and row.remaining_quantity:
            return {"class": "danger", "title": u"此订单请加急完成"}
        elif row.warning:
            return {"title": u"此订单的收货重量大于未分配重量，生产中重量，已发货重量，待发货重量之和"}

    def url_for_object(self, model, **kwargs):
        if model:
            return url_for("order.order", id_=model.id, **kwargs)
        else:
            return url_for("order.order", **kwargs)

    __default_order__ = ("id", "desc")

    def get_form_columns(self, obj=None):
        form_columns = OrderedDict()
        form_columns[u"订单详情"] = [
            "customer_order_number", ColumnSpec("goods_receipt.customer"),
            ColumnSpec("goods_receipt", css_class="control-text", label=u"收货单"), "net_weight",
            ColumnSpec("create_time"),
            ColumnSpec("dispatched_time", formatter=lambda v, obj: v if v and obj.dispatched else ""),
            PlaceHolderColumnSpec("log_list", label=u"日志", template_fname="logs-snippet.html")]

        form_columns[u"子订单列表"] = [
            PlaceHolderColumnSpec("sub_order_list", template_fname="order/sub-order-list-snippet.html", label="")]
        if SchedulerPermission.can():
            from lite_mms.portal.manufacture.views import work_command_view

            form_columns[u"工单列表"] = [TableColumnSpec("work_command_list", label="", col_specs=[
                LinkColumnSpec("id", label=u"编号", anchor=lambda v: v,
                               formatter=lambda v, obj: work_command_view.url_for_object(obj, url=request.url)),
                ColumnSpec("sub_order.id", label=u"子订单编号"), ColumnSpec("product", label=u"产品名称"),
                ColumnSpec("urgent", label=u"加急",
                           formatter=lambda v, obj: u"<span class='text-danger'>是</span>" if v else u"否"),
                ColumnSpec("sub_order.returned", label=u"退镀",
                           formatter=lambda v, obj: u"<span class='text-danger'>是</span>" if v else u"否"),
                ColumnSpec("org_weight", label=u"工序前重量"), ColumnSpec("org_cnt", label=u"工序前数量"),
                ColumnSpec("unit", label=u"单位"), ColumnSpec("processed_weight", label=u"工序后重量"),
                ColumnSpec("processed_cnt", label=u"工序后数量"), ColumnSpec("tech_req", label=u"技术要求"),
                ColumnSpec("department", label=u"车间"), ColumnSpec("team", label=u"班组"),
                ColumnSpec("qi", label=u"质检员"), ColumnSpec("status_name", label=u"状态")])]

        form_columns[u'订单流程图'] = [
            PlaceHolderColumnSpec('work_flow_json', template_fname='order/order-work-flow-snippet.html', label='')]
        return form_columns

    def try_edit(self, processed_objs=None):
        Permission.union(SchedulerPermission, CargoClerkPermission).test()
        if processed_objs and processed_objs[0].refined or processed_objs[0].dispatched:
            raise PermissionDenied

    def edit_hint_message(self, obj, read_only=False):
        if read_only:
            if SchedulerPermission.can():
                return u"正在排产订单%s" % obj.customer_order_number
            else:
                if obj.refined:
                    return u"订单%s已标记完善，不能修改" % obj.customer_order_number
                if obj.refined:
                    return u"订单%s已下发，不能修改" % obj.customer_order_number
                return ""
        else:
            return super(OrderModelView, self).edit_hint_message(obj, read_only)


class SubOrderModelView(ModelView):
    """

    """
    can_batchly_edit = False

    edit_template = "order/sub-order.html"

    def try_edit(self, processed_objs=None):
        Permission.union(SchedulerPermission, CargoClerkPermission).test()

        if processed_objs:
            if processed_objs[0].order.refined or processed_objs[0].order.dispatched:
                raise PermissionDenied

    @login_required
    def try_view(self, processed_objs=None):
        pass

    def edit_hint_message(self, obj, read_only=False):
        if read_only:
            if obj.order.refined:
                return u"子订单%s已标记完善，不能修改" % obj.id
            if obj.order.dispatched:
                return u"子订单%s已下发，不能修改" % obj.id
        else:
            return super(SubOrderModelView, self).edit_hint_message(obj, read_only)

    def get_form_columns(self, obj=None):

        form_columns = [ColumnSpec("id", label=u"编号"), ColumnSpec("create_time"), ColumnSpec("harbor"),
                        InputColumnSpec("product", group_by=Product.product_type),
                        InputColumnSpec("due_time", validators=[validators.Required(message=u"该字段不能为空")]), "weight"]
        if obj and obj.order_type == constants.EXTRA_ORDER_TYPE:
            form_columns.extend(["quantity", "unit", "spec", "type"])
        form_columns.extend(["tech_req", "urgent", "returned",
                             PlaceHolderColumnSpec("pic_url", label=u"图片", template_fname="pic-snippet.html",
                                                   form_width_class="col-lg-3"),
                             PlaceHolderColumnSpec("log_list", label=u"日志", template_fname="logs-snippet.html")])
        return form_columns

    __column_labels__ = {"product": u"产品", "weight": u"净重(公斤)", "harbor": u"卸货点", "urgent": u"加急", "returned": u"退镀",
                         "tech_req": u"技术要求", "create_time": u"创建时间", "due_time": u"交货日期", "quantity": u"数量",
                         "unit": u"数量单位", "type": u"型号", "spec": u"规格"}

    def preprocess(self, obj):
        from lite_mms.apis.order import SubOrderWrapper

        return SubOrderWrapper(obj)

    def on_model_change(self, form, model):
        if model.order_type == constants.STANDARD_ORDER_TYPE:
            model.quantity = model.weight
        model.remaining_quantity = model.quantity


from nav_bar import NavBar

order_model_view = OrderModelView(Order, u"订单")
sub_order_model_view = SubOrderModelView(SubOrder, u"子订单")
sub_nav_bar = NavBar()
sub_nav_bar.register(lambda: order_model_view.url_for_list(order_by="id", desc="1", category=""), u"所有订单",
                     enabler=lambda: category_filter.unfiltered(request.args.get("category", None)))
sub_nav_bar.register(
    lambda: order_model_view.url_for_list(order_by="id", desc="1", category=str(category_filter.UNDISPATCHED_ONLY)),
    u"仅展示待下发订单", enabler=lambda: request.args.get("category", "") == str(category_filter.UNDISPATCHED_ONLY))
sub_nav_bar.register(
    lambda: order_model_view.url_for_list(order_by="id", desc="1", category=category_filter.DELIVERABLE_ONLY),
    u"仅展示可发货订单", enabler=lambda: request.args.get("category", "") == str(category_filter.DELIVERABLE_ONLY))
sub_nav_bar.register(
    lambda: order_model_view.url_for_list(order_by="id", desc="1", category=category_filter.ACCOUNTABLE_ONLY),
    u"仅展示可盘点订单", enabler=lambda: request.args.get("category", "") == str(category_filter.ACCOUNTABLE_ONLY))


def hint_message(model_view):
    filter_ = [filter_ for filter_ in model_view.parse_filters() if filter_.col_name == "category"][0]
    if not filter_.has_value():
        return ""
    filter_.value = int(filter_.value)

    if filter_.value == category_filter.UNDISPATCHED_ONLY:
        return u"未下发订单未经收发员下发，调度员不能排产，请敦促收发员完善订单并下发"
    elif filter_.value == category_filter.DELIVERABLE_ONLY:
        return u"可发货订单中全部或部分产品可以发货，注意请催促质检员及时打印仓单"
    elif filter_.value == category_filter.ACCOUNTABLE_ONLY:
        return u"可盘点订单已经生产完毕（指已经全部分配给车间生产，最终生产完成，并通过质检），" \
               u"但是仍然有部分仓单没有发货。盘点后，这部分仓单会自动关闭"
    return ""


@order_page.route("/new-sub-order", methods=["GET", "POST"])
@decorators.templated("/order/new-extra-sub-order.html")
@decorators.nav_bar_set
def new_sub_order():
    """
    创建新的计件类型的子订单（只有计件类型的订单能够增加子订单）
    """
    if request.method == "GET":
        from lite_mms import apis

        order = apis.order.get_order(request.args.get("order_id", type=int))
        if not order:
            abort(404)
        if order.dispatched or order.refined:
            return redirect(url_for("error", error=u"已下发或已标记完善的订单不能新增子订单",
                                    url=url_for("order.order", id=order.id)))
        from lite_mms.constants import DEFAULT_PRODUCT_NAME

        return dict(titlename=u'新建子订单', order=order,
                    DEFAULT_PRODUCT_NAME=DEFAULT_PRODUCT_NAME,
                    product_types=apis.product.get_product_types(),
                    products=json.dumps(apis.product.get_products()),
                    harbor_list=apis.harbor.get_harbor_list(),
                    team_list=apis.manufacture.get_team_list())
    else:
        class NewSubOrderForm(Form):
            order_id = IntegerField('order_id', [validators.required()])
            product = IntegerField('product', [validators.required()])
            spec = TextField('spec', [validators.required()])
            type = TextField('type', [validators.required()])
            tech_req = TextField('tech_req')
            due_time = DateField('due_time',
                                 [validators.required()])
            urgent = BooleanField('urgent')
            returned = BooleanField('returned')
            unit = TextField('unit')
            quantity = IntegerField('quantity')
            weight = IntegerField('weight', [validators.required()])
            harbor = TextField('harbor', [validators.required()])

        form = NewSubOrderForm(request.form)
        order_id = form.order_id.data
        due_time = form.due_time.data
        if date.today() > due_time:
            return redirect(url_for("error", error=u"错误的交货日期", url=url_for("order.order", id_=order_id)))
        from lite_mms import apis

        try:
            sb = apis.order.SubOrderWrapper.new_sub_order(order_id=order_id, product_id=form.product.data,
                                                          spec=form.spec.data, type=form.type.data,
                                                          tech_req=form.tech_req.data, due_time=str(due_time),
                                                          urgent=form.urgent.data, weight=form.weight.data,
                                                          harbor_name=form.harbor.data, returned=form.returned.data,
                                                          unit=form.unit.data, quantity=form.quantity.data)
            flash(u"新建成功！")
        except ValueError, e:
            flash(unicode(e), "error")
        return redirect(url_for('order.order', id_=order_id))


@order_page.route('/work-command', methods=['GET', 'POST'])
@decorators.templated("order/work-command.html")
@decorators.nav_bar_set
def work_command():
    """
    生成一个新的工单
    """
    if request.method == "GET":
        from lite_mms import apis

        sub_order = apis.order.SubOrderWrapper.get_sub_order(
            request.args.get("sub_order_id", type=int))
        if not sub_order:
            abort(404)
        try:
            dep = apis.harbor.get_harbor_model(sub_order.harbor.name).department
            return dict(sub_order=sub_order, procedure_list=dep.procedure_list, department=dep, titlename=u"预排产")
        except AttributeError:
            abort(404)
    else:
        from lite_mms.apis import manufacture, order

        class PreScheduleForm(Form):
            sub_order_id = HiddenField('sub_order_id', [validators.required()])
            schedule_weight = IntegerField('schedule_weight',
                                           [validators.required()])
            procedure = IntegerField('procedure')
            tech_req = TextField('tech_req')
            schedule_count = IntegerField('schedule_count')
            urgent = BooleanField('urgent')
            url = HiddenField("url")

        form = PreScheduleForm(request.form)
        sub_order = order.get_sub_order(form.sub_order_id.data)
        if not sub_order:
            abort(404)
        if form.validate():
            try:
                inst = manufacture.new_work_command(
                    sub_order_id=sub_order.id,
                    org_weight=form.schedule_weight.data,
                    procedure_id=form.procedure.data,
                    org_cnt=form.schedule_count.data,
                    urgent=form.urgent.data,
                    tech_req=form.tech_req.data)
                if inst:
                    from lite_mms.apis.todo import remove_todo, DISPATCH_ORDER

                    remove_todo(DISPATCH_ORDER, sub_order.order.id)

                    from lite_mms.basemain import timeline_logger

                    timeline_logger.info(u"新建",
                                         extra={"obj": inst,
                                                "actor": current_user if current_user.is_authenticated else None,
                                                "action": u"新建", "obj_pk": inst.id})

                    if inst.sub_order.returned:
                        flash(u"成功创建工单（编号%d），请提醒质检员赶快处理" % inst.id)
                    else:
                        flash(u"成功创建工单（编号%d）" % inst.id)
            except ValueError as a:
                return render_template("error.html", msg=a.message,
                                       back_url=form.url.data or url_for('order.order', id_=sub_order.order.id)), 403
            return redirect(form.url.data or url_for('order.order', id_=sub_order.order.id))
        else:
            return render_template("error.html", msg=form.errors,
                                   back_url=url_for('order.order', id_=sub_order.order.id)), 403
