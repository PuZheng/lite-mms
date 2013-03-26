# -*- coding: utf-8 -*-
"""
@author: Yangminghua
"""
from datetime import datetime
import json
from flask import request, abort, url_for, render_template, flash
from flask.ext.login import current_user
from werkzeug.utils import redirect
from wtforms import Form, IntegerField, validators
from lite_mms.portal.cargo import cargo_page
from lite_mms.utilities import decorators, Pagination, do_commit
import lite_mms.constants as constants


@cargo_page.route('/')
def index():
    return redirect(url_for("cargo.unload_session_list"))


@cargo_page.route("/unload-session-list")
@decorators.templated("/cargo/unload-session-list.html")
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


@cargo_page.route("/unload-session")
@decorators.templated("/cargo/unload-session.html")
@decorators.nav_bar_set
def session_detail():
    from lite_mms import apis

    unload_session = apis.cargo.get_unload_session(
        session_id=request.args.get('id', type=int))
    if not unload_session:
        abort(404)
    return dict(unload_session=unload_session, titlename=u"卸货会话详情",
        order_types=apis.order.get_order_type_list())

@cargo_page.route("/unload-session-add", methods=['POST', 'GET'])
@decorators.templated("/cargo/unload-session-add.html")
@decorators.nav_bar_set
def session_add():
    from lite_mms import apis

    if request.method == 'POST':
        with_person = request.form.get("with_person", type=bool) or False
        return redirect(url_for('cargo.session_detail',
            id=apis.cargo.new_unload_session(
                request.form['plateNumber'],
                request.form['grossWeight'],
                with_person).id))
    else:
        working_list = []
        working_list.extend(apis.plate.get_plate_list("unloading"))
        working_list.extend(apis.plate.get_plate_list("delivering"))
        return dict(titlename=u"新增卸货会话",
            plateNumbers=apis.plate.get_plate_list(),
            working_plate_list=json.dumps(working_list)
        )

@cargo_page.route("/unload-session-delete", methods=['POST'])
def session_delete():
    from lite_mms import apis
    unload_session = apis.cargo.get_unload_session(request.form['id'])
    if unload_session.deleteable:
        do_commit(unload_session, action="delete")
        return redirect(url_for("cargo.unload_session_list"))
    else:
        return u'该卸货会话已经有卸货任务不能删除！', 403


@cargo_page.route("/unload-task", methods=["GET", "POST"])
@decorators.templated("/cargo/unload-task.html")
@decorators.nav_bar_set
def unload_task():
    from lite_mms import apis

    if request.method == 'GET':
        task = apis.cargo.get_unload_task(request.args.get('id', type=int))
        if not task:
            abort(404)
        return dict(plate=task.unload_session.plate, task=task,
            product_types=apis.product.get_product_types(),
            products=json.dumps(apis.product.get_products()))
    else: # POST
        class _ValidationForm(Form):
            task_id = IntegerField('task_id', [validators.required()])
            weight = IntegerField('weight', [validators.required()])
            product = IntegerField('product')


        form = _ValidationForm(request.form)
        if form.validate():
            task = apis.cargo.get_unload_task(form.task_id.data)
            if not task:
                abort(404)
            session = apis.cargo.get_unload_session(session_id=task.session_id)
            if not session:
                abort(404)

            weight = task.last_weight - form.weight.data
            if weight < 0:
                abort(500)
            task.update(weight=weight, product_id=form.product.data)

            return redirect(url_for(".session_detail", id=task.session_id))
        else:
            abort(403)


@cargo_page.route("/goods-receipt", methods=["GET", "POST"])
@decorators.templated("/cargo/goods-receipt.html")
@decorators.nav_bar_set
def goods_receipt():
    from lite_mms import apis

    if request.method == "GET":
        receipt = apis.cargo.get_goods_receipt(
            request.args.get("id", type=int))
        if not receipt:
            abort(404)
        return dict(receipt=receipt,
            product_types=apis.product.get_product_types(),
            products=json.dumps(apis.product.get_products()))
    else:
        class _ValidationForm(Form):
            customer = IntegerField('customer', [validators.required()])
            order_type = IntegerField('order_type', [validators.required()])
            unload_session_id = IntegerField('unload_session_id',
                [validators.required()])


        form = _ValidationForm(request.form)
        if form.validate():
            receipt = apis.cargo.new_goods_receipt(form.customer.data,
                form.unload_session_id.data)
            apis.order.new_order(order_type=form.order_type.data,
                goods_receipt_id=receipt.id,
                creator_id=current_user.id)
            return redirect(url_for("cargo.goods_receipt", id=receipt.id))
        else:
            return render_template("result.html",
                error_content=str(form.errors))


@cargo_page.route("/session-finish", methods=["POST"])
@decorators.nav_bar_set
def session_finish():
    from lite_mms import apis

    us = apis.cargo.get_unload_session(request.form['id'])
    if us.closeable:
        us.update(finish_time=datetime.now())
        return redirect(url_for('cargo.session_detail', id=request.form["id"]))
    else:
        return render_template("result.html", error_content=u"该状态的会话不能结束")


@cargo_page.route("/session-reopen", methods=["POST"])
@decorators.nav_bar_set
def session_reopen():
    from lite_mms import apis

    us = apis.cargo.get_unload_session(request.form["id"])
    if us.closed:
        us.update(finish_time=None)
        return redirect(url_for('cargo.session_detail', id=request.form["id"]))
    else:
        return render_template("result.html", error_content=u"该状态的会话不能重新打开")


