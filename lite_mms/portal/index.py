# -*- coding: UTF-8 -*-
from flask import redirect, send_from_directory, url_for, abort, render_template, request, json
from flask.ext.login import current_user, login_required
from lite_mms.basemain import app, nav_bar
from lite_mms.utilities import decorators

@app.route("/")
def index():
    if current_user.is_authenticated():
        next_url = current_user.default_url
    else:
        next_url = url_for("auth.login")
    if not next_url:
        abort(404)
    return redirect(next_url)

@app.route("/error")
def error():
    return render_template("error.html", msg=request.args["msg"], back_url=request.args["back_url"], nav_bar=nav_bar)

@app.route("/index")
@decorators.templated("index.html")
@login_required
@decorators.nav_bar_set
def default():
    return dict(titelname=u"首页")


@app.route("/serv-pic/<filename>")
def serv_pic(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route("/message")
def ajax_new_message():
    from lite_mms.apis.todo import TODOWrapper
    messages = []
    for message in TODOWrapper.get_all_notify(current_user.id):
        messages.append(message.to_dict())
    return json.dumps(messages)