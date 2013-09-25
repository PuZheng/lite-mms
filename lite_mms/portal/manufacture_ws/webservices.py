# -*- coding: UTF-8 
import time
from datetime import datetime, date, timedelta
import json
import os
import types
from flask import request
from flask.login import current_user

from wtforms import (Form, IntegerField, StringField, validators, 
    ValidationError)
from lite_mms.utilities import _
from lite_mms.basemain import app
from lite_mms.constants.quality_inspection import * # pylint: disable=W0401,
# W0614
from lite_mms.constants.work_command import * # pylint: disable=W0401,W0614
from lite_mms.portal.manufacture_ws import manufacture_ws
from lite_mms.utilities.decorators import (webservice_call, login_required_webservice, 
                                           permission_required_webservice)
from lite_mms.utilities import to_timestamp
from lite_mms.permissions.roles import (TeamLeaderPermission, DepartmentLeaderPermission, QualityInspectorPermission)


def _work_command_to_dict(wc):
    return dict(id=wc.id,
                customerName=wc.order.customer.name,
                department=dict(id=wc.department.id,
                                name=wc.department.name) if wc.department
                else "",
                isUrgent=1 if wc.urgent else 0,
                spec=wc.sub_order.spec,
                type=wc.sub_order.type,
                lastMod=to_timestamp(wc.last_mod),
                orderID=wc.sub_order.order_id,
                orderNum=wc.sub_order.order.customer_order_number,
                orderCreateTime=time.mktime(wc.sub_order.order.create_time.timetuple()),
                orderType=wc.sub_order.order_type,
                orgCount=wc.org_cnt,
                orgWeight=wc.org_weight,
                picPath=wc.pic_url,
                previousProcedure=wc.previous_procedure.name if wc
                .previous_procedure else "",
                procedure=wc.procedure.name if wc.procedure else "",
                processedCount=wc.processed_cnt,
                processedWeight=wc.processed_weight or 0,
                productName=wc.sub_order.product.name,
                status=wc.status,
                subOrderId=wc.sub_order_id,
                team=dict(id=wc.team.id, name=wc.team.name) if wc.team else "",
                technicalRequirements=wc.tech_req,
                handleType=wc.handle_type,
                deduction=wc.deduction,
                unit=wc.unit,
                rejected=int(wc.sub_order.returned))


@manufacture_ws.route("/work-command-list", methods=["GET"])
@webservice_call("json")
@login_required_webservice
def work_command_list():
    # pylint: disable=R0903
    class _ValidationForm(Form):
        def validate_status(self, field): # pylint: disable=R0201
            status_list = field.data.split(",")
            valid_status = [STATUS_DISPATCHING, STATUS_ASSIGNING,
                            STATUS_ENDING, STATUS_LOCKED, STATUS_REFUSED,
                            STATUS_QUALITY_INSPECTING, STATUS_FINISHED]
            if not all(status.isdigit() and int(status) in valid_status for
                       status in status_list):
                raise ValidationError("status must be one of " +
                                      ", ".join(str(i) for i in valid_status))

        department_id = IntegerField(u"department id")
        team_id = IntegerField(u"team id")
        start = IntegerField(u"start")
        cnt = IntegerField(u"count")
        status = StringField(u"status", [validators.DataRequired()])


        # pylint: enable=R0903


    form = _ValidationForm(request.args)
    if form.validate():
        status_list = [int(status) for status in form.status.data.split(',')]
        param_dict = dict(status_list=status_list)

        if len(status_list) == 1 and status_list[0] == STATUS_FINISHED:
            param_dict["date"] = datetime.now().date() - timedelta(days=1)
        if form.department_id.data is not None:
            param_dict.update(department_id=form.department_id.data)
        if form.team_id.data is not None:
            param_dict.update(team_id=form.team_id.data)
        if form.start.data is not None:
            param_dict.update(start=form.start.data)
        if form.cnt.data is not None:
            param_dict.update(cnt=form.cnt.data)
        import lite_mms.apis as apis

        wc_list, total_cnt = apis.manufacture.get_work_command_list(
            **param_dict)
        return json.dumps(
            dict(data=[_work_command_to_dict(wc) for wc in wc_list],
                 totalCnt=total_cnt))
    else:
        # we disable E1101, since it's a bug of pylint
        return str(form.errors), 412 # pylint: disable=E1101        


@manufacture_ws.route("/team-list", methods=["GET"])
@webservice_call("json")
@login_required_webservice
def team_list():
    department_id = request.args.get("department_id", type=int)
    if department_id:
        import lite_mms.apis as apis

        teams = apis.manufacture.get_team_list(department_id)
        return json.dumps([dict(name=t.name, id=t.id) for t in teams])
    return "invalid department_id", 404


