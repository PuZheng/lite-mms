# -*- coding: UTF-8 -*-
from collections import OrderedDict
from flask import url_for, request

from flask.ext.databrowser import ModelView, filters, column_spec
from flask.ext.login import login_required
from flask.ext.principal import PermissionDenied
from werkzeug.utils import cached_property
from lite_mms import constants

from lite_mms.models import WorkCommand, Order, SubOrder
from lite_mms.apis.manufacture import get_wc_status_list, get_status_list, get_handle_type_list
from lite_mms.permissions import SchedulerPermission


class WorkCommandView(ModelView):
    __list_columns__ = ["id", "sub_order.order.customer_order_number", "department", "team", "org_weight", "org_cnt",
                        "sub_order.unit", "urgent", "sub_order.returned", "tech_req", "handle_type", "status",
                        "procedure", "previous_procedure", "order.goods_receipt.customer"]

    __column_labels__ = {"id": u"编号", "department": u"车间", "team": u"班组", "sub_order.unit": u"单位",
                         "sub_order.returned": u"退镀", "urgent": u"加急", "org_weight": u"重量（公斤）", "org_cnt": u"数量",
                         "handle_type": u"处理类型", "tech_req": u"技术要求", "status": u"状态", "procedure": u"工序",
                         "previous_procedure": u"上道工序", "sub_order.order.customer_order_number": u"订单编号",
                         "sub_order": u"子订单编号", "order.goods_receipt.customer": u"客户"}

    __default_order__ = ("id", "desc")

    __sortable_columns__ = ["sub_order.order.customer_order_number", "urgent", "sub_order.returned"]

    def preprocess(self, obj):
        from lite_mms import apis
        return apis.manufacture.WorkCommandWrapper(obj)

    def patch_row_attr(self, idx, row):
        if row.status != constants.work_command.STATUS_FINISHED and (row.urgent or row.sub_order.returned):
            return {"class": "danger", "title": u"退镀或加急"}

    from datetime import datetime, timedelta
    today = datetime.today()
    yesterday = today.date()
    week_ago = (today - timedelta(days=7)).date()
    _30days_ago = (today - timedelta(days=30)).date()

    class In_Filter(filters.BaseFilter):
        __notation__ = "__in_ex"

        def __operator__(self, attr, value):
            return attr.in_(set(value))

    __column_filters__ = [
        In_Filter("status", u"是", options=[i[:2] for i in get_status_list()], display_col_name=u"状态"),
        filters.BiggerThan("create_time", name=u"在", display_col_name=u"创建时间",
                           options=[(yesterday, u'一天内'), (week_ago, u'一周内'), (_30days_ago, u'30天内')]),
        filters.Contains("sub_order.order.customer_order_number", name=u"包含", display_col_name=u"订单编号"),
        filters.EqualTo("sub_order.order.id", name="", hidden=True),
        filters.Only("urgent", display_col_name=u"只展示加急", test=lambda v: v == True, notation="__urgent"),
        filters.Only("sub_order.returned", display_col_name=u"只展示退镀", test=lambda v: v == True, notation="__returned"),
        filters.EqualTo("department", u"是")
    ]

    __column_formatters__ = {
        "status": lambda v, model: get_wc_status_list().get(v)[0],
        "department": lambda v, model: v if v else "",
        "team": lambda v, model: v if v else "",
        "sub_order.returned": lambda v, model: u"是" if v else u"否",
        "urgent": lambda v, model: u"是" if v else u"否",
        "procedure": lambda v, model: v if v else "",
        "previous_procedure": lambda v, model: v if v else "",
        "handle_type": lambda v, model: get_handle_type_list().get(v, u"未知")
    }
    
    def repr_obj(self, obj):
        return u"""
        <span>
        %(wc)s - <small>%(customer)s</small>
        <small class='pull-right muted'>
        %(datetime)s 
        </small>
        </span> 
        """ % {"wc": unicode(obj), "customer": obj.order.goods_receipt.customer, "datetime": obj.create_time.strftime("%m-%d %H:%M")}

    def try_create(self):
        raise PermissionDenied

    @login_required
    def try_view(self, processed_objs=None):
        pass

    def try_edit(self, processed_objs=None):
        SchedulerPermission.test()
        if processed_objs and processed_objs[
            0].status == constants.work_command.STATUS_DISPATCHING:
            return True
        else:
            raise PermissionDenied


    def edit_hint_message(self,obj, read_only=False):
        if read_only:
            if not SchedulerPermission.can():
                return u"无修改订单的权限"
            else:
                return u"工单%d已进入生产流程，不能修改" % obj.id
        else:
            return super(WorkCommandView, self).edit_hint_message(obj, read_only)

    def get_customized_actions(self, processed_objs=None):
        from .actions import schedule_action, retrieve_action

        def _get_status_filter(desc):
            for i in get_status_list():
                if i[1] == desc:
                    return i[0]
            else:
                return None

        if processed_objs:
            if all(schedule_action.test_enabled(obj) == 0 for obj in processed_objs):
                return [schedule_action]
            elif all(retrieve_action.test_enabled(obj) == 0 for obj in processed_objs):
                return [retrieve_action]
        else:
            if self.__column_filters__[0].value == unicode(_get_status_filter(u"待生产")):
                return [schedule_action]
            elif self.__column_filters__[0].value == unicode(_get_status_filter(u"生产中")):
                return [retrieve_action]
            elif self.__column_filters__[0].has_value:
                return [schedule_action, retrieve_action]
        return []

    def get_form_columns(self, obj=None):

        form_columns = OrderedDict()
        c = column_spec.ColumnSpec("", formatter=lambda v, obj: u"%s-%s" % (v.id, v.cause_name) if v else "")

        form_columns[u"工单信息"] = [column_spec.ColumnSpec("id"), column_spec.ColumnSpec("org_weight"),
                                 column_spec.ColumnSpec("org_cnt"), column_spec.ColumnSpec("sub_order.unit"),
                                 column_spec.ColumnSpec("sub_order.spec", label=u"规格"),
                                 column_spec.ColumnSpec("sub_order.type", label=u"型号"),
                                 "urgent", "sub_order.returned", "tech_req",
                                 column_spec.ColumnSpec("cause_name", label=u"产生原因"),
                                 column_spec.ColumnSpec("previous_work_command", label=u"上级工单",
                                                        formatter=lambda v, obj: u"%s-%s" % (
                                                            v.id, v.cause_name) if v else ""),
                                 column_spec.ListColumnSpec("next_work_command_list", label=u"下级工单",
                                                            item_col_spec=c),
                                 column_spec.PlaceHolderColumnSpec("log_list", label=u"日志",
                                                                   template_fname="logs-snippet.html")
        ]
        form_columns[u"加工信息"] = [column_spec.ColumnSpec("department"),
                                     column_spec.ColumnSpec("team"), "procedure",
                                     column_spec.ColumnSpec("previous_procedure"),
                                     column_spec.ColumnSpec("processed_weight", label=u"工序后重量"),
                                     column_spec.ColumnSpec("processed_cnt", label=u"工序后数量"),
                                     column_spec.ColumnSpec("status_name", label=u"状态"),
                                     column_spec.ColumnSpec("completed_time", label=u"生产结束时间"),
                                     column_spec.ColumnSpec("handle_type", label=u"处理类型",
                                                            formatter=lambda v, obj: get_handle_type_list().get(v, u"未知"))]
        if obj and obj.qir_list:
            from lite_mms.apis.quality_inspection import get_QI_result_list
            from lite_mms.portal.quality_inspection.views import qir_model_view
            def result(qir):
                for i in get_QI_result_list():
                    if qir.result == i[0]:
                        status =  i[1]
                        break
                else:
                    status = u"未知"
                return u"<a href='%s'>质检单%s%s了%s（公斤）</a>" % (
                qir_model_view.url_for_object(qir, url=request.url), qir.id, status, qir.weight)

            form_columns[u"质检信息"] = [column_spec.ListColumnSpec("qir_list", label=u"质检结果",
                                                                formatter=lambda v, obj: [result(qir) for qir in v])]

        form_columns[u"订单信息"] = [ column_spec.ColumnSpec("sub_order"),
                            column_spec.ColumnSpec("sub_order.order", label=u"订单号")]
        return form_columns

work_command_view = WorkCommandView(WorkCommand)
