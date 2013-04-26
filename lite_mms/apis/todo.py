#-*- coding:utf-8 -*-
#TODO to be completed
from flask.ext.login import current_user
from mongoengine import Q

from lite_mms import models


class MongoAPI(object):
    @classmethod
    def wrap_message(cls, message, self=True):
        from lite_mms.apis.auth import get_user
        author = get_user(message.author.user_id)
        next_actor = get_user(message.next_actor.user_id)
        if self:
            return u"在%(create_time)s, 由%(author)s通过%(action)s分配给了一个%(" \
                   u"obj_cls)s_%(obj_pk)s给你" % {
            "create_time": message.create_time, "author": author.username if author else "",
            "action": message.message, "obj_cls": message.obj_cls,
            "obj_pk": message.obj_pk}
        else:
            return u"在%(create_time)s, 你通过%(action)s分配给了一个%(" \
                   u"obj_cls)s_%(obj_pk)s给%(next_author)s" % {
            "create_time": message.create_time, "next_author": next_actor.username if next_actor else "",
            "action": message.message, "obj_cls": message.obj_cls,
            "obj_pk": message.obj_pk}

    @classmethod
    def get_message_list(cls, user_id=None, next_user_id=None):
        q_user = Q(user_id=user_id)
        q_next_user = Q(next_user_id=next_user_id)
        if user_id and next_user_id:
            l = models.Message.objects(q_user & q_next_user).all()
        elif user_id:
            l = models.Message.objects(q_user).all()
        else:
            l = models.Message.objects(q_next_user).all()
        return l

    @classmethod
    def add(cls, obj_cls, obj_pk, obj, action, next_actor_id=None,
            actor_id=None,
            priority=0):
        actor = cls.get_mongo_user(user_id=actor_id)
        next_actor = cls.get_mongo_user(next_actor_id)

        if obj_cls is None:
            obj_cls = obj.__class__.__name__
        if obj_pk is None and hasattr(obj, "id"):
            obj_pk = obj.id
        if actor is None:
            from flask.ext.login import current_user

            if current_user.is_authenticated():
                actor = current_user

        to_do = models.Message()
        to_do.obj_cls = obj_cls
        to_do.obj_pk = str(obj_pk)
        to_do.author = actor
        to_do.message = action
        to_do.next_actor = next_actor
        to_do.priority = priority

        to_do.save()

        next_actor.to_read_messages.append(to_do)
        next_actor.save()

    @classmethod
    def object_notify(cls, obj, to_user=(), sender=None, **kwargs):

        for user in to_user:
            MongoAPI.add(obj_cls=obj.__class__.__name__, obj_pk=obj.id,
                         obj=obj, action=kwargs.get("action"),
                         next_actor_id=user.id,
                         actor_id=sender.id or current_user.id)

    @classmethod
    def delete(cls, obj_cls, obj_pk):
        '''

        :param cls:
        :param obj_cls:
        :param obj_pk:
        :return:
        '''
        models.Message.objects(
            Q(obj_pk=str(obj_pk)) & Q(obj_cls=str(obj_cls))).delete()

    @classmethod
    def get_mongo_user(self, user_id):
        user, created = models.Identity.objects.get_or_create(
            user_id=user_id)
        if created:
            user.save()
        return user