#-*- coding:utf-8 -*-
from flask.ext.databrowser import filters


class UnfinishedFilter(filters.BaseFilter):

    def set_sa_criterion(self, query):
        from sqlalchemy import or_
        from lite_mms import constants, models
        return query.filter(
            models.Order.sub_order_list.any(
                or_(models.SubOrder.remaining_quantity > 0,
                    models.SubOrder.work_command_list.any(
                        models.WorkCommand.status != constants.work_command.STATUS_FINISHED))))

filter_ = UnfinishedFilter("default")


