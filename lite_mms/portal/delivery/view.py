#-*- coding:utf-8 -*-
from collections import OrderedDict
from flask import request, abort, redirect, url_for, render_template
from flask.ext.login import current_user
from flask.ext.principal import PermissionDenied
from sqlalchemy import exists
from flask.ext.databrowser import ModelView, filters
from flask.ext.databrowser.column_spec import ColumnSpec, ListColumnSpec, PlaceHolderColumnSpec, TableColumnSpec, \
    InputColumnSpec
from lite_mms import models, constants
from lite_mms.apis.delivery import ConsignmentWrapper, DeliverySessionWrapper
from lite_mms.portal.delivery import delivery_page

_with_person = u'<span class="icon-stack" title="有人"><i class="icon-sign-blank icon-stack-base"></i><i ' \
               u'class="icon-user icon-light"></i></span>'

_with_out_person = u'<span class="icon-stack" title="空"><i class="icon-check-empty icon-stack-base"></i></span>'


class DeliverySessionModelView(ModelView):
    can_batchly_edit = False
    column_hide_backrefs = False
    edit_template = "delivery/delivery-session.html"

    def get_list_columns(self):
        def gr_item_formatter(v, obj):
            # 格式化每个发货单，未打印或者过期，需要提示出来
            ret = unicode(v)
            v = ConsignmentWrapper(v)
            if not v.MSSQL_ID:
                ret += u'<small class="text-error"> (未导入)</small>'
            if v.stale:
                ret += u'<small class="text-error"> (过期)</small>'
            return ret

        return ["id", "plate_", "tare", "create_time", "finish_time", "with_person", "status",
                ListColumnSpec("customer_list_unwrapped", label=u"客 户", compressed=True),
                ListColumnSpec("consignment_list_unwrapped",
                               label=u"发货单",
                               compressed=True,
                               item_col_spec=ColumnSpec("", formatter=gr_item_formatter))
        ]

    __column_labels__ = {"id": u"编号", "plate_": u"车辆", "create_time": u"创建时间", "tare": u"净重（公斤）",
                         "with_person": u"驾驶室", "finish_time": u"结束时间", "status": u"状态"}

    __column_formatters__ = {"with_person": lambda v, obj: _with_person if v else _with_out_person,
                             "status": lambda v, obj: constants.delivery.desc_status(v),
                             "finish_time": lambda v, obj: v if v else ""
    }

    from datetime import datetime, timedelta

    today = datetime.today()
    yesterday = today.date()
    week_ago = (today - timedelta(days=7)).date()
    _30days_ago = (today - timedelta(days=30)).date()

    __column_filters__ = [filters.BiggerThan("create_time", name=u"在", default_value=str(yesterday),
                                             options=[(yesterday, u'一天内'), (week_ago, u'一周内'),
                                                      (_30days_ago, u'30天内')]),
                          filters.EqualTo("plate_", name=u"是"),
                          filters.Only("status", display_col_name=u"仅展示未完成会话", test=lambda col: ~col.in_(
                              [constants.delivery.STATUS_CLOSED, constants.delivery.STATUS_DISMISSED]),
                                       notation="__only_unclosed")]

    def get_form_columns(self, obj=None):
        __form_columns__ = OrderedDict()

        __form_columns__[u"发货会话详情"] = [ColumnSpec("id"), "plate_", "tare", "with_person", ColumnSpec("create_time")]

        __form_columns__[u"发货任务列表"] = [
            PlaceHolderColumnSpec("delivery_task_list", label="", template_fname="delivery/delivery-task-list-snippet.html")]

        __form_columns__[u"发货单列表"] = [
            PlaceHolderColumnSpec("consignment_list", label="", template_fname="delivery/consignment-list-snippet.html")]
        if obj and obj.status not in [constants.delivery.STATUS_CLOSED, constants.delivery.STATUS_DISMISSED]:
            __form_columns__[u"已选择仓单列表"] = [
                PlaceHolderColumnSpec("store_bill_list", label="", template_fname="delivery/store-bill-list-snippet.html")]
        return __form_columns__


    __default_order__ = ("create_time", "desc")

    def __list_filters__(self):
        return [filters.NotEqualTo("plate", name=u"", value="foo")]

    def preprocess(self, obj):
        return DeliverySessionWrapper(obj)

    def patch_row_attr(self, idx, obj):
        test = len(obj.customer_list) > len(obj.consignment_list)
        stale = False
        unimported = False
        for cn in obj.consignment_list:
            if not cn.MSSQL_ID:
                unimported = True
            if cn.stale:
                stale = True
        if test or stale:
            return {
                "title": u"有客户发货单没有生成，或者存在已经过期的发货单, 强烈建议您重新生成发货单!",
                "class": "alert alert-error"}
        elif unimported:
            return {
                "title": u"有客户发货单未导入",
                "class": "alert alert-warning"}

    def get_create_columns(self):


        def filter_plate(q):
            return q.filter(~exists().where(models.UnloadSession.plate == models.Plate.name).where(
                models.DeliverySession.plate == models.Plate.name))

        columns = OrderedDict()
        columns[u"基本信息"] = [InputColumnSpec("plate_", filter_=filter_plate),
                            InputColumnSpec("with_person", label=u"驾驶室是否有人"), "tare"]
        columns[u"已选择仓单列表"] = [
            PlaceHolderColumnSpec("store_bill_list", label="", template_fname="delivery/store-bill-list-snippet.html",
                                  as_input=True)]
        return columns

    def get_customized_actions(self, model_list=None):
        from lite_mms.portal.delivery.actions import CloseAction, OpenAction, CreateConsignmentAction, PrintConsignment

        action_list = []
        if model_list is None: # for list
            action_list.extend([CloseAction(u"关闭"), OpenAction(u"打开"), CreateConsignmentAction(u"生成发货单")])
        else:
            if len(model_list) ==1:
                if model_list[0].status in [constants.delivery.STATUS_CLOSED, constants.delivery.STATUS_DISMISSED]:
                    action_list.append(OpenAction(u"打开"))
                else:
                    action_list.append(CloseAction(u"关闭"))
                action_list.append(CreateConsignmentAction(u"生成发货单"))
                if model_list[0].consignment_list:
                    action_list.append(PrintConsignment(u"打印发货单"))
        return action_list

    def try_edit(self, processed_objs=None):
        def _try_edit(obj):
            if obj and obj.finish_time or obj.status in [constants.delivery.STATUS_CLOSED, constants.delivery.STATUS_DISMISSED]:
                raise PermissionDenied

        if isinstance(processed_objs, (list, tuple)):
            for obj_ in processed_objs:
                _try_edit(obj_)
        else:
            _try_edit(processed_objs)

    def edit_hint_message(self,obj, read_only=False):
        if read_only:
            return u"发货会话%s已关闭，不能修改" % obj.id
        else:
            return super(DeliverySessionModelView, self).edit_hint_message(obj, read_only)

