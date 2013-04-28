# -*- coding: UTF-8 -*-
import json
from flask.ext.mongoengine import MongoEngine
from flask import Flask, render_template, redirect, url_for, request
from flask.ext.login import LoginManager, current_user, logout_user
from flask.ext.babel import Babel

app = Flask(__name__)

app.config["MONGODB_DB"] = "localhost"
app.config["DEBUG"] = True
app.config["MONGODB_DBRef"] = True
app.config["CSRF_ENABLED"] = False

app.secret_key = "DJklfj;12"
db = MongoEngine(app)
login_manager = LoginManager()
login_manager.init_app(app)
babel = Babel(app)

from flask.ext.mongoengine.wtf import model_form

from lite_todo import app

import models

LoginForm = model_form(models.User, exclude="to_read_messages")

@app.route("/")
def index():
    if current_user.is_authenticated():
        return render_template("index.html")
    else:
        return redirect(url_for("login"))


@app.route("/login", methods=("GET", "POST"))
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate():
        from auth import authenticate

        if authenticate(form.username.data, form.password.data):
            return redirect(url_for("index"))
        else:
            return "error", 403
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    if logout_user():
        return redirect(url_for("index"))
    else:
        return "error", 403

@app.route("/message")
def ajax_new_message():
    messages = []
    for message in current_user.to_read_messages:
        # dict_ = {"author": message.author.username, "message": message.message,
        #          "next_actor": message.next_actor.username,
        #          "create_time": unicode(message.create_time), "obj_pk": message.obj_pk,
        #          "obj_cls": message.obj_cls}

        detail = u"在%(create_time)s, 由%(author)s通过%(action)s分配给了一个%(obj_cls)s_%(obj_pk)s给你" % {
        "create_time": message.create_time, "author": message.author.username,
        "action": message.message, "obj_cls": message.obj_cls,
        "obj_pk": message.obj_pk}
        messages.append(detail)
    # current_user.to_read_messages = []
    # current_user.save()
    return json.dumps(messages)


@login_manager.user_loader
def load_user(user_id):
    import auth

    return auth.get_user(user_id=user_id)


if __name__ == "__main__":
    app.run()