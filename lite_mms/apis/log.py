#-*- coding:utf-8 -*-
import datetime
from flask import redirect, request
from lite_mms.apis import ModelWrapper
from lite_mms.models import Log


class LogWrapper(ModelWrapper):
    @classmethod
    def get_log(cls, id_):
        one = Log.query.get(id_)
        if one:
            return LogWrapper(one)
        else:
            return None

    @classmethod
    def get_log_list(cls, actor_id=None, begin_time=None, end_time=None,
                     days=None):
        q_ = Log.query
        if actor_id:
            q_ = q_.filter(Log.actor_id == actor_id)
        if begin_time:
            begin_time = datetime.datetime.strptime(begin_time, "%Y-%m-%d")
            q_ = q_.filter(Log.create_time > begin_time)
        if end_time:
            end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d") \
                       + datetime.timedelta(1)
            q_ = q_.filter(Log.create_time < end_time)
        q_ = q_.order_by(Log.create_time.desc())
        return [LogWrapper(l) for l in q_.all()]

    @property
    def create_date(self):
        return self.create_time.date()

    @property
    def url_map(self):
        def _obj_wrap(str_, id_):
            from lite_mms.basemain import app

            for endpoint, url in app.url_map._rules_by_endpoint.iteritems():
                if endpoint.endswith(str_.replace("Wrapper", "").lower()):
                    args = url[0].arguments
                    if args:
                        return url[0].build({enumerate(args).next()[1]: id_,
                                             "url": request.url})[1]
                    else:
                        return url[0].build({"id": id_, "url": request.url})[1]

        if self.obj_cls:
            yield self.obj_pk, _obj_wrap(self.obj_cls, self.obj_pk)