@delivery_page.route("/weigh-delivery-task/<int:id_>", methods=["GET", "POST"])
def weigh_delivery_task(id_):
    from lite_mms.apis.delivery import get_delivery_task

    task = get_delivery_task(id_)
    if not task:
        abort(404)
    if request.method == "POST":
        current_weight = request.form.get('weight', type=int)
        weight = current_weight - task.last_weight
        result = task.update(weight=weight)
        if not result:
            abort(500)
        import fsm
        from lite_mms.apis import todo
        fsm.fsm.reset_obj(task.delivery_session)
        fsm.fsm.next(constants.delivery.ACT_WEIGHT, current_user)
        # delete todo
        todo.remove_todo(todo.WEIGH_DELIVERY_TASK, id_)
        return redirect(request.form.get("url") or url_for("delivery.delivery_session", id_=task.delivery_session_id))
    else:
        from lite_mms.basemain import nav_bar
        return render_template("delivery/delivery-task.html", titlename=u"发货任务称重", task=task, nav_bar=nav_bar)


class DeliveryTaskModelView(ModelView):
    pass

class ConsignmentModelView(ModelView):
    def try_create(self):
        raise PermissionDenied

    can_batchly_edit = False

    def get_customized_actions(self, processed_objs=None):
        from .actions import PayAction, PreviewConsignment

        ret = [PreviewConsignment(u"打印预览")]
        from lite_mms.permissions.roles import AccountantPermission

        if AccountantPermission.can() and isinstance(processed_objs, (list, tuple)):
            if any(obj.pay_in_cash and not obj.is_paid for obj in processed_objs):
                ret.append(PayAction(u"支付"))
        return ret

    def __list_filters__(self):
        from lite_mms.permissions.roles import AccountantPermission

        if AccountantPermission.can():
            return [filters.EqualTo("pay_in_cash", value=True)]
        return []

    def get_list_columns(self):
        return ["id", "consignment_id", "delivery_session", "actor", "create_time", "customer", "pay_in_cash",
                ColumnSpec("is_paid", formatter=lambda v, obj: u"是" if v else u"否"), ColumnSpec("notes", trunc=8)]


    __column_labels__ = {"consignment_id": u"发货单编号", "customer": u"客户", "delivery_session": u"车牌号",
                         "actor": u"发起人", "delivery_session.id": u"发货会话", "create_time": u"创建时间", "is_paid": u"是否支付",
                         "pay_in_cash": u"支付方式", "notes": u"备注"}

    __column_formatters__ = {"actor": lambda v, obj: u"--" if v is None else v,
                             "pay_in_cash": lambda v, obj: u"现金支付" if v else u"月结"}

    def get_column_filters(self):
        from lite_mms.permissions.roles import AccountantPermission

        not_paid_default = AccountantPermission.can()
        return [
            filters.EqualTo("customer", name=u"是"),
            filters.Only("is_paid", display_col_name=u"只展示未付款发货单", test=lambda col: col == False,
                         notation=u"is_paid", default_value=not_paid_default),
            filters.Only("MSSQL_ID", display_col_name=u"只展示未导出发货单", test=lambda col: col == None,
                         notation="is_export", default_value=False)
        ]

    def get_form_columns(self, obj=None):
        self.__form_columns__ = OrderedDict()
        self.__form_columns__[u"发货单详情"] = [
            ColumnSpec("consignment_id"),
            ColumnSpec("actor"),
            ColumnSpec("create_time"),
            ColumnSpec("customer"),
            ColumnSpec("delivery_session"),
            ColumnSpec("notes", trunc=24),
            ColumnSpec("is_paid", formatter=lambda v, obj: u"是" if v else u"否"),
        ]
        if obj and self.preprocess(obj).measured_by_weight:
            col_specs = ["id", ColumnSpec("product", label=u"产品",
                                          formatter=lambda v, obj: unicode(v.product_type) + "-" + unicode(v)),
                         ColumnSpec("weight", label=u"重量"),
                         ColumnSpec("returned_weight",
                                    label=u"退镀重量"),
                         ColumnSpec("team", label=u"生产班组")]

        else:
            col_specs = ["id", ColumnSpec("product", label=u"产品",
                                          formatter=lambda v, obj: unicode(v.product_type) + "-" + unicode(v)),
                         ColumnSpec("weight", label=u"重量"),
                         ColumnSpec("spec", label=u"型号"),
                         ColumnSpec("type", label=u"规格"),
                         ColumnSpec("quantity", label=u"数量"),
                         ColumnSpec("unit", label=u"单位"),
                         ColumnSpec("returned_weight",
                                    label=u"退镀重量"),
                         ColumnSpec("team", label=u"生产班组")]

        self.__form_columns__[u"产品列表"] = [
            TableColumnSpec("product_list_unwrapped", label="", col_specs=col_specs,
                            sum_fields=["weight", "returned_weight"])
        ]
        return self.__form_columns__


    def preprocess(self, obj):
        return ConsignmentWrapper(obj)


