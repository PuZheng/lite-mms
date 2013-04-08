# -*- coding: utf-8 -*-
import sys
from datetime import datetime

from werkzeug.datastructures import MultiDict
from flask import url_for
from flask.ext.babel import _
from sqlalchemy.orm.exc import NoResultFound
from wtforms import (Form, IntegerField, ValidationError, TextField,
                     BooleanField, validators)
from werkzeug.utils import cached_property

import lite_mms.constants as constants
from lite_mms import models
from lite_mms.apis import ModelWrapper
from lite_mms.exceptions import InvalidAction, InvalidStatus
from lite_mms.utilities import action_name, status_name, do_commit
from lite_mms.utilities.state_machine import StateMachine, State


class WorkCommandWrapper(ModelWrapper):
    @property
    def qi(self):
        if self.qir_list:
            return self.qir_list[0].actor
        else:
            return None
    
    @property
    def finish_time(self):
        if self.status == constants.work_command.STATUS_FINISHED:
            return self.last_mod
        return None

    @cached_property
    def status_name(self):
        return get_wc_status_list().get(self.status)[0]

    @cached_property
    def status_describe(self):
        return get_wc_status_list().get(self.status)[1]

    @property
    def product(self):
        return self.sub_order.product

    @cached_property
    def handle_type_name(self):
        return get_handle_type_list().get(self.handle_type)

    @property
    def pic_url(self):
        if self.pic_path:
            return url_for("serv_pic", filename=self.pic_path)
        else:
            return ""

    @cached_property
    def harbor(self):
        return self.sub_order.harbor

    @property
    def order(self):
        return self.sub_order.order

    @property
    def unit(self):
        return self.sub_order.unit

    @property
    def default_department(self):
        for d in get_department_list():
            if self.harbor in d.harbor_list:
                return d
        return None

    @classmethod
    def new_work_command(cls, sub_order_id, org_weight, org_cnt, procedure_id,
                         urgent, tech_req="", pic_path=""):
        """

        :param cls:
        :param sub_order_id:
        :param org_weight:
        :param org_cnt:
        :param procedure_id:
        :param urgent:
        :param tech_req:
        :param pic_path:
        :return: 新生成的WorkCommandWrapper
        :raise: ValueError 如果参数错误
        """

        from lite_mms.apis import order

        try:
            sub_order = order.get_sub_order(sub_order_id).model
        except AttributeError:
            raise ValueError(_(u"没有该子订单%d" % sub_order_id))

        if not org_cnt:
            if sub_order.order_type == constants.EXTRA_ORDER_TYPE:
                raise ValueError(_(u"需要schedule_count字段"))
            else:
                org_cnt = org_weight

        if procedure_id:
            try:
                procedure = models.Procedure.query.filter(
                    models.Procedure.id == procedure_id).one()
            except NoResultFound:
                raise ValueError(_(u"没有该工序"))
        else:
            procedure = None

        if sub_order.remaining_quantity < org_cnt:
            raise ValueError(_(u"子订单的未排产数量小于%d" % org_cnt))
        org_weight = int(sub_order.unit_weight * org_cnt)

        work_command = models.WorkCommand(sub_order=sub_order,
                                          org_weight=org_weight,
                                          procedure=procedure,
                                          tech_req=tech_req,
                                          urgent=urgent, org_cnt=org_cnt,
                                          pic_path=pic_path or sub_order
                                          .pic_path)
        if sub_order.returned:
            work_command.processed_cnt = work_command.org_cnt
            work_command.processed_weight = work_command.org_weight
            work_command.status = constants.work_command\
            .STATUS_QUALITY_INSPECTING
        sub_order.remaining_quantity -= org_cnt

        do_commit([sub_order, work_command])

        return WorkCommandWrapper(work_command)

    @classmethod
    def get_list(cls, status_list, harbor=None, department_id=None,
                 normal=None, team_id=None, start=0, cnt=sys.maxint,
                 keywords=None, order_id=None, date=None):
        """get the work command list from database, sorted by last mod time
        descentally
        :param status_list: the status of to retrieve, should be a list of integers
        """
        import types

        wc_q = models.WorkCommand.query

        if isinstance(status_list, types.ListType):
            wc_q = wc_q.filter(models.WorkCommand.status.in_(status_list))
        if department_id:
            wc_q = wc_q.filter(
                models.WorkCommand.department_id == department_id)
        if team_id:
            wc_q = wc_q.filter(models.WorkCommand.team_id == team_id)
        if harbor and harbor != u"全部":
            wc_q = wc_q.join(models.SubOrder).filter(
                models.SubOrder.harbor_name == harbor)
        if normal:
            wc_q = wc_q.filter(models.WorkCommand.org_weight > 0)
        if keywords:
            wc_q = wc_q.filter(
                models.WorkCommand.id.like("%" + keywords + "%"))
        if order_id:
            wc_q = wc_q.filter(models.WorkCommand.sub_order_id.in_(
                [sub_order.id for sub_order in models.SubOrder.query.filter(
                    models.SubOrder.order_id == order_id)]))
        if date:
            wc_q = wc_q.filter(models.WorkCommand.last_mod > date)
        total_cnt = wc_q.count()
        wc_q = wc_q.order_by(models.WorkCommand.urgent.desc()).order_by(
            models.WorkCommand.create_time.asc()).offset(start).limit(cnt)
        return [WorkCommandWrapper(wc) for wc in wc_q.all()], total_cnt

    @classmethod
    def get_work_command(cls, id_):
        """
        get work command from database
        :return: WorkCommandWrapper or None
        """
        if not id_:
            return None
        try:
            return WorkCommandWrapper(
                models.WorkCommand.query.filter(
                    models.WorkCommand.id == id_).one())
        except NoResultFound:
            return None


    def update(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self.model, k):
                setattr(self.model, k, v)
        do_commit(self.model)

    def go(self, actor_id, **kwargs):
        class _ValidationForm(Form):
            def add_value(self, **kwargs):
                try:
                    self.__values.update(kwargs)
                except AttributeError:
                    self.__values = {}
                    self.__values.update(kwargs)

            @property
            def values(self):
                try:
                    ret = self.__values
                except AttributeError:
                    ret = {}
                ret.update(self.data)
                # remove none values
                for k, v in ret.items():
                    if v is None:
                        ret.pop(k)
                return ret

            def validate_team_id(self, field): # pylint: disable=R0201
                if self.action.data == constants.work_command.ACT_ASSIGN:
                    if not field:
                        raise ValidationError("team_id required when "
                                              "assigning work command")
                    try:
                        self.add_value(
                            team=TeamWrapper.get_team(field.data).model)
                    except AttributeError:
                        raise ValidationError(
                            "no such team " + str(field.data))

            def validate_department_id(self, field):
                if self.action.data == constants.work_command.ACT_DISPATCH:
                    if not field:
                        raise ValidationError("department_id required when "
                                              "dispatching work command")
                    try:
                        self.add_value(
                            department=DepartmentWrapper.get_department(
                                field.data).model)
                    except AttributeError:
                        raise ValidationError(
                            "no such department " + str(field.data))

            valid_actions = [constants.work_command.ACT_DISPATCH,
                             constants.work_command.ACT_ASSIGN,
                             constants.work_command.ACT_ADD_WEIGHT,
                             constants.work_command.ACT_END,
                             constants.work_command.ACT_CARRY_FORWARD,
                             constants.work_command.ACT_RETRIEVAL,
                             constants.work_command.ACT_REFUSE,
                             constants.work_command.ACT_AFFIRM_RETRIEVAL,
                             constants.work_command.ACT_QI,
                             constants.work_command.ACT_REFUSE_RETRIEVAL,
                             constants.work_command.ACT_RETRIVE_QI,
                             constants.work_command.ACT_QUICK_CARRY_FORWARD]
            action = IntegerField("action", [validators.AnyOf(valid_actions)])
            team_id = IntegerField("team id")
            department_id = IntegerField("department id")
            quantity = IntegerField("quantity")
            weight = IntegerField("weight")
            tech_req = TextField("tech_req")
            urgent = BooleanField("urgent")
            deduction = IntegerField("deduction")
            procedure_id = IntegerField("procedure_id")


        work_command_sm = WorkCommandSM(self.model)

        form = _ValidationForm(MultiDict(kwargs))
        if not form.validate():
            raise ValueError(form.errors)
        try:
            work_command_sm.next(actor=models.User.query.get(actor_id),
                                 **form.values)
        except InvalidAction, e:
            raise ValueError(e.description)
        self.model.last_mod = datetime.now()
        do_commit(self.model)


    @property
    def retrievable(self):
        return self.status in [constants.work_command.STATUS_ASSIGNING,
                               constants.work_command.STATUS_ENDING]

    @property
    def deduction(self):
        return sum(deduction.weight for deduction in self.deduction_list)


