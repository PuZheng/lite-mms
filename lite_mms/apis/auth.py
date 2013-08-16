# -*- coding: utf-8 -*-
"""
用户类
"""
from hashlib import md5
from flask import session, g
import flask.ext.login as login
from sqlalchemy.orm.exc import NoResultFound
from lite_mms.exceptions import AuthenticateFailure
from lite_mms.apis import ModelWrapper
from lite_mms.basemain import app
from itsdangerous import URLSafeTimedSerializer
from lite_mms.constants import groups

class UserWrapper(login.UserMixin, ModelWrapper):
    """
    a wrapper of the actual user model
    """

    @property
    def default_url(self):
        return self.group.default_url

    @property
    def permissions(self):
        ret = set()
        for group in self.groups:
            for perm in group.permissions:
                ret.add(perm)
        return ret

    @property
    def group(self):
        for group in self.groups:
            if group.id == int(session['current_group_id']):
                return group
        return self.groups[0]

    @property
    def group_name(self):
        """
        get the group name of the **FIRST** group that user belongs
        """
        return self.group.name

    def __eq__(self, other):
        """
        比较。如果id相同，则认为相同
        :param other: 比较的对象
        :return:True or False
        """
        return isinstance(other, UserWrapper) and self.id == other.id

    def __repr__(self):
        return "<UserWrapper %s> " % self.username

    @property
    def can_login_client(self):
        """
        test if the user could login in client
        """
        can_login_groups = { 
            groups.DEPARTMENT_LEADER, 
            groups.TEAM_LEADER, 
            groups.LOADER, 
            groups.QUALITY_INSPECTOR
        }
        return all(group.id in can_login_groups for group in self.groups)

    @property
    def _serializer(self):
        """
        get a serializer to generate authentication token
        """
        secret_key = app.config.get('SECRET_KEY')
        salt = app.config.get('SECURITY_%s_SALT' % self.username.upper())
        return URLSafeTimedSerializer(secret_key=secret_key, salt=salt)

    def get_auth_token(self):
        '''
        get the authentiaction token, see `https://flask-login.readthedocs.org/en/latest/#flask.ext.login.LoginManager.token_loader`_
        '''
        return self._serializer.dumps([self.username, self.password])

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


def get_user_list(group_id=None):
    from lite_mms import models
    q = models.User.query
    if group_id:
        q = q.filter(models.User.groups.any(models.Group.id == group_id))
    return [UserWrapper(user) for user in q.all()]


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
        raise AuthenticateFailure("用户名或者密码错误")


if __name__ == "__main__":
    pass
