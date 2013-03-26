# -*- coding: UTF-8 -*-
"""
@author: Yangminghua
@version: $
"""
from sqlalchemy.exc import SQLAlchemyError
from lite_mms import models

def get_plate_list(status=None):
    def _get_condition(plate_q, status):
        if status == "unloading":
            model = models.UnloadSession
        elif status == "delivering":
            model = models.DeliverySession
        else:
            return plate_q
        return plate_q.join(model, model.plate == models.Plate.name).filter(
            model.finish_time == None)

    return [p.name for p in
            _get_condition(models.Plate.query, status).all()]