class DepartmentWrapper(ModelWrapper):
    @classmethod
    def get_list(cls):
        return [DepartmentWrapper(d) for d in models.Department.query.all()]

    @classmethod
    def get_department(cls, id_):
        if not id_:
            return None
        try:
            return DepartmentWrapper(
                models.Department.query.filter(
                    models.Department.id == id_).one())
        except NoResultFound:
            return None


class TeamWrapper(ModelWrapper):
    @classmethod
    def get_list(cls, department_id=None):
        """
        get teams from database
        :rtype: ListType
        """
        query_ = models.Team.query
        if department_id:
            query_ = query_.filter(models.Team.department_id == department_id)
        return [TeamWrapper(team) for team in query_.all()]


    @classmethod
    def get_team(cls, id_):
        """
        get team from database according to id_
        :return TeamWrapper or None
        """
        if not id_:
            return None
        try:
            return TeamWrapper(models.Team.query.filter(
                models.Team.id == id_).one())
        except NoResultFound:
            return None

    def get_team_work_command_dict(self, begin_date=None, end_date=None):
        #只计算生产完毕的
        wc_dict = {}
        for wc in get_work_command_list(
            status_list=[constants.work_command.STATUS_FINISHED],
            team_id=self.id)[0]:
            list_ = wc_dict.setdefault(wc.create_time.strftime("%Y-%m-%d"), [])
            flag = True
            if begin_date:
                flag = flag and (wc.create_time.date() >= begin_date.date())
            if end_date:
                flag = flag and (wc.create_time.date() <= end_date.date())
            if flag and wc.org_weight > 0:
                list_.append(wc)
        return wc_dict


