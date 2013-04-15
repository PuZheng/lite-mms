#-*- coding:utf-8 -*-
from sqlalchemy.orm.exc import NoResultFound
from lite_mms import models


def get(name, default=None, type=None):
    try:
        rv = models.Config.query.filter(
            models.Config.property_name == name).one().property_value
        if type is not None:
            rv = type(rv)
    except (KeyError, ValueError, NoResultFound):
        rv = default
    return rv