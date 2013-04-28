#-*- coding:utf-8 -*-
from flask.ext.databrowser import ModelView, filters
from flask.ext.login import login_required, current_user
from lite_mms.apis import wraps

from lite_mms import models


class TODOView(ModelView):
    list_template = "todo/o-list.html"

    def __list_filters__(self):
        return [filters.EqualTo("user_id", value=current_user.id)]

    def scaffold_list(self, models):
        class _Proxy(object):
            def __init__(self, obj):
                self._obj = obj

            def __getattr__(self, item):
                if hasattr(self._obj, item):
                    return getattr(self._obj, item)
                else:
                    if item == "obj":
                        return get_obj(getattr(self, "obj_cls", None),
                                       getattr(self, "obj_pk", None))
                    else:
                        return getattr(self.obj, item)

        return [_Proxy(wraps(obj)) for obj in models]

    @login_required
    def try_view(self, list_=None):
        pass


def get_obj(obj_cls, obj_pk):
    if obj_cls and obj_pk:
        model = getattr(models, obj_cls)
        one = model.query.get(obj_pk)
        if one:
            return wraps(one)
    return None

to_do_view = TODOView(models.TODO, u"待办事项")