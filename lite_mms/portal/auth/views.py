# -*- coding: UTF-8 -*-
from flask import request, render_template, redirect, url_for, current_app, \
    session
from lite_mms.portal.auth import auth
from flask.ext.principal import identity_changed, Identity, AnonymousIdentity
from lite_mms.utilities import _
from wtforms import PasswordField, TextField, Form, HiddenField
from flask.ext.login import login_user, logout_user, login_required, \
    current_user
from lite_mms.exceptions import AuthenticateFailure

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if current_user.is_anonymous():
            return render_template("auth/login.haml",titlename=u'登录')
        return redirect("/")
    else:
        class LoginForm(Form):
            username = TextField()
            password = PasswordField()
            next_url = HiddenField()

        form = LoginForm(request.form)
        if form.validate():
            username = form.username.data
            password = form.password.data
            try:
                import lite_mms.apis as apis
                user = apis.auth.authenticate(username, password)
            except AuthenticateFailure:
                return render_template("auth/login.haml",
                                       error=_(u"用户名或者密码错误"))
            if not login_user(user):
                return render_template("auth/login.haml",
                                       error=_(u"登陆失败"))

            identity_changed.send(current_app._get_current_object(),
                                  identity=Identity(user.id))
            return redirect(form.next_url.data or "/")
        else:
            return render_template("auth/login.haml",
                             error=_(u"请输入用户名及密码"))

@auth.route("/logout")
@login_required
def logout():
    try:
        logout_user()
    except Exception: # in case sesson expire
        pass
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())

    next_url = request.args.get("next", "/")
    return redirect(next_url)


