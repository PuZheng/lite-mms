# -*- coding: UTF-8 -*-
"""
@author: Yangminghua
@version: $
"""
import warnings
from lite_mms import models

warnings.warn("doesn't use",DeprecationWarning)

from sqlalchemy.orm.exc import NoResultFound

class Group(object):
    def __init__(self, _id, name, permissions):
        self.id = _id
        self.name = name
        self.permissions = permissions

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, Group) and other.id == self.id

    @classmethod
    def _from_json(cls, json_group):
        return Group(_id=json_group["id"], name=json_group["name"],
            permissions=json_group["permissions"])

    @classmethod
    def get_list(cls):
        return models.Group.query.all()

    @classmethod
    def get_group(cls, _id):
        try:
            return models.Group.query.filter_by(id=_id).one()
        except NoResultFound:
            return None

get_group = Group.get_group