class WorkCommandState(State):
    status = "DEFAULT"

    def __init__(self, work_command):
        self.work_command = work_command


    def next(self, action):
        raise InvalidAction(_(u"%(status)s状态不允许进行%(action)s操作" %
                              {"action": action_name(action),
                               "status": status_name(self.status)}))

class StateDispatching(WorkCommandState):
    """
    the initial state
    """
    status = constants.work_command.STATUS_DISPATCHING

    def next(self, action):
        if action == constants.work_command.ACT_DISPATCH:
            return StateAssigning(self.work_command)
        else:
            raise InvalidAction(_(u"%(status)s状态不允许进行%(action)s操作" %
                                {"action": action_name(action),
                                 "status": status_name(self.status)}))

    def run(self, **kwargs):
        self.work_command.set_status(constants.work_command.STATUS_DISPATCHING)
        if self.last_status == constants.work_command.STATUS_LOCKED:
            # 根据车间主任之前填写的工序后重量/数量，将原有工单的重量修正后
            # 返回
            old_wc = self.work_command
            old_wc.org_weight -= kwargs["weight"]
            if old_wc.org_weight <= 0:
                # 至少保证为1， 这同时也意味着原有工单的重量不准确，所以不能
                # 进行回收
                old_wc.org_weight = 1
            processed_weight = kwargs["weight"]

            if old_wc.sub_order.order_type == constants.EXTRA_ORDER_TYPE:
                old_wc.org_cnt -= kwargs["quantity"]
                processed_quantity = kwargs["quantity"]
            else:
                old_wc.org_cnt = old_wc.org_weight
                processed_quantity = processed_weight
            if old_wc.org_cnt <= 0:
                # 至少保证为1， 这同时也意味着原有工单的数量不准确，所以不能
                # 进行回收
                old_wc.org_cnt = 1

            if processed_weight and processed_quantity:
                new_wc = models.WorkCommand(sub_order=old_wc.sub_order,
                                            org_weight=processed_weight,
                                            procedure=old_wc.procedure,
                                            urgent=old_wc.urgent,
                                            status=constants.work_command.STATUS_QUALITY_INSPECTING,
                                            department=old_wc.department,
                                            processed_weight=processed_weight,
                                            team=old_wc.team,
                                            previous_procedure=old_wc.previous_procedure,
                                            tag=old_wc.tag,
                                            tech_req=old_wc.tech_req,
                                            org_cnt=processed_quantity,
                                            processed_cnt=processed_quantity,
                                            pic_path=old_wc.pic_path,
                                            handle_type=old_wc.handle_type)

                do_commit(new_wc)

        self.work_command.department = None
        self.work_command.team = None