@manufacture_ws.route("/work-command", methods=["PUT"])
@webservice_call("json")
def work_command():
    action = request.args.get('action', type=int)
    if action in {ACT_ASSIGN, ACT_REFUSE, ACT_AFFIRM_RETRIEVAL, ACT_REFUSE_RETRIEVAL}:
        permission = DepartmentLeaderPermission
    elif action in {ACT_ADD_WEIGHT, ACT_END, ACT_CARRY_FORWARD, ACT_QUICK_CARRY_FORWARD}:
        permission = TeamLeaderPermission
    else:
        permission = QualityInspectorPermission

    return permission_required_webservice(permission)(_work_command)

def _work_command():
    import lite_mms.apis as apis

    class _ValidationForm(Form):
        def validate_team_id(self, field):
            if self.action.data == ACT_ASSIGN:
                if field.data is None:
                    raise ValidationError("team required when assigning \
work command")

        def validate_weight(self, field):
            if self.action.data == ACT_ADD_WEIGHT or self.action.data == \
                    ACT_AFFIRM_RETRIEVAL:
                if field.data is None:
                    raise ValidationError(_("需要weight字段"))

        def validate_is_finished(self, field):
            if field.data is not None:
                if field.data not in [0, 1]:
                    raise ValidationError("is finished should be 0 or 1")

        work_command_id = StringField(u"work command id",
                                      [validators.DataRequired()])
        quantity = IntegerField(u"quantity")
        weight = IntegerField(u"weight")
        remain_weight = IntegerField(u"remain_weight")
        team_id = IntegerField(u"team id")
        action = IntegerField(u"action", [validators.DataRequired(), validators.AnyOf([ACT_AFFIRM_RETRIEVAL, ACT_ADD_WEIGHT, ACT_END, ACT_CARRY_FORWARD, ACT_REFUSE, ACT_REFUSE_RETRIEVAL, ACT_AFFIRM_RETRIEVAL, ACT_QI, ACT_REFUSE_RETRIEVAL, ACT_RETRIVE_QI, ACT_QUICK_CARRY_FORWARD])])
        is_finished = IntegerField(u"is finished")
        deduction = IntegerField(u"deduction")


    form = _ValidationForm(request.args)

    if form.validate():
        # pylint: disable=R0912
        if form.action.data == ACT_ASSIGN:
            try:
                work_command_id = int(form.work_command_id.data)
            except ValueError:
                return "work command id should be integer", 403
            try:
                wc = apis.manufacture.get_work_command(work_command_id)
                if not wc:
                    return u"无此工单%s" % work_command_id, 404
                wc.go(actor_id=current_user.id, action=form.action.data,
                      team_id=form.team_id.data)
            except ValueError, e:
                return unicode(e), 403
            result = wc
        elif form.action.data == ACT_AFFIRM_RETRIEVAL:
            kwargs = {"weight": form.weight.data}
            if form.quantity.data:
                kwargs.update(quantity=form.quantity.data)
            try:
                work_command_id = int(form.work_command_id.data)
            except ValueError:
                return "work command id should be integer", 403
            try:
                wc = apis.manufacture.get_work_command(work_command_id)
                if not wc:
                    return u"无此工单%s" % work_command_id, 404

                wc.go(actor_id=current_user.id, action=form.action.data,
                      **kwargs)
            except ValueError, e:
                return unicode(e), 403
            result = wc
        elif form.action.data == ACT_ADD_WEIGHT:
            kwargs = {"weight": form.weight.data}
            if form.quantity.data:
                kwargs.update(quantity=form.quantity.data)
            try:
                work_command_id = int(form.work_command_id.data)
            except ValueError:
                return "work command id should be integer", 403
            try:
                wc = apis.manufacture.get_work_command(work_command_id)
                if not wc:
                    return u"无此工单%s" % work_command_id, 404

                wc.go(actor_id=current_user.id, action=form.action.data,
                      **kwargs)
                if form.is_finished.data:
                    wc.go(actor_id=current_user.id, action=ACT_END)
            except ValueError, e:
                return unicode(e), 403
            result = wc
        elif form.action.data == ACT_QI:
            try:
                work_command_id = int(form.work_command_id.data)
            except ValueError:
                return "work command id should be integer", 403
            try:
                wc = apis.manufacture.get_work_command(work_command_id)
                if not wc:
                    return u"无此工单%s" % work_command_id, 404

                wc.go(actor_id=current_user.id, action=form.action.data,
                      deduction=form.deduction.data or 0)
            except ValueError, e:
                return unicode(e), 403
            result = wc
        elif form.action.data in [ACT_CARRY_FORWARD, ACT_END,
                                  ACT_REFUSE_RETRIEVAL,
                                  ACT_REFUSE]:
            try:
                wc_id_list = [int(wc_id) for wc_id in
                              form.work_command_id.data.split(",")]
            except ValueError:
                return "work command id should be integer", 403
            result = []
            # TODO may be it could be done batchly
            for work_command_id in wc_id_list:
                wc = apis.manufacture.get_work_command(work_command_id)
                if not wc:
                    return u"无此工单%s" % work_command_id, 404

                try:
                    wc.go(actor_id=current_user.id, action=form.action.data)
                except ValueError, e:
                    return unicode(e), 403
                result.append(wc)
            if len(result) == 1:
                result = result[0]
                # pylint: enable=R0912
        elif form.action.data == ACT_RETRIVE_QI:

            try:
                work_command_id = int(form.work_command_id.data)
            except ValueError:
                return "work command id should be integer", 403
            try:
                wc = apis.manufacture.get_work_command(work_command_id)
                if not wc:
                    return u"无此工单%s" % work_command_id, 404

                if wc.last_mod.date() < date.today():
                    return u'不能取消今天以前的质检单', 403

                wc.go(actor_id=current_user.id, action=form.action.data)
            except ValueError, e:
                return unicode(e), 403
            result = wc
        elif form.action.data == ACT_QUICK_CARRY_FORWARD:
            try:
                work_command_id = int(form.work_command_id.data)
            except ValueError:
                return "work command id should be integer", 403
            try:
                wc = apis.manufacture.get_work_command(work_command_id)
                if not wc:
                    return u"无此工单%s" % work_command_id, 404

                if wc.processed_weight <= 0:
                    return u'未加工过的工单不能快速结转', 403

                wc.go(actor_id=current_user.id, action=form.action.data)
            except ValueError, e:
                return unicode(e), 403
            result = wc

        if isinstance(result, types.ListType):
            return json.dumps([_work_command_to_dict(wc) for wc in result])
        else:
            return json.dumps(_work_command_to_dict(result))
    else:
        # we disable E1101, since it's a bug of pylint
        return str(form.errors), 403 # pylint: disable=E1101        

