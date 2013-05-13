#-*- coding:utf-8 -*-
from . import ModelWrapper
from lite_mms import models
from lite_mms.utilities import do_commit
from .notify import notifications


class TODOWrapper(ModelWrapper):

    @property
    def create_date(self):
        return self.create_time.date()


def new_todo(whom, action, obj=None, msg="", sender=None, **kwargs):
    """
    告诉"whom"对"obj"执行"action" 
    :param whom: who should be responsible for this todo
    :type whom: models.User
    :param str action: what should do
    :param obj: action should be performed upon which
    :param msg: supplementary message
    :param sender: who send this message, if not specified, we regard SYSTEM
        send this todo
    :Param kwargs: supplementary information
    """
    todo = do_commit(todo_factory.render(whom, action, obj, msg, sender, **kwargs))
    notify(whom.id, todo.id)

def notify(user_id, to_do_id):
    notifications.add(user_id, to_do_id)

def remove_todo(action, obj_pk):
    for to_do in models.TODO.query.filter(
                    models.TODO.action==action).filter(
                    models.TODO.obj_pk==obj_pk).all():
        do_commit(to_do, "delete")

class ToDoFactory(object):

    def __init__(self):
        self.__map = {}

    def render(self, whom, action, obj, msg, sender, **kwargs):
        return self.__map[action](whom, action, obj, msg, sender, **kwargs)

    def upon(self, action):
        def _(strategy):
            self.__map[action] = strategy
        return _

todo_factory = ToDoFactory()

def get_all_notify(user_id):
    id_list = notifications.pop(user_id)
    if id_list:
        return [TODOWrapper(i) for i in models.TODO.query.filter(models.TODO.id.in_(id_list)).all()]
    return []

WEIGH_UNLOAD_TASK = u"weigh_unload_task"

@todo_factory.upon(WEIGH_UNLOAD_TASK)
def weigh_unload_task(whom, action, obj, msg, sender, **kwargs):
    """
    称重任务
    """
    from lite_mms.basemain import data_browser
    msg = u'装卸工%s完成了一次来自%s(车牌号"%s")卸货任务，请称重！' % (obj.creator.username, obj.customer.name, obj.unload_session.plate) + (msg and " - " + msg)
    return models.TODO(user=whom, action=action, obj_pk=obj.id, actor=sender, 
                msg=msg, 
                context_url=data_browser.get_form_url(obj.unload_session))
    