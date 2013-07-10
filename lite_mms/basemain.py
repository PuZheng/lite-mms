# -*- coding: UTF-8 -*-
import os
from sqlalchemy.exc import SQLAlchemyError
from flask import Flask, render_template, request, session, g
from flask.ext.babel import Babel, gettext
from flask.ext.nav_bar import FlaskNavBar

app = Flask(__name__, instance_relative_config=True)
app.config.from_object("lite_mms.default_settings")
if "LITE_MMS_HOME" in os.environ:
    app.config.from_pyfile(
        os.path.join(os.environ["LITE_MMS_HOME"], "config.py"), silent=True)
app.config.from_pyfile(os.path.join(os.getcwd(), "config.py"), silent=True)
from flask.ext.login import LoginManager, current_user
login_manager = LoginManager()
login_manager.init_app(app)
from flask.ext.principal import Principal

principal = Principal(app)

import logging
import logging.handlers

logging.basicConfig(level=logging.DEBUG)

file_handler = logging.handlers.TimedRotatingFileHandler(
    app.config["LOG_FILE"], 'D', 1, 10, "utf-8")
file_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
file_handler.suffix = "%Y%m%d.log"
app.logger.addHandler(file_handler)

from lite_mms.log.handler import DBHandler
timeline_logger = logging.getLogger("timeline")
timeline_logger.addHandler(DBHandler())
# create upload files

if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

babel = Babel(app)

nav_bar = FlaskNavBar(app)

from flask.ext.databrowser import DataBrowser
from lite_mms.database import db
from lite_mms import constants
data_browser = DataBrowser(app, db, page_size=constants.ITEMS_PER_PAGE, logger=timeline_logger)

# ============== REGISTER BLUEPRINT ========================
serve_web = app.config["SERVE_TYPE"] in ["both", "web"]
serve_ws = app.config["SERVE_TYPE"] in ["both", "ws"]


if serve_web:

    from lite_mms.portal.report import report_page
    from flask.ext.report import FlaskReport
    from flask.ext.report.utils import collect_models
    from lite_mms import models

    def collect_model_names():
        ret = {}

        for k, v in models.__dict__.items():
            if hasattr(v, '_sa_class_manager'):
                ret[v.__tablename__] = v.__modelname__
        return ret

    FlaskReport(db, collect_models(models), app, report_page, {
        'report_list': {
            'nav_bar': nav_bar,    
        },
        'report': {
            'nav_bar': nav_bar,    
        },
        'data_set': {
            'nav_bar': nav_bar,    
        },
        'data_sets': {
            'nav_bar': nav_bar,    
        }
    }, 
    collect_model_names())
    app.register_blueprint(report_page, url_prefix="/report")
    from lite_mms.portal.store import store_bill_page
    app.register_blueprint(store_bill_page, url_prefix="/store")
    from lite_mms.portal.deduction import deduction_page
    app.register_blueprint(deduction_page, url_prefix="/deduction")
    from lite_mms.portal.auth import auth
    app.register_blueprint(auth, url_prefix="/auth")
    from lite_mms.portal.cargo import cargo_page, gr_page
    app.register_blueprint(cargo_page, url_prefix='/cargo')
    app.register_blueprint(gr_page, url_prefix='/goods_receipt')
    from lite_mms.portal.delivery import delivery_page, consignment_page
    app.register_blueprint(delivery_page, url_prefix='/delivery')
    app.register_blueprint(consignment_page, url_prefix='/consignment')
    from lite_mms.portal.misc import misc
    app.register_blueprint(misc, url_prefix="/misc")
    from lite_mms.portal.manufacture import manufacture_page
    app.register_blueprint(manufacture_page, url_prefix="/manufacture")
    from lite_mms.portal.order import order_page
    app.register_blueprint(order_page, url_prefix="/order")
    from lite_mms.portal.op import op_page
    app.register_blueprint(op_page, url_prefix="/op")
    from lite_mms.portal.admin2 import admin2_page
    app.register_blueprint(admin2_page, url_prefix="/admin2")
    
    from lite_mms.portal.import_data import import_data_page
    app.register_blueprint(import_data_page, url_prefix="/import_data")
    from lite_mms.portal.search import search_page
    app.register_blueprint(search_page, url_prefix="/search")

    from lite_mms.portal.timeline import time_line_page
    app.register_blueprint(time_line_page, url_prefix="/timeline")

    from lite_mms.portal.todo import to_do_page
    app.register_blueprint(to_do_page, url_prefix="/todo")

    import lite_mms.portal.admin

if serve_ws:
    from lite_mms.portal.auth_ws import auth_ws
    app.register_blueprint(auth_ws, url_prefix="/auth_ws")
    from lite_mms.portal.cargo_ws import cargo_ws
    app.register_blueprint(cargo_ws, url_prefix='/cargo_ws')
    from lite_mms.portal.delivery_ws import delivery_ws
    app.register_blueprint(delivery_ws, url_prefix='/delivery_ws')
    from lite_mms.portal.order_ws import order_ws
    app.register_blueprint(order_ws, url_prefix="/order_ws")
    from lite_mms.portal.manufacture_ws import manufacture_ws
    app.register_blueprint(manufacture_ws, url_prefix="/manufacture_ws")

# ====================== REGISTER NAV BAR ===================================
from lite_mms.permissions.roles import (CargoClerkPermission, AccountantPermission, QualityInspectorPermission,
                                        DepartmentLeaderPermission, AdminPermission, SchedulerPermission)
