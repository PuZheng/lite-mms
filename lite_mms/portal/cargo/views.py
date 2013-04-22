# -*- coding: utf-8 -*-
import re
import json

from flask import request, abort, url_for, render_template, flash
from flask.ext.babel import _
from flask.ext.login import current_user
from flask.ext.databrowser import ModelView
from flask.ext.databrowser.column_spec import InputColumnSpec, ColumnSpec, PlaceHolderColumnSpec, ListColumnSpec
from werkzeug.utils import redirect
from wtforms import Form, IntegerField, validators, HiddenField
from werkzeug.datastructures import OrderedMultiDict

from lite_mms.portal.cargo import cargo_page, fsm
from lite_mms.utilities import decorators, do_commit
from lite_mms.permissions import CargoClerkPermission,AdminPermission
from lite_mms import constants
from lite_mms.basemain import nav_bar
from lite_mms.apis import wraps
import lite_mms.constants.cargo as cargo_const
from lite_mms.models import UnloadSession, Plate

@cargo_page.route('/')
def index():
    return redirect(unload_session_model_view.url_for_list())

class UnloadSessionModelView(ModelView):

    list_template = "cargo/unload-session-list.html"
    edit_template = "cargo/unload-session.html"

    as_radio_group = True
    can_batchly_edit = False

    __list_columns__ = ["id", "plate_", "create_time", "finish_time", "with_person", "status", 
                        ListColumnSpec("customer_list_unwrapped", label=u"客户列表", compressed=True),
                        PlaceHolderColumnSpec("goods_receipt_list", label=u"收货单", template_fname="cargo/goods-receipts-snippet.html")]

    __column_labels__ = {"id": u"编号", "plate_": u"车辆", "create_time": u"创建时间", "finish_time": u"结束时间", 
                         "with_person": u"驾驶室", "status": u"状态", "goods_receipt_list": u"收货单", "gross_weight": u"净重"}


    def patch_row_css(self, idx, obj): 
        if len(obj.customer_list) > len(obj.goods_receipt_list):
            return "alert alert-warning"

    __column_formatters__ = {
        "create_time": lambda v, obj: v.strftime("%m月%d日 %H点").decode("utf-8"),
        "finish_time": lambda v, obj: v.strftime("%m月%d日 %H点").decode("utf-8") if v else "--",
        "with_person": lambda v, obj: u'有人' if v else u'无人', 
        "status": lambda v, obj: cargo_const.desc_status(v),
    }

    __default_order__ = ("id", "desc")

    __sortable_columns__ = ["id", "plate", "create_time", "finish_time"]

    from flask.ext.databrowser import filters                             
    from datetime import datetime, timedelta                              
    today = datetime.today()                                              
    yesterday = today.date()                                                 
    week_ago = (today - timedelta(days=7)).date()                         
    _30days_ago = (today - timedelta(days=30)).date()      


    __column_filters__ = [filters.BiggerThan("create_time", name=u"在", default_value=str(yesterday),
                                             options=[(yesterday, u'一天内'), (week_ago, u'一周内'), (_30days_ago, u'30天内')]),
                          filters.Only("status", display_col_name=u"仅展示未完成会话", test=lambda col: ~col.in_([cargo_const.STATUS_CLOSED, cargo_const.STATUS_DISMISSED]), notation="__only_unclosed")
                         ]

    def try_view(self):
        from flask.ext.principal import Permission
        Permission.union(CargoClerkPermission, AdminPermission).test()

    def preprocess(self, model):
        from lite_mms import apis
        return apis.cargo.UnloadSessionWrapper(model)

    def get_customized_actions(self, model=None):
        from lite_mms.portal.cargo.actions import MyDeleteAction, CloseAction, OpenAction
        if model is None: # for list
            return [MyDeleteAction(u"删除", CargoClerkPermission), CloseAction(u"关闭"), OpenAction(u"打开")]
        else:
            if model.status in [cargo_const.STATUS_CLOSED, cargo_const.STATUS_DISMISSED]:
                return [MyDeleteAction(u"删除", CargoClerkPermission), OpenAction(u"打开")]
            else:
                return [MyDeleteAction(u"删除", CargoClerkPermission), CloseAction(u"关闭")]

    # ================= FORM PART ============================
    __create_columns__ = ["plate_", InputColumnSpec("with_person", label=u"驾驶室是否有人"), "gross_weight"]
    __form_columns__ = OrderedMultiDict()
    __form_columns__[u"详细信息"] = [
        InputColumnSpec("plate_", opt_filter=lambda obj: not wraps(obj).unloading), 
        InputColumnSpec("with_person", label=u"驾驶室是否有人"),
        ColumnSpec("status", label=u"状态", formatter=lambda v, obj: '<strong>' + cargo_const.desc_status(v) + '</strong>', 
                   css_class="input-small uneditable-input"), 
        InputColumnSpec("create_time", label=u"创建时间", read_only=True),
        InputColumnSpec("finish_time", label=u"结束时间", read_only=True),
        PlaceHolderColumnSpec(col_name="id", label=u"日志", template_fname="cargo/us-log-snippet.html")
    ]
    __form_columns__[u"收货任务列表"] = [PlaceHolderColumnSpec(col_name="task_list", label=u"", template_fname="cargo/unload-task-list-snippet.haml")]