def _handle_delete():
    from lite_mms.apis import quality_inspection

    id_ = request.args.get("id", type=int)
    if not id_:
        return "id and required", 403
    try:
        return quality_inspection.remove_qi_report(id_=id_,
                                                   actor_id=current_user.id)
    except ValueError, e:
        return unicode(e), 403

@manufacture_ws.route("/delete-quality-inspection-report",
                      methods=["POST"])
@webservice_call("json")
def delete_quality_inspection_report():
    """
    this method is equivalent to "DELETE quality-inspection-report"
    I do this for WAP
    """
    return _handle_delete()


def _qir2dict(qir):
    return dict(id=qir.id, actor_id=qir.actor_id, quantity=qir.quantity,
                weight=qir.weight, result=qir.result,
                work_command_id=qir.work_command_id, pic_url=qir.pic_url)


@manufacture_ws.route("/quality-inspection-report",
                      methods=["POST", "PUT", "DELETE"])
@webservice_call("json")
@permission_required_webservice(QualityInspectorPermission)
def quality_inspection_report():
    from lite_mms.apis import quality_inspection

    if request.method == "POST":
        class _ValidationForm(Form):
            work_command_id = IntegerField(u"work_command_id",
                                           [validators.DataRequired()])
            quantity = IntegerField(u"quantity", [validators.DataRequired()])
            result = IntegerField(u"result", [validators.AnyOf([FINISHED,
                                                                NEXT_PROCEDURE,
                                                                REPAIR,
                                                                REPLATE,
                                                                DISCARD])])


        form = _ValidationForm(request.args)
        if form.validate():
            try:
                try:
                    f = request.files.values()[0]
                except IndexError:
                    f = None
                pic_path = ""
                if f:
                    pic_path = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.jpg")
                    f.save(os.path.join(app.config["UPLOAD_FOLDER"], pic_path))
                qir = quality_inspection.new_QI_report(
                    actor_id=current_user.id,
                    work_command_id=form.work_command_id.data,
                    quantity=form.quantity.data,
                    result=form.result.data, pic_path=pic_path)
                return json.dumps(_qir2dict(qir))
            except ValueError, e:
                return unicode(e), 403
        else:
            # we disable E1101, since it's a bug of pylint
            return str(form.errors), 403 # pylint: disable=E1101        
    elif request.method == "DELETE":
        return _handle_delete()
    else: # PUT
        try:
            try:
                f = request.files.values()[0]
            except IndexError:
                f = None
            pic_path = ""
            if f:
                pic_path = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.jpg")
                f.save(os.path.join(app.config["UPLOAD_FOLDER"], pic_path))
            quantity = request.args.get("quantity", type=int)
            result = request.args.get("result", type=int)
            if not quantity and not result and not pic_path:
                return "you must update some value!", 403
            from lite_mms.apis import quality_inspection

            qir = quality_inspection.update_qi_report(
                request.args.get("id", type=int),
                actor_id=current_user.id,
                quantity=quantity, result=result, pic_path=pic_path)
            return json.dumps(_qir2dict(qir))
        except ValueError, e:
            return unicode(e), 403


@manufacture_ws.route("/quality-inspection-report-list",
                      methods=['GET'])
@login_required_webservice
def quality_inspection_report_list():
    work_command_id = request.args.get("work_command_id", type=int)

    if work_command_id:
        import lite_mms.apis.quality_inspection as QI

        try:
            qirs, total_cnt = QI.get_qir_list(work_command_id)
            return json.dumps([_qir2dict(qir) for qir in qirs])
        except ValueError, e:
            return unicode(e), 403
    else:
        return "work command id required", 403

