# -*- coding: utf-8 -*-
"""
基于角色的用户权限
"""

from flask.ext.principal import Permission, RoleNeed 
from lite_mms.constants import groups

DepartmentLeaderPermission = Permission(RoleNeed(unicode(groups.DEPARTMENT_LEADER)))
DepartmentLeaderPermission.brief = u"车间主任角色"
QualityInspectorPermission = Permission(RoleNeed(unicode(groups.QUALITY_INSPECTOR)))
QualityInspectorPermission.brief = u"质检员角色"
CargoClerkPermission = Permission(RoleNeed(unicode(groups.CARGO_CLERK)))
CargoClerkPermission.brief = u"收发员角色"
SchedulerPermission = Permission(RoleNeed(unicode(groups.SCHEDULER)))
SchedulerPermission.brief = u"调度员角色"
AccountantPermission = Permission(RoleNeed(unicode(groups.ACCOUNTANT)))
AccountantPermission.brief = u"财会人员角色"
AdminPermission = Permission(RoleNeed(unicode(groups.ADMINISTRATOR)))
AdminPermission.brief = u"管理员角色"

