#-*- coding:utf-8 -*-
from flask import request
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

    @property
    def url_map(self):
        def _obj_wrap(str_, id_):
            from lite_mms.basemain import app
            from lite_mms.utilities import camel_case
            for endpoint, url in app.url_map._rules_by_endpoint.iteritems():
                if endpoint.endswith(camel_case(str_)):
                    args = url[0].arguments
                    if args:
                        return url[0].build({enumerate(args).next()[1]: id_,
                                             "url": request.url})[1]
                    else:
                        return url[0].build({"id": id_, "url": request.url})[1]

