#-*- coding:utf-8 -*-
#TODO to be completed
from . import ModelWrapper
from lite_mms import models
from lite_mms.utilities import do_commit


class TODOWrapper(ModelWrapper):
    def get_list(self, user):
        return [ModelWrapper(obj) for obj in
                models.TODO.query.filter(models.TODO.user == user).all()]

    def get(self, id_):
        one = models.TODO.get(id_)
        if one:
            return ModelWrapper(one)
        else:
            return None

    @classmethod
    def add(cls, obj_cls, obj_pk, obj, action, next_actor=None, actor=None,
            priority=0):

        if obj_cls is None:
            obj_cls = obj.__class__.__name__
        if obj_pk is None and hasattr(obj, "id"):
            obj_pk = obj.id
        if actor is None:
            from flask.ext.login import current_user

            if current_user.is_authenticated():
                actor = current_user

        to_do = models.TODO()
        to_do.obj_cls = obj_cls
        to_do.obj_pk = obj_pk
        to_do.actor = actor
        to_do.action = action
        if next_actor:
            to_do.user = next_actor
        to_do.priority = priority

        do_commit(to_do)