from lite_mms.permissions.order import view_order, schedule_order
from lite_mms.permissions.work_command import view_work_command
nav_bar.register(cargo_page, name=u"卸货会话", permissions=[CargoClerkPermission], group=u"卸货管理")
nav_bar.register(gr_page, name=u"收货单", permissions=[CargoClerkPermission], group=u"卸货管理")
nav_bar.register(order_page, default_url='/order/order-list', name=u"订单管理",
                 permissions=[view_order])
nav_bar.register(order_page, default_url='/order/order-list', name=u"订单管理",
                 permissions=[schedule_order])
nav_bar.register(delivery_page, name=u'发货会话',
                 permissions=[CargoClerkPermission], group=u"发货管理")
nav_bar.register(consignment_page, name=u'发货单',
                 permissions=[CargoClerkPermission.union(AccountantPermission)], group=u"发货管理")
nav_bar.register(manufacture_page, name=u"工单管理",
                 permissions=[SchedulerPermission])
#nav_bar.register(delivery_page, name=u"发货单管理",
                 #default_url="/delivery/consignment-list",
                 #permissions=[AccountantPermission])
nav_bar.register(manufacture_page, name=u"质检管理",
                 default_url="/manufacture/qir-list",
                 permissions=[DepartmentLeaderPermission])
nav_bar.register(store_bill_page, name=u"仓单管理",
                 default_url="/store/store-bill-list",
                 permissions=[QualityInspectorPermission])
nav_bar.register(deduction_page, name=u"扣重管理", default_url="/deduction/",
                 permissions=[QualityInspectorPermission])

nav_bar.register(time_line_page, name=u"时间线", default_url="/timeline/log-list")
nav_bar.register(search_page, name=u"搜索", default_url="/search/search")
nav_bar.register(admin2_page, name=u"管理中心", default_url="/admin2/user-list", permissions=[AdminPermission])
nav_bar.register(to_do_page, name=u"待办事项", default_url="/todo/todo-list")
nav_bar.register(report_page, name=u"报表列表", default_url="/report/report-list", permissions=[AdminPermission], group=u'报表', 
                 enabler=lambda nav: request.path.startswith('/report/report'))
nav_bar.register(report_page, name=u"数据集合列表", default_url="/report/data-sets", permissions=[AdminPermission], group=u'报表', 
                 enabler=lambda nav: request.path.startswith('/report/data-set'))


#install jinja utilities
from lite_mms.utilities import url_for_other_page, datetimeformat
from lite_mms.utilities.decorators import after_this_request 
from lite_mms import permissions

app.jinja_env.globals['url_for_other_page'] = url_for_other_page
app.jinja_env.globals['permissions'] = permissions
app.jinja_env.filters['_datetimeformat'] = datetimeformat
app.jinja_env.add_extension("jinja2.ext.loopcontrols")

from flask.ext.principal import (identity_loaded, RoleNeed, UserNeed, PermissionDenied)

@login_manager.user_loader
def load_user(user_id):
    from lite_mms.apis import auth
    return auth.get_user(user_id)


@identity_loaded.connect_via(app)
def permission_handler(sender, identity):
    from flask.ext import login

    identity.user = login.current_user
    if not identity.user:
        return
    if hasattr(identity.user, 'id'):
        identity.provides.add(UserNeed(unicode(identity.user.id)))

    if hasattr(identity.user, 'groups'):
        current_group_id = session.get('current_group_id')
        if current_group_id is None:
            current_group_id = request.cookies.get('current_group_id')
        if current_group_id is None:
            group = identity.user.groups[0]
            @after_this_request
            def set_group_id(response):
                response.set_cookie('current_group_id', str(group.id))
                return response
        else:
            for group_ in identity.user.groups:
                if group_.id == current_group_id:
                    group = group_
                    break
            else:
                group = identity.user.groups[0]
                @after_this_request
                def set_group_id(response):
                    response.set_cookie('current_group_id', str(group.id))
                    return response
        session['current_group_id'] = str(group.id)
        identity.provides.add(RoleNeed(unicode(group.id)))

    if hasattr(identity.user, 'permissions'):
        for perm in identity.user.permissions:
            try:
                for need in permissions.permissions[perm.name]["needs"]:
                    identity.provides.add(need)
            except KeyError:
                pass

#设置无权限处理器
@app.errorhandler(PermissionDenied)
@app.errorhandler(401)
def permission_denied(error):

    #如果用户已登录则显示无权限页面
    from flask import redirect, url_for
    if not current_user.is_anonymous():
        return redirect(url_for("error", msg=u'请联系管理员获得访问权限!',
                                back_url=request.args.get("url")))
        #如果用户还未登录则转向到登录面
    return render_template("auth/login.html",
                           error=gettext(u"请登录"), next_url=request.url, titlename=u"请登录")

if not app.config["DEBUG"]:
    @app.errorhandler(Exception)
    def error(error):
        if isinstance(error, SQLAlchemyError):
            from lite_mms.database import db

            db.session.rollback()
        from werkzeug.debug.tbtools import get_current_traceback

        traceback = get_current_traceback(skip=1, show_hidden_frames=False,
                                          ignore_system_exceptions=True)
        app.logger.error("%s %s" % (request.method, request.url))
        app.logger.error(traceback.plaintext)
        return render_template("result.html", error_content=u"系统异常!",
                               back_url=request.args.get("back_url", "/"),
                               nav_bar=nav_bar), 403

@app.after_request
def call_after_request_callbacks(response):
    for callback in getattr(g, 'after_request_callbacks', ()):
        response = callback(response)
    return response
