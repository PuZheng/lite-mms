# -*- coding: utf-8 -*-
"""
用户类
"""
from hashlib import md5
from flask import session
import flask.ext.login as login
from sqlalchemy.orm.exc import NoResultFound
from lite_mms.exceptions import AuthenticateFailure
from lite_mms.apis import ModelWrapper


class UserWrapper(login.UserMixin, ModelWrapper):
    """
    a wrapper of the actual user model
    """

    @property
    def default_url(self):
        return self.groups[0].default_url

    @property
    def permissions(self):
        ret = set()
        for group in self.groups:
            for perm in group.permissions:
                ret.add(perm)
        return ret

    @property
    def group_name(self):
        """
        get the group name of the **FIRST** group that user belongs
        """
        try:
            return self.groups[0].name
        except IndexError:
            return "-"

    def __eq__(self, other):
        """
        比较。如果id相同，则认为相同
        :param other: 比较的对象
        :return:True or False
        """
        return isinstance(other, UserWrapper) and self.id == other.id

    def __repr__(self):
        return "<UserWrapper %s> " % self.username


def get_user(id_):
    if not id_:
        return None
        # TODO 这里需要优化
    from lite_mms import models

    try:
        return UserWrapper(
            models.User.query.filter(models.User.id == id_).one())
    except NoResultFound:
        return None


def get_user_list():
    from lite_mms import models

    return [UserWrapper(user) for user in models.User.query.all()]


def authenticate(username, password):
    """
    authenticate a user, test if username and password mathing
    :return: an authenticated User or None if can't authenticated
    :rtype: User
    :raise: exceptions.AuthenticateFailure
    """
    try:
        from lite_mms import models

        return UserWrapper(
            models.User.query.filter(models.User.username == username).filter(
                models.User.password == md5(password).hexdigest()).one())
    except NoResultFound:
        raise AuthenticateFailure("无此用户")


if __name__ == "__main__":
    pass
