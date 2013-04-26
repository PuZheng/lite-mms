#-*- coding:utf-8 -*-
from flask.ext.login import login_user


def authenticate(username, password):
    user = get_user(username, password)
    if user and login_user(user):
        return True
    else:
        return False


def get_user(username=None, password=None, user_id=None):
    from models import User
    if username or password:
        user = User.objects.filter(username=username, password=password).first()
    else:
        user = User.objects.with_id(user_id)
    return user
