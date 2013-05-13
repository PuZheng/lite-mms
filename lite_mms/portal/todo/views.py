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
        return [wraps(obj) for obj in models]

    @login_required
    def try_view(self, list_=None):
        pass

to_do_view = TODOView(models.TODO, u"待办事项")
