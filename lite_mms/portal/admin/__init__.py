# -*- coding: utf-8 -*-
from lite_mms.basemain import app, data_browser
from flask.ext.admin import Admin, AdminIndexView
from lite_mms.portal.admin.basic_settings import BasicSettings
from lite_mms.portal.admin.data_admin import DataAdminView
from lite_mms.portal.admin.department_settings import DepartmentModelView
from lite_mms.portal.admin.order_settings import OrderModelView,\
    SubOrderModelView
from lite_mms.database import db
from lite_mms.models import Department,  SubOrder, WorkCommand
from flask.ext.databrowser import ModelView as DataModelView


index_view = AdminIndexView(name=u"基本设置",
                            template="admin/basic_settings/index.html")

admin = Admin(app, index_view=index_view, name="lite-mms")

admin.add_view(DepartmentModelView(Department, db.session, name=u"车间管理",
                                   endpoint="department_settings"))
admin.add_view(
    SubOrderModelView(SubOrder, db.session, name=u"子订单管理", category=u"订单管理"))

data_admin = DataAdminView(name=u"数据管理", endpoint="data")


class WorkCommandView(DataModelView):
    __list_columns__ = ["id", "team", "department", "processed_weight",
                        "deduction_list"]
    __column_labels__ = {"id": u"编号", "team": u"班组", "department": u"车间",
                         "processed_weight": u"工序后重量", "deduction_list": u"扣重"}
    form_formatters = {"department": lambda x: x.name}
    __list_formatters__ = {"team": lambda model, v: v.name if v else "",
                           "department": lambda model, v: v.name if v else "",
                           "deduction_list": lambda model, v: sum(i.weight for i in v)}

data_browser.register_model_view(WorkCommandView(WorkCommand),
                                 data_admin.create_blueprint(admin))
admin.add_view(data_admin)