class StateRefused(WorkCommandState):
    """
    in fact, it is just an alias of STATUS_DISPATCHING
    """

    status = constants.work_command.STATUS_REFUSED

    def next(self, action):
        if action == constants.work_command.ACT_DISPATCH:
            return StateAssigning(self.work_command)
        else:
            raise InvalidAction(_(u"%(status)s状态不允许进行%(action)s操作" %
                                {"action": action_name(action),
                                 "status": status_name(self.status)}))

    def run(self, **kwargs):
        self.work_command.set_status(constants.work_command.STATUS_REFUSED)


class StateAssigning(WorkCommandState):
    status = constants.work_command.STATUS_ASSIGNING

    def next(self, action):
        if action == constants.work_command.ACT_ASSIGN:
            return StateEnding(self.work_command)
        elif action == constants.work_command.ACT_REFUSE:
            return StateRefused(self.work_command)
        elif action == constants.work_command.ACT_RETRIEVAL:
            return StateDispatching(self.work_command)
        else:
            raise InvalidAction(_(u"%(status)s状态不允许进行%(action)s操作" %
                                {"action": action_name(action),
                                 "status": status_name(self.status)}))

    def run(self, **kwargs):
        self.work_command.set_status(constants.work_command.STATUS_ASSIGNING)
        if kwargs.get("department"):
            self.work_command.department = kwargs["department"]
        self.work_command.tech_req = kwargs["tech_req"]
        if kwargs.get("procedure_id"):
            self.work_command.procedure_id = kwargs.get("procedure_id")
        self.work_command.team = None
        if not self.work_command.department:
            raise InvalidStatus(_(u"%(status)s状态必须有department字段") % {
            "status": status_name(self.status)})