unload_session_model_view = UnloadSessionModelView(UnloadSession, u"卸货会话")

class plateModelView(ModelView):
    
    can_edit = False
    create_template = "cargo/plate.html" 
    
    __create_columns__ = [
        InputColumnSpec("name", 
                        doc=u'车牌号的形式应当是"省份缩写+字母+空格+五位数字或字母"',
                        validators=[validators.Regexp(u'^[\u4E00-\u9FA3][a-z]\s*[a-z0-9]{5}$', flags=re.IGNORECASE|re.U, message=u"格式错误")]),
    ]

    def populate_obj(self, form):
        # normalize plate
        name = form["name"].data
        m = re.match(u'^(?P<part1>[\u4E00-\u9FA3][a-z])\s*(?P<part2>[a-z0-9]{5})$', name, re.IGNORECASE|re.U)
        name = m.groupdict()["part1"] + ' ' + m.groupdict()["part2"]
        name = name.upper()
        return Plate(name=name)

plate_model_view = plateModelView(Plate, u"车辆")

@cargo_page.route("/weigh-unload-task/<int:id_>", methods=["GET", "POST"])
@decorators.templated("/cargo/unload-task.haml")
def weigh_unload_task(id_):
    from lite_mms import apis
    task = apis.cargo.get_unload_task(id_)
    if not task:
        abort(404)
    if request.method == 'GET':
        return dict(plate=task.unload_session.plate, task=task,
            product_types=apis.product.get_product_types(),
            products=json.dumps(apis.product.get_products()))
    else: # POST
        class _ValidationForm(Form):
            weight = IntegerField('weight', [validators.required()])
            product = IntegerField('product')
        form = _ValidationForm(request.form)
        if form.validate():
            weight = task.last_weight - form.weight.data
            if weight < 0:
                abort(403)
            task.update(weight=weight, product_id=form.product.data)
            from flask.ext.login import current_user
            fsm.fsm.reset_obj(task.unload_session)
            fsm.fsm.next(cargo_const.ACT_WEIGHT, current_user)
            return redirect(unload_session_model_view.url_for_object(model=task.unload_session.model))
        else:
            return render_template("validation-error.html", errors=form.errors,
                                   back_url=unload_session_model_view.url_for_object(model=task.unload_session.model),
                                   nav_bar=nav_bar), 403


@cargo_page.route("/unload-session/", methods=["POST", "GET"])
@cargo_page.route("/unload-session/<int:id_>", methods=["POST", "GET"])
def unload_session(id_=None):
    from lite_mms import apis

    if request.method == "GET":
        if id_:
            unload_session = apis.cargo.get_unload_session(id_)
            if not unload_session:
                abort(404)
            return render_template("cargo/unload-session.html",
                                   unload_session=unload_session,
                                   titlename=u"卸货会话详情",
                                   order_types=apis.order.get_order_type_list(),
                                   nav_bar=nav_bar)
        else:
            working_list = []
            working_list.extend(apis.plate.get_plate_list("unloading"))
            working_list.extend(apis.plate.get_plate_list("delivering"))
            return render_template("cargo/unload-session-add.html",
                                   titlename=u"新增卸货会话",
                                   plateNumbers=apis.plate.get_plate_list(),
                                   working_plate_list=json.dumps(working_list),
                                   nav_bar=nav_bar)
    else:
        if id_:
            unload_session = apis.cargo.get_unload_session(id_)
            url = request.form.get('url')
            if not unload_session:
                abort(404)
            if request.form.get("method") == "reopen":
                if unload_session.closed:
                    fsm.fsm.reset_obj(unload_session)
                    fsm.fsm.next(constants.cargo.ACT_OPEN, current_user)
                    flash(u"重新打开卸货会话%d成功！" % unload_session.id)
                else:
                    return _(u"该会话不能重新打开"), 403
            elif request.form.get("method") == "finish":
                if unload_session.closeable:
                    fsm.fsm.reset_obj(unload_session)
                    fsm.fsm.next(constants.cargo.ACT_CLOSE, current_user)
                    flash(u"结束卸货会话%d成功！" % unload_session.id)
                else:
                    return _(u"该会话不能结束"), 403
            elif request.form.get("method") == "delete":
                if unload_session.deleteable:
                    do_commit(unload_session, action="delete")
                    flash(u"删除成功！")
                    return redirect(url_for("cargo.unload_session_list"))
                else:
                    return _(u'该卸货会话已经有卸货任务不能删除！'), 403
            return redirect(url_for('cargo.unload_session', id_=id_,
                                    _method="GET", url=url))
        else:
            with_person = request.form.get("with_person", False, type=bool)
            unload_session = apis.cargo.new_unload_session(
                request.form['plateNumber'], request.form['grossWeight'],
                with_person)

            return redirect(
                url_for('cargo.unload_session', id_=unload_session.id,
                        _method="GET"))


