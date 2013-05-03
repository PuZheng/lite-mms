# -*- coding: UTF-8 -*-
from flask import Blueprint, redirect, url_for, flash, abort, render_template, request
from flask.ext.login import current_user
from wtforms import Form, HiddenField, IntegerField, validators, TextField, BooleanField
from lite_mms import constants
from lite_mms.utilities import decorators

manufacture_page = Blueprint("manufacture", __name__, static_folder="static",
                             template_folder="templates")

from lite_mms.portal.manufacture import views, ajax

from lite_mms.apis.manufacture import get_department_list

from lite_mms.basemain import data_browser, nav_bar


def _wrapper(department):
    return dict(id=department.id, name=department.name,
                procedure_list=[dict(id=p.id, name=p.name) for p in
                                department.procedure_list])


department_list = [_wrapper(d) for d in get_department_list()]


def _do_register(model_view):
    extra_params = {
        "list_view": {
            "nav_bar": nav_bar,
            "titlename": model_view.model_name + u"列表",
        },
        "form_view": {
            "nav_bar": nav_bar,
            "titlename": u"编辑" + model_view.model_name,
        }

    }
    data_browser.register_model_view(model_view, manufacture_page, extra_params)

_do_register(views.work_command_view)

@manufacture_page.route("/")
def index():
    return redirect(url_for("manufacture.work_command_list"))


@manufacture_page.route('/schedule', methods=['GET', 'POST'])
@decorators.nav_bar_set
def schedule():
    import lite_mms.apis as apis

    if request.method == 'GET':

        work_command_list = [apis.manufacture.get_work_command(id_) for id_ in request.args.getlist("work_command_id")]

        if 1 == len(work_command_list):
            work_command = work_command_list[0]
            return render_template("manufacture/schedule-work-command.html", titlename=u'排产',
                                   department_list=department_list, work_command=work_command)
        else:
            from lite_mms.utilities.functions import deduplicate

            department_set = deduplicate([wc.department for wc in work_command_list], lambda x: x.name)

            param_dic = {'titlename': u'批量排产', 'department_list': department_list,
                         'work_command_list': work_command_list,
                         'default_department_id': department_set[0].id if len(department_set) == 1 else None}

            return render_template("manufacture/batch-schedule.html",
                                   **param_dic)
    else: # POST
        class WorkCommandForm(Form):
            id = HiddenField('id', [validators.required()])
            url = HiddenField('url')
            procedure_id = IntegerField('procedure_id')
            department_id = IntegerField('department_id', [validators.required()])
            tech_req = TextField('tech_req')
            urgent = BooleanField('urgent')

        form = WorkCommandForm(request.form)
        if form.validate():
            department = apis.manufacture.get_department(
                form.department_id.data)
            if not department:
                abort(404)
            work_command_id_list = form.id.raw_data
            for work_command_id in work_command_id_list:
                work_command = apis.manufacture.get_work_command(work_command_id)

                if work_command:
                    d = dict(tech_req=form.tech_req.data,
                             urgent=form.urgent.data,
                             department_id=department.id,
                    )
                    if form.procedure_id.data:
                        d.update(procedure_id=form.procedure_id.data)

                    work_command.go(actor_id=current_user.id,
                                    action=constants.work_command.ACT_DISPATCH,
                                    **d)
                else:
                    abort(404)
            flash(u"工单(%s)已经被成功排产至车间(%s)" %
                  (",".join(work_command_id_list), department.name))
            return redirect(
                form.url.data or url_for("manufacture.work_command_list"))
        else:
            return render_template("result.html", error_content=form.errors)