class StateEnding(WorkCommandState):
    status = constants.work_command.STATUS_ENDING

    def next(self, action):
        if action == constants.work_command.ACT_ADD_WEIGHT:
            return self
        elif action == constants.work_command.ACT_RETRIEVAL:
            return StateLocked(self.work_command)
        elif action == constants.work_command.ACT_END:
            return StateQualityInspecting(self.work_command)
        elif action == constants.work_command.ACT_CARRY_FORWARD:
            if self.work_command.processed_cnt == 0: # carry forward COMPLETELY
                return StateAssigning(self.work_command)
            else:
                return StateQualityInspecting(self.work_command)
        elif action == constants.work_command.ACT_QUICK_CARRY_FORWARD:
            return StateEnding(self.work_command)
        else:
            raise InvalidAction(_(u"%(status)s状态不允许进行%(action)s操作" %
                                {"action": action_name(action),
                                 "status": status_name(self.status)}))

    def run(self, **kwargs):
        if self.action == constants.work_command.ACT_QUICK_CARRY_FORWARD:
            old_wc = self.work_command

            new_wc = models.WorkCommand(sub_order=old_wc.sub_order,
                                        org_weight=old_wc.processed_weight,
                                        procedure=old_wc.procedure,
                                        status=constants.work_command
                                        .STATUS_QUALITY_INSPECTING,
                                        team=old_wc.team,
                                        department=old_wc.department,
                                        previous_procedure=old_wc
                                        .previous_procedure,
                                        tag=old_wc.tag,
                                        tech_req=old_wc.tech_req,
                                        org_cnt=old_wc.processed_cnt,
                                        pic_path=old_wc.pic_path,
                                        handle_type=old_wc.handle_type,
                                        processed_weight=old_wc.processed_weight,
                                        processed_cnt=old_wc.processed_cnt)

            remain_quantity = old_wc.org_cnt - old_wc.processed_cnt
            if remain_quantity <= 0:
                remain_quantity = 1
            remain_weight = int(
                self.work_command.unit_weight * remain_quantity)

            old_wc.org_cnt = remain_quantity
            old_wc.org_weight = remain_weight
            old_wc.processed_cnt = 0
            old_wc.processed_weight = 0
            do_commit([old_wc, new_wc])

        else:
            self.work_command.set_status(constants.work_command.STATUS_ENDING)
            if kwargs.has_key("team"): # when it comes by ACT_ASSIGN
                self.work_command.team = kwargs["team"]

            if self.last_status == constants.work_command.STATUS_ENDING:
                try:
                    self.work_command.processed_weight += kwargs["weight"]
                except KeyError:
                    raise InvalidAction(_(u"该操作需要weight字段"))
                if self.work_command.sub_order.order_type == constants\
                .EXTRA_ORDER_TYPE: # 计件类型
                    try:
                        self.work_command.processed_cnt += kwargs["quantity"]
                    except KeyError:
                        raise InvalidAction(_(u"该操作需要quantity字段"))
                else: # 普通类型
                    self.work_command.processed_cnt = self.work_command\
                    .processed_weight

class StateQualityInspecting(WorkCommandState):
    status = constants.work_command.STATUS_QUALITY_INSPECTING

    def next(self, action):
        if action == constants.work_command.ACT_QI:
            return StateFinished(self.work_command)
        else:
            raise InvalidAction(_(u"%(status)s状态不允许进行%(action)s操作" %
                                {"action": action_name(action),
                                 "status": status_name(self.status)}))

    def run(self, **kwargs):
        self.work_command.set_status(
            constants.work_command.STATUS_QUALITY_INSPECTING)
        if self.last_status == constants.work_command\
        .STATUS_ENDING:
            if self.action == constants.work_command.ACT_CARRY_FORWARD:
                old_wc = self.work_command
                remain_quantity = old_wc.org_cnt - old_wc.processed_cnt
                if remain_quantity <= 0:
                    remain_quantity = 1
                remain_weight = int(
                    self.work_command.unit_weight * remain_quantity)
                new_wc = models.WorkCommand(sub_order=old_wc.sub_order,
                                            org_weight=remain_weight,
                                            procedure=old_wc.procedure,
                                            status=constants.work_command
                                            .STATUS_ASSIGNING,
                                            previous_procedure=old_wc
                                            .previous_procedure,
                                            tag=old_wc.tag,
                                            tech_req=old_wc.tech_req,
                                            org_cnt=remain_quantity,
                                            pic_path=old_wc.pic_path,
                                            handle_type=old_wc.handle_type,
                                            department=old_wc.department)

                old_wc.org_cnt -= new_wc.org_cnt #:实际工作的黑件数
                old_wc.org_weight -= new_wc.org_weight

                do_commit([new_wc, old_wc])

            self.work_command.completed_time = datetime.now()
            do_commit(self.work_command) 
        elif self.last_status == constants.work_command.STATUS_FINISHED:
            old_wc = self.work_command
            from lite_mms.apis.quality_inspection import QIReportWrapper

            qir_list = [QIReportWrapper(qir) for qir in old_wc.qir_list]
            if not qir_list:
                raise InvalidAction(u'该工单没有质检报告，不能取消质检结果')
                # 若某个质检报告生成的仓单已经完全发货或者部分发货, 不能取消质检报告
            if any(qir.partly_delivered for qir in qir_list):
                raise InvalidAction(u'新生成的仓单已经发货，不能取消质检报告')
            generate_wc_list = [
            qi_report.generated_work_command for qi_report
            in qir_list if qi_report.generated_work_command]
            if any(wc.status not in [constants.work_command.STATUS_DISPATCHING,
                                     constants.work_command.STATUS_ASSIGNING,
                                     constants.work_command.STATUS_REFUSED]
                for wc in generate_wc_list):
                raise InvalidAction(u'新生成的工单已经分配，不能取消质检报告')

            # 删除工单的质检报告中，完全没有发货的仓单
            models.StoreBill.query.filter(models.StoreBill.qir_id.in_(
                [qir.id for qir in qir_list])).delete("fetch")
            # 删除工单的质检报告生成的工单
            wc_id_list = [qir.generated_work_command_id for qir in qir_list]
            models.QIReport.query.filter(
                models.QIReport.work_command_id == old_wc.id).update(
                {"generated_work_command_id": None})
            models.WorkCommand.query.filter(
                models.WorkCommand.id.in_(wc_id_list)).delete(
                "fetch")
            old_wc.deduction_list = []