@cargo_page.route("/unload-task/<int:id_>", methods=["GET", "POST"])
@decorators.templated("cargo/unload-task.html")
@decorators.nav_bar_set
def unload_task(id_):
    from lite_mms import apis

    if request.method == 'GET':
        task = apis.cargo.get_unload_task(id_)
        if not task:
            abort(404)
        return dict(task=task, product_types=apis.product.get_product_types(),
                    products=json.dumps(apis.product.get_products()))
    else: # POST
        if id_:
            task = apis.cargo.get_unload_task(id_)
            if not task:
                abort(404)
            if request.form.get("method") == "delete":
                us = task.unload_session
                do_commit(task, "delete")
                fsm.fsm.reset_obj(us)
                fsm.fsm.next(constants.cargo.ACT_WEIGHT, current_user)
                flash(u"删除卸货任务%d成功" % task.id)
                return redirect(
                    request.form.get("url") or url_for("cargo.unload_session",
                                                       id_=task.session_id,
                                                       _method="GET"))
            else:
                class _ValidationForm(Form):
                    weight = IntegerField('weight', [validators.required()])
                    product = IntegerField('product')
                    url = HiddenField("url")

                form = _ValidationForm(request.form)
                if form.validate():
                    session = apis.cargo.get_unload_session(session_id=task.session_id)
                    if not session:
                        abort(404)

                    weight = task.last_weight - form.weight.data
                    if weight < 0:
                        abort(500)
                    if not task.weight:
                        fsm.fsm.reset_obj(task.unload_session)
                        fsm.fsm.next(constants.cargo.ACT_WEIGHT, current_user)
                    task.update(weight=weight, product_id=form.product.data)
                    url = form.url.data or url_for("cargo.unload_session",
                                                   id_=task.session_id, _method="GET")
                    return redirect(url)
                else:
                    abort(403)


@cargo_page.route("/goods-receipt/", methods=["GET", "POST"])
@cargo_page.route("/goods-receipt/<int:id_>", methods=["GET", "POST"])
@decorators.templated("cargo/goods-receipt.html")
@decorators.nav_bar_set
def goods_receipt(id_=None):
    from lite_mms import apis
    if id_:
        receipt = apis.cargo.get_goods_receipt(id_)
        if not receipt:
            abort(404)
        if request.method == "GET":
            return dict(receipt=receipt, titlename=u"收货单详情",
                        product_types=apis.product.get_product_types(),
                        products=json.dumps(apis.product.get_products()))
        else:
            if request.form.get("method") == "delete":
                if receipt.order:
                    abort(403)
                else:
                    do_commit(receipt, "delete")
                    flash(u"删除收货单%s成功" % receipt.receipt_id)
                return redirect(
                    request.form.get("url") or url_for("cargo.unload_session",
                                                       id_=receipt.unload_session.id))
            else:
                if request.form.get("type") == "extra":
                    order_type = constants.EXTRA_ORDER_TYPE
                    type_ = constants.EXTRA_ORDER_TYPE_NAME
                else:
                    order_type = constants.STANDARD_ORDER_TYPE
                    type_ = constants.STANDARD_ORDER_TYPE_NAME

                order = apis.order.new_order(receipt.id,
                                             order_type,
                                             current_user.id)

                flash(u"创建%s类型的订单成功"% type_)
                return redirect(url_for("order.order", id_=order.id,
                                        url=request.form.get("url")))
    else:
        class _ValidationForm(Form):
            customer = IntegerField('customer', [validators.required()])
            unload_session_id = IntegerField('unload_session_id',
                                             [validators.required()])
            url = HiddenField('url')

        form = _ValidationForm(request.form)
        if form.validate():
            receipt = apis.cargo.new_goods_receipt(form.customer.data,
                                                   form.unload_session_id.data)
            return redirect(
                url_for("cargo.goods_receipt", id_=receipt.id, _method="GET",
                        url=form.url.data))
        else:
            flash(form.errors, "error")
            return redirect(form.url.data or url_for("cargo.unload_session"))


@cargo_page.route("/goods-receipt-preview/<int:id_>")
@decorators.templated("cargo/goods-receipt-preview.html")
@decorators.nav_bar_set
def goods_receipt_preview(id_):
    from lite_mms import apis

    receipt = apis.cargo.get_goods_receipt(id_)
    PER_PAGE  = apis.config.get("print_count_per_page", 5.0, type=float)
    import math
    pages = int(math.ceil(len(receipt.unload_task_list) / PER_PAGE))
    if not receipt:
        abort(404)
    return {"receipt": receipt, "titlename": u"收货单打印预览", "pages": pages,
            "per_page": PER_PAGE}
