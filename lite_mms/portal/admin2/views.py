# -*- coding: UTF-8 -*-
import numbers

from flask.ext.databrowser import ModelView, column_spec
from flask.ext.databrowser.action import DeleteAction
from flask.ext.databrowser.filters import BaseFilter

from lite_mms.models import User, Group, Department, Team, Procedure, Harbor
import lite_mms.constants as constants
import lite_mms.constants.groups as groups_const
from lite_mms.permissions.roles import AdminPermission

class AdminModelView(ModelView):
    as_radio_group = True
    can_batchly_edit = False
    list_template = "admin2/list.html"
    create_template = edit_template = "admin2/object.html"

    def try_view(self):
        AdminPermission.test()

class UserModelView(AdminModelView):

    edit_template = create_template = "admin2/user.html"

    __list_columns__ = ["id", "username", column_spec.PlaceHolderColumnSpec("groups", label=u"用户组", 
                                                                            template_fname="admin2/user-groups-snippet.html")]
    __column_labels__ = {"id": u"编号", "username": u"用户名", "group": u"用户组", "password": u"密码(md5加密)", 
                         "groups": u"用户组列表"}

    class UserDeleteAction(DeleteAction):

        def test_enabled(self, obj):
            if obj.id == constants.ADMIN_USER_ID:
                return -2
            return 0

        def get_forbidden_msg_formats(self):
            return {
                -2: u"您不能删除超级管理员!"
            }

    __customized_actions__ = [UserDeleteAction(u"删除", AdminPermission)]


    def get_column_filters(self):
        class UserGroupFilter(BaseFilter):

            def set_sa_criterion(self, query):
                if isinstance(self.value, numbers.Number) or self.value.isdigit():
                    self.value = int(self.value)
                    query = query.filter(User.groups.any(Group.id==self.value))
                return query
        return [UserGroupFilter(u"group", name=u"是", options=[(group.id, group.name) for group in Group.query.all()])]

    # ============ FORM PART ===========================
    __create_columns__ = __form_columns__ = ["username", "password", "groups"]

user_model_view = UserModelView(User, u"用户")

class GroupModelView(AdminModelView):

    __list_columns__ = ["id", "name"] 
    __column_labels__ = {"id": u"编号", "name": u"组名", "permissions": u"权限列表"}

    class GroupDeleteAction(DeleteAction):

        def test_enabled(self, obj):
            if obj.id in {groups_const.DEPARTMENT_LEADER, 
                          groups_const.TEAM_LEADER, 
                          groups_const.LOADER, 
                          groups_const.QUALITY_INSPECTOR, 
                          groups_const.CARGO_CLERK, 
                          groups_const.SCHEDULER, 
                          groups_const.ACCOUNTANT, 
                          groups_const.ADMINISTRATOR}:
                return -2
            return 0
        
        def get_forbidden_msg_formats(self):
            return {
                -2: u"您不能删除系统内建用户组!"
            }
        
    __customized_actions__ = [GroupDeleteAction(u"删除", AdminPermission)]

    # ======================= FORM PART ==================================
    __form_columns__ = __create_columns__ =  ["name", "permissions"]

group_model_view = GroupModelView(Group, u"用户组")


class DepartmentModelView(AdminModelView):

    __list_columns__ = ["id", "name", 
                        column_spec.PlaceHolderColumnSpec("team_list", label=u"班组列表", template_fname="admin2/department-team-list-snippet.html"), 
                        column_spec.PlaceHolderColumnSpec("leader_list", label=u"车间主任", template_fname="admin2/department-leader-list-snippet.html"),
                        column_spec.PlaceHolderColumnSpec("procedure_list", label=u"允许工序", template_fname="admin2/department-procedure-list-snippet.html")]

    __create_columns__ = __form_columns__ = ["name", 
                                             column_spec.InputColumnSpec("leader_list", 
                                                                         filter_=lambda q: q.filter(User.groups.any(Group.id==groups_const.DEPARTMENT_LEADER)),
                                                                        doc=u'只有用户组是"车间主任", 才能作为车间主任'), 
                                             "procedure_list"]

    __column_labels__ = {"id": u"编号", "name": u"名称", "leader_list": u"车间主任列表", "procedure_list": u"车间允许工序列表"}

    __customized_actions__ = [DeleteAction(u"删除", AdminPermission)]

department_model_view = DepartmentModelView(Department, u"车间")


class TeamModelView(AdminModelView):

    __list_columns__ = ["id", "name", "department", "leader"]

    __create_columns__ = __form_columns__ = ["name", 
                                             column_spec.InputColumnSpec("leader", 
                                                                         label=u"班组长",
                                                                         filter_=lambda q: q.filter(User.groups.any(Group.id==groups_const.TEAM_LEADER)),
                                                                         doc=u'只有用户组是"班组长"，才能作为班组长'), "department"]
   
    __column_labels__ = {"id": u"编号", "name": u"名称", "leader": u"班组长", "department": u"所属车间"}

    __customized_actions__ = [DeleteAction(u"删除", AdminPermission)]

team_model_view = TeamModelView(Team, u"班组")


class HarborModelView(AdminModelView):
    __list_columns__ = ["name", "department"]
    __column_labels__ = {"name": u"名称", "department": u"默认车间"}
    __create_columns__ = __form_columns__ = ["name", "department"]
    
harbor_model_view = HarborModelView(Harbor, u"装卸点")


class ProcedureModelView(AdminModelView):
    __column_labels__ = {"name": u"名称", "department_list": u"可以执行此工序的车间"}
    __create_columns__ = __form_columns__ = ["name", "department_list"]

procedure_model_view = ProcedureModelView(Procedure, u"工序")