class StateFinished(WorkCommandState):
    status = constants.work_command.STATUS_FINISHED

    def next(self, action):
        if action == constants.work_command.ACT_RETRIVE_QI:
            return StateQualityInspecting(self.work_command)
        else:
            raise InvalidAction(_(u"%(status)s状态不允许进行%(action)s操作" %
                                {"action": action_name(action),
                                 "status": status_name(self.status)}))

    def run(self, **kwargs):
        self.work_command.set_status(constants.work_command.STATUS_FINISHED)
        if self.last_status == constants.work_command\
        .STATUS_QUALITY_INSPECTING:
            old_wc = self.work_command
            procedure = ""
            previous_procedure = ""
            handle_type = ""
            status = ""
            department = None

            for qir in old_wc.qir_list:
                qir.report_time = datetime.now()
                do_commit(qir)
                if qir.result == constants.quality_inspection.FINISHED:
                    sb = models.StoreBill(qir)
                    if self.work_command.team:
                        sb.printed = True
                        sb.harbor = self.work_command.team.department.harbor_list[0]
                    do_commit(sb)
                    continue
                elif qir.result == constants.quality_inspection.DISCARD:
                    # use QIReport as discard report
                    continue
                elif qir.result == constants.quality_inspection.NEXT_PROCEDURE:
                    handle_type = constants.work_command.HT_NORMAL
                    procedure = None
                    previous_procedure = old_wc.procedure
                    status = constants.work_command.STATUS_DISPATCHING
                    department = None
                elif qir.result == constants.quality_inspection.REPAIR:
                    handle_type = constants.work_command.HT_REPAIRE
                    procedure = old_wc.procedure
                    previous_procedure = old_wc.previous_procedure #可能有三道工序
                    status = constants.work_command.STATUS_ASSIGNING if old_wc.department else constants.work_command.STATUS_DISPATCHING
                    # 这个工单可能是由退货产生的。
                    department = old_wc.department
                elif qir.result == constants.quality_inspection.REPLATE:
                    handle_type = constants.work_command.HT_REPLATE
                    procedure = old_wc.procedure
                    previous_procedure = old_wc.previous_procedure
                    status = constants.work_command.STATUS_ASSIGNING if old_wc.department else constants.work_command.STATUS_DISPATCHING
                    department = old_wc.department
                new_wc = models.WorkCommand(sub_order=old_wc.sub_order,
                                            org_weight=qir.weight,
                                            status=status,
                                            tech_req=old_wc.tech_req,
                                            org_cnt=qir.quantity,
                                            procedure=procedure,
                                            previous_procedure=previous_procedure,
                                            pic_path=qir.pic_path,
                                            handle_type=handle_type,
                                            department=department)

                do_commit(new_wc)
                qir.generated_work_command_id = new_wc.id
                do_commit(qir)
            if kwargs.get("deduction"):
                do_commit(models.Deduction(weight=kwargs["deduction"],
                                           work_command=old_wc,
                                           actor=kwargs["actor"],
                                           team=old_wc.team))


