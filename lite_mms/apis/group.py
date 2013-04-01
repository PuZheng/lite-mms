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

def get_group(id_):
    try:
        return models.Group.query.filter_by(id=id_).one()
    except NoResultFound:
        return None

