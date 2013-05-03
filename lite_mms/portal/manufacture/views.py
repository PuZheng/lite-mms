# -*- coding: UTF-8 -*-
from flask.ext.databrowser import ModelView, filters, column_spec
from flask.ext.login import login_required
from flask.ext.principal import PermissionDenied
from werkzeug.utils import cached_property
from lite_mms import constants

from lite_mms.models import WorkCommand, Order, SubOrder
from lite_mms.apis.manufacture import get_wc_status_list, get_status_list, get_handle_type_list


class WorkCommandView(ModelView):
    __list_columns__ = ["id", "sub_order.order.customer_order_number", "department", "team", "org_weight", "org_cnt",
                        "sub_order.unit", "urgent", "sub_order.returned", "tech_req", "handle_type", "status",
                        "procedure", "previous_procedure"]

    __column_labels__ = {"id": u"编号", "department": u"车间", "team": u"班组", "sub_order.unit": u"单位",
                         "sub_order.returned": u"退镀", "urgent": u"加急", "org_weight": u"重量（公斤）", "org_cnt": u"数量",
                         "handle_type": u"处理类型", "tech_req": u"技术要求", "status": u"状态", "procedure": u"工序",
                         "previous_procedure": u"上道工序", "sub_order.order.customer_order_number": u"订单编号",
                         "sub_order": u"子订单编号"}

    __default_order__ = ("id", "desc")

    __sortable_columns__ = ["sub_order.order.customer_order_number", "urgent", "sub_order.returned"]

    def patch_row_attr(self, idx, row):
        if row.status != constants.work_command.STATUS_FINISHED and (row.urgent or row.sub_order.returned):
            return {"class":"warning", "title":u"退镀或加急"}

    from datetime import datetime, timedelta
    today = datetime.today()
    yesterday = today.date()
    week_ago = (today - timedelta(days=7)).date()
    _30days_ago = (today - timedelta(days=30)).date()

    class In_Filter(filters.BaseFilter):
        __notation__ = "__in_ex"

        def __operator__(self, attr, value):
            return attr.in_(set(value))

    class OrderIDFilter(filters.BaseFilter):
        def set_sa_criterion(self, q):
            q = q.filter(Order.id == self.value).join(SubOrder).join(Order)
            return q

        @cached_property
        def attr(self):
            return ""


    __column_filters__ = [
        In_Filter("status", u"是", options=[i[:2] for i in get_status_list()], display_col_name=u"状态"),
        filters.BiggerThan("create_time", name=u"在", display_col_name=u"创建时间",
                           options=[(yesterday, u'一天内'), (week_ago, u'一周内'), (_30days_ago, u'30天内')]),
        filters.Contains("sub_order.order.customer_order_number", name=u"包含", display_col_name=u"订单编号"),
        OrderIDFilter("order_id", hidden=True),
        filters.Only("urgent", display_col_name=u"只展示加急", test=lambda v: v == True, notation="__urgent"),
        filters.Only("sub_order.returned", display_col_name=u"只展示退镀", test=lambda v: v == True, notation="__returned")
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

    def try_create(self):
        raise PermissionDenied

    @login_required
    def try_view(self, processed_objs=None):
        pass

    def try_edit(self, processed_objs=None):
        raise PermissionDenied

    def get_customized_actions(self, processed_objs=None):
        from .actions import schedule_action, retrieve_action

        def _get_status_filter(desc):
            for i in get_status_list():
                if i[1] == desc:
                    return i[0]
            else:
                return None

        if self.__column_filters__[0].value == unicode(_get_status_filter(u"待生产")) or (
                processed_objs and all(schedule_action.test_enabled(obj) == 0 for obj in processed_objs)):
            return [schedule_action]
        elif self.__column_filters__[0].value == unicode(_get_status_filter(u"生产中")) or (
                processed_objs and all(retrieve_action.test_enabled(obj) == 0 for obj in processed_objs)):
            return [retrieve_action]
        else:
            return []

    __form_columns__ = ["id", "sub_order", "sub_order.order.customer_order_number", "department", "team", "org_weight",
                        "org_cnt", "sub_order.unit", "procedure", "previous_procedure",
                        column_spec.ColumnSpec("urgent", formatter=lambda v, obj: u"是" if v else u'否',label=u"加急"),
                        "sub_order.returned", "tech_req", "status",
                        column_spec.ColumnSpec("handle_type", label=u"处理类型", formatter=lambda v, obj: get_handle_type_list().get(v, u"未知"))]

work_command_view = WorkCommandView(WorkCommand)
# from flask import (request, abort, redirect, url_for, render_template, json,
#                    flash)
# from flask.ext.login import current_user
# from wtforms import Form, HiddenField, TextField, BooleanField, \
#     IntegerField, validators
# from lite_mms.portal.manufacture import manufacture_page
# import lite_mms.constants as constants
# from lite_mms.utilities import decorators, Pagination
# from lite_mms.permissions.work_command import view_work_command
#
#
# @manufacture_page.route("/")
# def index():
#     return redirect(url_for("manufacture.work_command_list"))
#
#
# @manufacture_page.route("/work-command-list", methods=["POST", "GET"])
# @decorators.templated("/manufacture/work-command-list.html")
# @decorators.nav_bar_set
# def work_command_list():
#     decorators.permission_required(view_work_command)
#     page = request.args.get('page', 1, type=int)
#     status = request.args.get('status', 1, type=int)
#     harbor = request.args.get('harbor', u"全部")
#     order_id = request.args.get('order_id', None)
#     status_list = []
#     schedule_button = False
#     retrieve_button = False
#     if status == constants.work_command.STATUS_DISPATCHING:
#         status_list.extend(
#             [constants.work_command.STATUS_REFUSED])
#         schedule_button = True
#     elif status == constants.work_command.STATUS_ENDING:
#         status_list.extend(
#             [constants.work_command.STATUS_LOCKED,
#              constants.work_command.STATUS_ASSIGNING])
#         retrieve_button = True
#     status_list.append(status)
#     import lite_mms.apis as apis
#
#     work_commands, total_cnt = apis.manufacture.get_work_command_list(
#         status_list=status_list, harbor=harbor, order_id=order_id,
#         start=(page - 1) * constants.UNLOAD_SESSION_PER_PAGE,
#         cnt=constants.UNLOAD_SESSION_PER_PAGE)
#     pagination = Pagination(page, constants.UNLOAD_SESSION_PER_PAGE, total_cnt)
#     param_dic = {'titlename': u'工单列表', 'pagination': pagination,
#                  'status': status, 'work_command_list': work_commands,
#                  'harbor': harbor, 'schedule': schedule_button,
#                  'retrieve': retrieve_button,
#                  'status_list': apis.manufacture.get_status_list(),
#                  'harbor_list': apis.harbor.get_harbor_list(),
#                  'all_status': dict(
#                      [(name, getattr(constants.work_command, name)) for name in
#                       constants.work_command.__dict__ if
#                       name.startswith("STATUS")]),
#     }
#     return param_dic
#
#
# @manufacture_page.route("/work-command/<id_>")
# @decorators.templated("/manufacture/work-command.html")
# @decorators.nav_bar_set
# def work_command(id_):
#     decorators.permission_required(view_work_command)
#     import lite_mms.apis as apis
#
#     wc = apis.manufacture.get_work_command(id_)
#     if not wc:
#         abort(404)
#     return {"work_command": wc,
#             "backref": request.args.get("backref")}
#
#
# @manufacture_page.route('/schedule', methods=['GET', 'POST'])
# @decorators.nav_bar_set
# def schedule():
#     import lite_mms.apis as apis
#
#     if request.method == 'GET':
#         decorators.permission_required(view_work_command)
#
#         def _wrapper(department):
#             return dict(id=department.id, name=department.name,
#                         procedure_list=[dict(id=p.id, name=p.name) for p in
#                                         department.procedure_list])
#
#         work_command_id_list = request.args.getlist("work_command_id")
#         department_list = apis.manufacture.get_department_list()
#         from lite_mms.basemain import nav_bar
#
#         if 1 == len(work_command_id_list):
#             work_command = apis.manufacture.get_work_command(
#                 work_command_id_list[0])
#             return render_template("manufacture/schedule-work-command.html",
#                                    **{'titlename': u'排产',
#                                       'department_list': [_wrapper(d) for d in
#                                                           department_list],
#                                       'work_command': work_command,
#                                       'nav_bar': nav_bar
#                                    })
#         else:
#             work_command_list = [apis.manufacture.get_work_command(id)
#                                  for id in work_command_id_list]
#             default_department_id = None
#
#
#             from lite_mms.utilities.functions import deduplicate
#
#             department_set = deduplicate(
#                 [wc.department for wc in work_command_list], lambda x: x.name)
#             if len(department_set) == 1: # 所有的工单都来自于同一个车间
#                 default_department_id = department_set.pop().id
#
#             param_dic = {'titlename': u'批量排产',
#                          'department_list': [_wrapper(d) for d in
#                                              department_list],
#                          'work_command_list': work_command_list,
#                          'default_department_id': default_department_id,
#                          'nav_bar': nav_bar
#             }
#             return render_template("/manufacture/batch-schedule.html",
#                                    **param_dic)
#     else: # POST
#         from lite_mms.permissions.work_command import schedule_work_command
#
#         decorators.permission_required(schedule_work_command, ("POST",))
#         form = WorkCommandForm(request.form)
#         if form.validate():
#             department = apis.manufacture.get_department(
#                 form.department_id.data)
#             if not department:
#                 abort(404)
#             work_command_id_list = form.id.raw_data
#             for work_command_id in work_command_id_list:
#                 work_command = apis.manufacture.get_work_command(
#                     int(work_command_id))
#
#                 if work_command:
#                     d = dict(tech_req=form.tech_req.data,
#                              urgent=form.urgent.data,
#                              department_id=department.id,
#                     )
#                     if form.procedure_id.data:
#                         d.update(procedure_id=form.procedure_id.data)
#
#                     work_command.go(actor_id=current_user.id,
#                                     action=constants.work_command.ACT_DISPATCH,
#                                     **d)
#                 else:
#                     abort(404)
#             flash(u"工单(%s)已经被成功排产至车间(%s)" %
#                   (",".join(work_command_id_list), department.name))
#             return redirect(
#                 form.url.data or url_for("manufacture.work_command_list"))
#         else:
#             return render_template("result.html", error_content=form.errors)
#
# @manufacture_page.route('/retrieve', methods=['POST'])
# def retrieve():
#     import lite_mms.apis as apis
#
#     work_command_id_list = request.form.getlist('work_command_id', type=int)
#     for id in work_command_id_list:
#         try:
#             apis.manufacture.WorkCommandWrapper.get_work_command(id).go(
#                 actor_id=current_user.id,
#                 action=constants.work_command.ACT_RETRIEVAL)
#         except ValueError as e:
#             return unicode(e), 403
#         except AttributeError:
#             abort(404)
#     flash(u"回收工单%s成功" % ",".join(str(id_) for id_ in work_command_id_list))
#     return redirect(
#         request.form.get('url', url_for('manufacture.work_command_list')))
#
#
# @manufacture_page.route('/qir-work-command-list')
# @decorators.templated('/manufacture/quality-inspection-work-command-list.html')
# @decorators.nav_bar_set
# def QI_work_command_list():
#     page = request.args.get('page', 1, type=int)
#     department_id = request.args.get('department', type=int)
#     from lite_mms import apis
#
#     work_command_list, total_cnt = apis.manufacture.get_work_command_list(
#         status_list=[constants.work_command.STATUS_FINISHED],
#         department_id=department_id, normal=True)
#     pagination = Pagination(page, constants.UNLOAD_SESSION_PER_PAGE, total_cnt)
#     return {'titlename': u'工单列表', 'work_command_list': work_command_list,
#             'pagination': pagination, 'department': department_id,
#             'department_list': apis.manufacture.get_department_list()
#     }
#
#
# @manufacture_page.route('/qir-list')
# @decorators.templated('/manufacture/quality-inspection-report-list.html')
# @decorators.nav_bar_set
# def QI_report_list():
#     work_command_id = request.args.get("id", type=int)
#     if work_command_id:
#         from lite_mms import apis
#
#         work_command = apis.manufacture.get_work_command(work_command_id)
#         qir_list, total_cnt = apis.quality_inspection.get_qir_list(
#             work_command_id)
#         return {'titlename': u'质检单', 'qir_list': qir_list,
#                 'work_command': work_command,
#                 'qir_result_list': apis.quality_inspection.get_QI_result_list()}
#     else:
#         abort(403)
#
#
# class WorkCommandForm(Form):
#     id = HiddenField('id', [validators.required()])
#     url = HiddenField('url')
#     procedure_id = IntegerField('procedure_id')
#     department_id = IntegerField('department_id', [validators.required()])
#     tech_req = TextField('tech_req')
#     urgent = BooleanField('urgent')
#