class StateLocked(WorkCommandState):
    status = constants.work_command.STATUS_LOCKED

    def next(self, action):
        if action == constants.work_command.ACT_AFFIRM_RETRIEVAL:
            return StateDispatching(self.work_command)
        elif action == constants.work_command.ACT_REFUSE_RETRIEVAL:
            # TODO should inform scheduler
            return StateEnding(self.work_command)
        else:
            raise InvalidAction(_(u"%(status)s状态不允许进行%(action)s操作" %
                                {"action": action_name(action),
                                 "status": status_name(self.status)}))

    def run(self, **kwargs):
        self.work_command.set_status(constants.work_command.STATUS_LOCKED)


class WorkCommandSM(StateMachine):
    def __init__(self, work_command):
        if work_command.status == constants.work_command.STATUS_DISPATCHING:
            init_state = StateDispatching(work_command)
        elif work_command.status == constants.work_command.STATUS_ASSIGNING:
            init_state = StateAssigning(work_command)
        elif work_command.status == constants.work_command.STATUS_ENDING:
            init_state = StateEnding(work_command)
        elif work_command.status == constants.work_command.STATUS_LOCKED:
            init_state = StateLocked(work_command)
        elif work_command.status == constants.work_command.STATUS_QUALITY_INSPECTING:
            init_state = StateQualityInspecting(work_command)
        elif work_command.status == constants.work_command.STATUS_REFUSED:
            init_state = StateRefused(work_command)
        elif work_command.status == constants.work_command.STATUS_FINISHED:
            init_state = StateFinished(work_command)
        else:
            raise InvalidStatus(_(u"工单%(wc_id)d的状态%(status)d是非法的" %
                                  {"status": work_command.status,
                                   "wc_id": work_command.id}))
        super(WorkCommandSM, self).__init__(init_state)


def get_status_list():
    return [
        (constants.work_command.STATUS_DISPATCHING, u'待生产', u"需要调度员排产的工单"),
        (constants.work_command.STATUS_ENDING, u'生产中', u"进入生产环节的工单"),
        (constants.work_command.STATUS_QUALITY_INSPECTING, u'待质检',
         u"待质检员质检完成的工单"),
        (constants.work_command.STATUS_FINISHED, u'已完成', u"已经结束生产的工单"),
    ]


def get_wc_status_list():
    return {
        constants.work_command.STATUS_DISPATCHING: (u'待排产', u'待调度员排产'),
        constants.work_command.STATUS_ASSIGNING: ( u'待分配', u'待车间主任分配'),
        constants.work_command.STATUS_LOCKED: (u'锁定', u'调度员已请求回收，待车间主任处理'),
        constants.work_command.STATUS_ENDING: (u'待请求结转或结束', u'待班组长结转或结束'),
        constants.work_command.STATUS_QUALITY_INSPECTING: (
            u'待质检', u'待质检员质检完成'),
        constants.work_command.STATUS_REFUSED: (u'车间主任打回', u'调度员分配后，被车间主任打回'),
        constants.work_command.STATUS_FINISHED: (u'已结束', u'已经结束生产'),
    }


def get_handle_type_list():
    return {
        constants.work_command.HT_NORMAL: u'正常加工',
        constants.work_command.HT_REPAIRE: u'返修',
        constants.work_command.HT_REPLATE: u'返镀'
    }

get_work_command_list = WorkCommandWrapper.get_list
get_work_command = WorkCommandWrapper.get_work_command
new_work_command = WorkCommandWrapper.new_work_command
get_team_list = TeamWrapper.get_list
get_team = TeamWrapper.get_team
get_department_list = DepartmentWrapper.get_list
get_department = DepartmentWrapper.get_department
