# -*- coding: utf-8 -*-
"""
@author: Yangminghua
"""
from datetime import datetime
import json
from flask import request, abort, url_for, render_template, flash
from flask.ext.babel import _
from werkzeug.utils import redirect
from wtforms import Form, IntegerField, validators, HiddenField
from lite_mms.portal.cargo import cargo_page
from lite_mms.utilities import decorators, Pagination, do_commit
from lite_mms import constants
from lite_mms.basemain import nav_bar


@cargo_page.route('/')
def index():
    return redirect(url_for("cargo.unload_session_list"))


@cargo_page.route("/unload-session-list")
@decorators.templated("cargo/unload-session-list.html")
@decorators.nav_bar_set
def unload_session_list():
    page = request.args.get("page", 1, type=int)
    import lite_mms.apis as apis

    sessions, total_cnt = apis.cargo.get_unload_session_list(
        (page - 1) * constants.UNLOAD_SESSION_PER_PAGE,
        constants.UNLOAD_SESSION_PER_PAGE)
    pagination = Pagination(page, constants.UNLOAD_SESSION_PER_PAGE, total_cnt)
    order_types = apis.order.get_order_type_list()
    return dict(titlename=u"卸货会话列表", sessions=sessions, pagination=pagination,
                order_types=order_types)


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
                    unload_session.update(finish_time=None)
                    flash(u"重新打开卸货会话%d成功！" % unload_session.id)
                else:
                    return _(u"该会话不能重新打开"), 403
            elif request.form.get("method") == "finish":
                if unload_session.closeable:
                    unload_session.update(finish_time=datetime.now())
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
        class _ValidationForm(Form):
            weight = IntegerField('weight', [validators.required()])
            product = IntegerField('product')
            url = HiddenField("url")

        form = _ValidationForm(request.form)
        if form.validate():
            task = apis.cargo.get_unload_task(id_)
            if not task:
                abort(404)
            session = apis.cargo.get_unload_session(session_id=task.session_id)
            if not session:
                abort(404)

            weight = task.last_weight - form.weight.data
            if weight < 0:
                abort(500)
            task.update(weight=weight, product_id=form.product.data)
            url = form.url.data or url_for("cargo.unload_session",
                                           id_=task.session_id, _method="GET")
            return redirect(url)
        else:
            abort(403)


@cargo_page.route("/goods-receipt/", methods=["GET", "POST"])
@cargo_page.route("/goods-receipt/<int:id_>")
@decorators.templated("cargo/goods-receipt.html")
@decorators.nav_bar_set
def goods_receipt(id_=None):
    from lite_mms import apis

    if request.method == "GET":
        receipt = apis.cargo.get_goods_receipt(id_)
        if not receipt:
            abort(404)
        return dict(receipt=receipt, titlename=u"收货单详情",
                    product_types=apis.product.get_product_types(),
                    products=json.dumps(apis.product.get_products()))
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
    if not receipt:
        abort(404)
    return {"receipt": receipt}