class ConsignmentProductModelView(ModelView):
    __column_labels__ = {"product": u"产品", "weight": u"净重", "returned_weight": u"退镀重量", "team": u"班组",
                         "quantity": u"数量", "unit": u"单位", "spec": u"型号", "type": u"规格"}

    def try_edit(self, processed_objs=None):
        from lite_mms import permissions

        permissions.CargoClerkPermission.test()
        if processed_objs[0].consignment.MSSQL_ID is not None:
            raise PermissionDenied

    def edit_hint_message(self, obj, read_only=False):
        from lite_mms import permissions

        if not permissions.CargoClerkPermission.can():
            return u"您不能修改本发货单，因为您不是收发员"
        if obj.consignment.MSSQL_ID is not None:
            return u"您不能修改本发货单，该发货单已经插入原有系统"
        return super(ConsignmentProductModelView, self).edit_hint_message(obj, read_only)

    def get_form_columns(self, obj=None):
    #if obj and apis.delivery.ConsignmentWrapper(obj.consignment).measured_by_weight:
    #return [InputColumnSpec("product", group_by=Product.product_type), "weight", "returned_weight", "team"]
    #else:
    #return [InputColumnSpec("product", group_by=Product.product_type), "weight", "quantity", "unit", "spec",
    #"type", "returned_weight", "team"]
        return ['unit']
        #return [InputColumnSpec("product", group_by=Product.product_type), "weight", "quantity", "unit", "spec",
        #"type", "returned_weight", "team"]


delivery_session_view = DeliverySessionModelView(models.DeliverySession, u"发货会话")
delivery_task_view = DeliveryTaskModelView(models.DeliveryTask, u"发货任务")
consigment_model_view = ConsignmentModelView(models.Consignment, u"发货单")
consigment_product_model_view = ConsignmentProductModelView(models.ConsignmentProduct, u"发货单项")
