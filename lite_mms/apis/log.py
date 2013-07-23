#-*- coding:utf-8 -*-
from lite_mms.apis import ModelWrapper
from lite_mms import models

model_map = {k: v for k, v in models.__dict__.items() if hasattr(v, "_sa_class_manager")}


class LogWrapper(ModelWrapper):
    @classmethod
    def get_log_list(cls, pk, model_name):
        return [LogWrapper(l) for l in
                models.Log.query.filter(models.Log.obj_pk == pk).filter(models.Log.obj_cls == model_name).all()]

    @property
    def obj_class(self):
        try:
            return model_map.get(self.obj_cls).__modelname__
        except (TypeError, AttributeError):
            return u"未知"


