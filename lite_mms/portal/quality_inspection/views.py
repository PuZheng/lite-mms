#-*- coding:utf-8 -*-
from flask.ext.databrowser import ModelView, column_spec, filters
from flask.ext.login import login_required
from flask.ext.principal import PermissionDenied
from lite_mms import models
from lite_mms.permissions.roles import QualityInspectorPermission
from lite_mms.apis.quality_inspection import get_QI_result_list, get_QI_result


class QIR(ModelView):
    @login_required
    def try_view(self, processed_objs=None):
        pass

    def try_create(self):
        raise PermissionDenied

    can_batchly_edit = False

    def try_edit(self, processed_objs=None):
        QualityInspectorPermission.test()
        raise PermissionDenied

    def edit_hint_message(self, obj, read_only=False):
        if read_only:
            if QualityInspectorPermission.can():
                return u"质检报告%s不能在浏览器上修改" % obj.id
            else:
                return u"您没有修改质检报告%s的权限" % obj.id
        else:
            return super(QIR, self).edit_hint_message(obj, read_only)

    __default_order__ = ("id", "desc")

    __list_columns__ = ["id", "work_command_id", "weight", "quantity",
                        column_spec.ColumnSpec("result", label=u"质检结果", formatter=lambda v, obj: get_QI_result(v)),
                        column_spec.ColumnSpec("actor", label=u"质检员"),
                        column_spec.ImageColumnSpec("pic_url", label=u"图片", css_class="img-responsive img-polaroid")]

    __column_labels__ = {"id": u"编号", "quantity": u"数量", "weight": u"重量", "work_command_id": u"工单号"}

    __form_columns__ = [column_spec.ColumnSpec("id"), "weight", "quantity",
                        column_spec.ColumnSpec('unit', label=u"单位"),
                        column_spec.SelectColumnSpec(col_name="result", label=u"质检结果", choices=get_QI_result_list()),
                        column_spec.ColumnSpec("work_command", label=u"工单编号"),
                        column_spec.ColumnSpec("report_time", label=u"创建时间"),
                        column_spec.ColumnSpec("actor", label=u"质检员"),
                        column_spec.PlaceHolderColumnSpec("pic_url", template_fname="pic-snippet.html", label=u"图片")]

    __column_filters__ = [filters.EqualTo("result", display_col_name=u"质检结果", options=get_QI_result_list())]

    def preprocess(self, obj):
        from lite_mms.apis.quality_inspection import QIReportWrapper

        return QIReportWrapper(obj)


qir_model_view = QIR(model=models.QIReport)