# -*- coding: UTF-8 -*-

from CodernityDB.hash_index import HashIndex
from lite_task_flow.constants import TASK_TYPE_CODE


class TaskWithGroup(HashIndex):

    """
    an index indexed by task flow id and task tag
    """
    TAG = 'task_with_group'
    custom_header = "from lite_task_flow import constants"

    def __init__(self, *args, **kwargs):
        kwargs['key_format'] = 'I'
        super(TaskWithGroup, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        if data.get('t') == constants.TASK_TYPE_CODE:
            handle_group_id = data['extra_params'].get('handle_group_id')
            if handle_group_id is not None:
                return handle_group_id, None

    def make_key(self, key):
        return key.id
