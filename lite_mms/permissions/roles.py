# -*- coding: utf-8 -*-
"""
基于角色的用户权限
"""

from flask.ext.principal import Permission, RoleNeed 
from lite_mms.constants import groups

DepartmentLeaderPermission = Permission(RoleNeed(unicode(groups.DEPARTMENT_LEADER)))
QualityInspectorPermission = Permission(RoleNeed(unicode(groups.QUALITY_INSPECTOR)))
CargoClerkPermission = Permission(RoleNeed(unicode(groups.CARGO_CLERK)))
SchedulerPermission = Permission(RoleNeed(unicode(groups.SCHEDULER)))
AccountantPermission = Permission(RoleNeed(unicode(groups.ACCOUNTANT)))
AdminPermission = Permission(RoleNeed(unicode(groups.ADMINISTRATOR)))

