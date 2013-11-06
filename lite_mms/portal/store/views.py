#-*- coding:utf-8 -*-
from flask import  redirect, url_for, json, abort, render_template
from werkzeug.utils import cached_property
from wtforms.validators import Required
from flask.ext.login import login_required
from flask.ext.databrowser import ModelView, filters
from flask.ext.databrowser.column_spec import ColumnSpec, InputColumnSpec, PlaceHolderColumnSpec
from flask.ext.principal import PermissionDenied

from lite_mms import models
from lite_mms.basemain import nav_bar
from lite_mms.apis.delivery import StoreBillWrapper
from lite_mms.permissions import QualityInspectorPermission
from lite_mms.portal.store import store_bill_page
from lite_mms.utilities import decorators

_printed = u"<i class='fa fa-ticket fa-fw' title='已打印'></i>"
_unprinted = u"<i class='fa fa-square-o fa-fw' title='未打印'></i>"


class StoreBillModelView(ModelView):
    __default_order__ = ("id", "desc")

    __list_columns__ = ["id", "customer", "product", "weight", "quantity", "sub_order.order.customer_order_number",
                        "qir", "qir.actor", "printed", "create_time", "qir.work_command", "harbor"]

    __column_labels__ = {"id": u"仓单号",
                         "customer": u"客户",
                         "product": u"产品",
                         "weight": u"重量(公斤)",
                         "quantity": u"数量",
                         "sub_order.order.customer_order_number": u"订单号",
                         "qir": u"质检报告",
                         "qir.actor": u"质检员",
                         "create_time": u"创建时间",
                         "qir.work_command": u"工单号",
                         "printed": u"打印",
                         "harbor": u"存放点",
                         "pic_url": u"图片"}

    __column_formatters__ = {"printed": lambda v, obj: _printed if v else _unprinted,
                             "harbor": lambda v, model: v if v else ""}

    def preprocess(self, obj):
        return StoreBillWrapper(obj)

    def try_create(self):
        raise PermissionDenied

    class Undeliveried(filters.Only):
        def set_sa_criterion(self, q):
            if self.value:
                return q.filter(models.StoreBill.delivery_session == None).filter(
                    models.StoreBill.delivery_task == None)
            else:
                return q

        @cached_property
        def attr(self):
            return self.col_name

    __column_filters__ = [filters.EqualTo("customer", u"是"),
                          filters.Only("printed", display_col_name=u"只展示未打印", test=lambda v: v == False,
                                       notation="__only_printed"),
                          Undeliveried("undeliveried", display_col_name=u"只展示未发货", test=None,
                                       notation="__undeliveried")]

    def try_edit(self, processed_objs=None):
        def _try_edit(obj):
            if obj and obj.delivery_session and obj.delivery_task:
                raise PermissionDenied

        QualityInspectorPermission.test()
        if isinstance(processed_objs, (list, tuple)):
            for obj in processed_objs:
                _try_edit(obj)
        else:
            _try_edit(processed_objs)

    def edit_hint_message(self, obj, read_only=False):
        if read_only:
            if QualityInspectorPermission.can():
                return u"仓单-%s已发货，不能编辑" % obj.id
            else:
                return u"您没有修改的权限"
        else:
            return super(StoreBillModelView, self).edit_hint_message(obj, read_only)

    def get_form_columns(self, obj=None):
        columns = [ColumnSpec("id"), "qir.work_command", "customer", "product",
                   InputColumnSpec("harbor", validators=[Required(u"不能为空")]), "weight"]
        if obj and not StoreBillWrapper(obj).sub_order.measured_by_weight:
            columns.extend(["quantity",
                           ColumnSpec("unit", label=u"单位"), ColumnSpec("sub_order.spec", label=u"型号"),
                           ColumnSpec("sub_order.type", label=u"规格"), ])
        columns.extend([ColumnSpec("create_time"),
                       ColumnSpec("printed", label=u"是否打印", formatter=lambda v, obj: u"是" if v else u"否"),
                       ColumnSpec("sub_order.id", label=u"子订单号"), "sub_order.order.customer_order_number",
                       PlaceHolderColumnSpec("pic_url", label=u"图片", template_fname="pic-snippet.html",
                                             form_width_class="col-lg-3"),
                       PlaceHolderColumnSpec("log_list", label=u"日志", template_fname="logs-snippet.html")])
        return columns

    def get_customized_actions(self, processed_objs=None):
        if QualityInspectorPermission.can():
            from .actions import PreviewPrintAction

            return [PreviewPrintAction(u"打印预览")]
        else:
            return []

    @login_required
    def try_view(self, processed_objs=None):
        pass


store_bill_view = StoreBillModelView(models.StoreBill, u"仓单")


@store_bill_page.route('/')
def index():
    return redirect(url_for("store_bill.store_bill_list"))


@store_bill_page.route("/store-bill-preview/<ids_>")
@decorators.nav_bar_set
def store_bill_preview(ids_):
    if not ids_:
        abort(404)
    import lite_mms.apis as apis

    store_bill_list = [apis.delivery.get_store_bill(id_) for id_ in json.loads(ids_)]
    return render_template("store/batch-print-preview.html", titlename=u"仓单预览", store_bill_list=store_bill_list,
                           nav_bar=nav_bar)