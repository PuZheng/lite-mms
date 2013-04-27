#-*- coding:utf-8 -*-
#TODO to be completed
from . import ModelWrapper
from lite_mms import models
from lite_mms.utilities import do_commit
from .notify import notifications

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

        return do_commit(to_do)

    @classmethod
    def object_notify(cls, obj, to_user=(), sender=None, **kwargs):

        for user in to_user:
            to_do = cls.add(obj_cls=obj.__class__.__name__, obj_pk=obj.id, obj=obj,
                    action=kwargs.get("action"), next_actor=user, actor=sender)
            cls.notify(user.id, to_do.id)

    @classmethod
    def delete(cls, obj_cls, obj_pk):
        for to_do in models.TODO.query.filter(
                        models.TODO.obj_cls == obj_cls).filter(
                        models.TODO.obj_pk == obj_pk).all():
            do_commit(to_do, "delete")

    @classmethod
    def notify(cls, user_id, to_do_id):
        notifications.add(user_id, to_do_id)

    @classmethod
    def get_all_notify(cls, user_id):
        notifies = notifications.get(user_id)
        if notifies:
            notifications.delete(user_id)
            notifies = cls.get_messages(notifies)
        return notifies

    @classmethod
    def get_messages(cls, id_list):
        return [TODOWrapper(todo) for todo in
                models.TODO.query.filter(models.TODO.id.in_(id_list)).all()]

    @property
    def create_date(self):
        return self.create_time.date()

    def to_json(self):
        return u"在%(create_time)s, 由%(author)s通过%(action)s分配给了一个%(obj_cls)s_%(obj_pk)s给你" % {
        "create_time": self.create_time, "author": self.actor.username,
        "action": self.action, "obj_cls": self.obj_cls,
        "obj_pk": self.obj_pk}