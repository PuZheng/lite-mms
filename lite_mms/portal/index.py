# -*- coding: UTF-8 -*-
from flask import redirect, send_from_directory, url_for, abort
from flask.ext.login import current_user, login_required
from lite_mms.basemain import app
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

@app.route("/index")
@decorators.templated("index.html")
@login_required
@decorators.nav_bar_set
def default():
    return dict(titelname=u"首页")


@app.route("/serv-pic/<filename>")
def serv_pic(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


