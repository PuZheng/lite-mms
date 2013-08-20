#-*- coding:utf-8 -*-
from . import Widget, DASHBOARD_WIDGETS
from sqlalchemy import func

from lite_mms import models, constants
from lite_mms.database import db


class ManufactureWidget(Widget):
    def query(self):
        return db.session.query(func.sum(models.WorkCommand.org_weight).label(u"生成中重量")).filter(
            models.WorkCommand.status != constants.work_command.STATUS_FINISHED)

    @property
    def data(self):
        return int(self.query().first()[0])


manufacture_widget = ManufactureWidget(name=u"生产中重量", description=u"生成中工单的总重量")


class ToDeliveryWidget(Widget):
    def query(self):
        return db.session.query(func.sum(models.StoreBill.weight).label(u"待发货重量")).filter(models.StoreBill.delivery_task_id == None)

    @property
    def data(self):
        return int(self.query().first()[0])


to_delivery_widget = ToDeliveryWidget(name=u"待发货重量", description=u"待发货的仓单的总重量")
DASHBOARD_WIDGETS.append(manufacture_widget)
DASHBOARD_WIDGETS.append(to_delivery_widget)