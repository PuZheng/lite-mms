# -*- coding: utf-8 -*-
"""
@author: Yangminghua
"""
import json
from socket import error
import time
from collections import OrderedDict
from flask import request, abort, render_template, url_for, flash
from lite_mms.utilities import _, do_commit
from werkzeug.utils import redirect
from wtforms import Form, IntegerField, validators, HiddenField, TextField
from lite_mms.portal.delivery import delivery_page, consignment_page
from lite_mms.permissions import CargoClerkPermission, AccountantPermission
from lite_mms.utilities import decorators, Pagination
from lite_mms.database import db
import lite_mms.constants as constants
import lite_mms.apis as apis


@delivery_page.route('/')
def index():
    return redirect(url_for("delivery.session_list"))


@delivery_page.route("/delivery-session-list")
@CargoClerkPermission.require()
@decorators.templated("/delivery/delivery-session-list.html")
@decorators.nav_bar_set
def session_list():
    page = request.args.get("page", 1, type=int)
    page_size = constants.DELIVERY_SESSION_PER_PAGE
    import lite_mms.apis as apis

    sessions, total_cnt = apis.delivery.get_delivery_session_list(
        (page - 1) * page_size, page_size)
    pagination = Pagination(page, constants.DELIVERY_SESSION_PER_PAGE,
                            total_cnt)
    order_types = apis.order.get_order_type_list()
    return dict(titlename=u"发货会话列表", sessions=sessions, pagination=pagination,
                order_types=order_types)


@delivery_page.route("/delivery-session", methods=["GET", "POST"])
@delivery_page.route("/delivery-session/<int:id_>", methods=["GET", "POST"])
@CargoClerkPermission.require()
@decorators.templated("/delivery/delivery-session.html")
@decorators.nav_bar_set
def delivery_session(id_=None):
    import lite_mms.apis as apis

    if request.method == "GET":
        if id_:
            delivery_session = apis.delivery.get_delivery_session(id_)
            if delivery_session is None:
                abort(404)
            return dict(delivery_session=delivery_session, titlename=u"发货会话详情")
        else:
            working_list = []
            working_list.extend(apis.plate.get_plate_list("unloading"))
            working_list.extend(apis.plate.get_plate_list("delivering"))
            return render_template("delivery/delivery-session-add.html",
                                   titlename=u"新增发货会话",
                                   plateNumbers=apis.plate.get_plate_list(),
                                   working_plate_list=json.dumps(working_list)
            )
    else:
        if id_:
            ds = apis.delivery.get_delivery_session(id_)
            if request.form.get("method") == "reopen":
                if ds.reopen():
                    flash(u"重新打开发货会话%d成功" % ds.id)
                else:
                    return u"该状态的会话不能重新打开", 403
            elif request.form.get("method") == "delete":
                if ds.deleteable:
                    do_commit(ds, action="delete")
                    flash(u"删除发货会话%d成功" % ds.id)
                    return redirect(request.form.get("url") or url_for(
                        "delivery.session_list"))
                else:
                    return u'该发货会话已经装过货，不能删除', 403
            elif request.form.get("method") == "finish":
                if ds.finish():
                    flash(u"关闭发货会话%d成功" % ds.id)
                else:
                    return u"该状态的会话不能关闭", 403
            return redirect(
                url_for('delivery.delivery_session', id_=ds.id, _method="GET",
                        url=request.form.get("url")))
        else:
            with_person = request.form.get("with_person", type=bool) or False
            ds = apis.delivery.new_delivery_session(
                request.form['plateNumber'],
                request.form['tare'],
                with_person)
            store_bill_id_list = request.form.getlist('store_bill_id',
                                                      type=int)
            if store_bill_id_list:
                ds.add_store_bill_list(store_bill_id_list)
            return redirect(
                url_for('delivery.delivery_session', id_=ds.id, _method="GET"))


@delivery_page.route("/store-bill-list/", methods=['POST', 'GET'])
@delivery_page.route("/store-bill-list/<int:delivery_session_id>",
                     methods=['POST', 'GET'])
@CargoClerkPermission.require()
@decorators.templated("/delivery/store-bill-list.html")
@decorators.nav_bar_set
def store_bill_add(delivery_session_id=None):
    import lite_mms.apis as apis

    if request.method == 'POST':
        store_bill_id_list = request.form.getlist('store_bill_id', type=int)
        if delivery_session_id:
            delivery_session = apis.delivery.get_delivery_session(
                delivery_session_id)
            delivery_session.add_store_bill_list(store_bill_id_list)
            return redirect(
                request.form.get("url") or url_for('delivery.delivery_session',
                                                   id_=delivery_session_id))
        else:
            return redirect(url_for('delivery.delivery_session',
                                    store_bill_id=store_bill_id_list))
    else:
        customers = apis.delivery.get_store_bill_customer_list()
        d = dict(titlename=u'选择仓单', customer_list=customers)
        if delivery_session_id:
            d["delivery_session_id"] = delivery_session_id
        return d


@delivery_page.route("/delivery-task/<int:id_>", methods=['GET', 'POST'])
@CargoClerkPermission.require()
@decorators.templated("/delivery/delivery-task.html")
@decorators.nav_bar_set
def delivery_task(id_):
    import lite_mms.apis as apis

    task = apis.delivery.get_delivery_task(id_)
    if not task:
        abort(404)
    if request.method == "GET":
        return dict(task=task, titlename=u'装货任务详情')
    else:
        current_weight = request.form.get('weight', type=int)
        weight = current_weight - task.last_weight
        result = task.update(weight=weight)
        if not result:
            abort(500)
        return redirect(
            request.form.get("url") or url_for("delivery.delivery_session",
                                               id_=task.delivery_session_id))


@delivery_page.route("/consignment/", methods=["POST"])
@delivery_page.route("/consignment/<int:id_>", methods=["GET", "POST"])
@decorators.templated("/delivery/consignment.html")
@decorators.nav_bar_set
def consignment(id_=None):
    import lite_mms.apis as apis
    from flask.ext.principal import Permission

    Permission.union(CargoClerkPermission, AccountantPermission).test()
    if request.method == "GET":
        cons = apis.delivery.get_consignment(id_)
        team_list = apis.manufacture.get_team_list()
        if not cons:
            abort(404)
        else:
            return dict(plate=cons.plate, consignment=cons, titlename=u'发货单详情',
                        team_list=team_list)
    else:
        if id_:
            cons = apis.delivery.get_consignment(id_)
            if not cons:
                abort(404)
            params = {}
            if request.form:
                params["pay_in_cash"] = request.form.get("pay_in_cash",
                                                         type=int)
                params["notes"] = request.form.get("notes")
                try:
                    cons.update(cons.id, **params)
                    if CargoClerkPermission.can():
                        flash(u"更新成功")
                except ValueError, e:
                    flash(unicode(e.message), "error")
            else:
                if cons.pay_in_cash:
                    cons.paid()
                    flash(u"支付成功")
            return redirect(url_for("delivery.consignment", id_=id_,
                                    url=request.form.get("url")))
        else:
            class _ValidationForm(Form):
                customer = IntegerField('customer', [validators.required()])
                pay_mod = IntegerField('pay_mod', [validators.required()])
                delivery_session_id = IntegerField('delivery_session_id',
                                                   [validators.required()])
                url = HiddenField("url")

            form = _ValidationForm(request.form)
            delivery_session_id = form.delivery_session_id.data
            customer_id = form.customer.data
            pay_in_cash = True if form.pay_mod.data else False
            cons = apis.delivery.new_consignment(
                customer_id=customer_id,
                delivery_session_id=delivery_session_id,
                pay_in_cash=pay_in_cash)

            return redirect(url_for("delivery.consignment", id_=cons.id,
                                    url=form.url.data))


@delivery_page.route("/consignment_preview/<int:id_>", methods=["GET"])
@decorators.templated("/delivery/consignment-preview.html")
@decorators.nav_bar_set
def consignment_preview(id_):
    from flask.ext.principal import Permission

    Permission.union(CargoClerkPermission, AccountantPermission).test()

    import lite_mms.apis as apis

    cons = apis.delivery.get_consignment(id_)
    if not cons:
        abort(404)
    else:
        PER_PAGE  = apis.config.get("print_count_per_page", 5.0, type=float)
        import math
        pages = int(math.ceil(len(cons.product_list) / PER_PAGE))
        return dict(plate=cons.plate, consignment=cons, titlename=u'发货单详情',
                    pages=pages, per_page=PER_PAGE)


@delivery_page.route("/store-bill/<int:id_>", methods=["GET"])
@CargoClerkPermission.require()
@decorators.templated("store/store-bill.html")
@decorators.nav_bar_set
def store_bill(id_):
    import lite_mms.apis as apis

    store_bill = apis.delivery.get_store_bill(id_)
    if store_bill:
        return dict(titlename=u'仓单详情', store_bill=store_bill,
                    harbors=apis.harbor.get_harbor_list())
    else:
        return _("没有此仓单%(id)d" % {"id": id_}), 404


@delivery_page.route("/consignment-list")
@AccountantPermission.require()
@decorators.templated("/delivery/consignment-list.html")
@decorators.nav_bar_set
def consignment_list():
    import lite_mms.apis as apis

    is_paid = request.args.get("is_paid", 0, type=int)
    customer_id = request.args.get("customer_id", 0, type=int)
    customer = apis.customer.get_customer(customer_id)
    page = request.args.get("page", 1, type=int)
    page_size = constants.DELIVERY_SESSION_PER_PAGE

    cons, total_cnt = apis.delivery.get_consignment_list(pay_in_cash=True,
                                                         is_paid=is_paid,
                                                         customer_id=customer_id,
                                                         idx=(
                                                             page - 1) * page_size,
                                                         cnt=page_size)


    pagination = Pagination(page, constants.DELIVERY_SESSION_PER_PAGE,
                            total_cnt)
    return dict(titlename=u'发货单列表', consignment_list=cons,
                customer_list=apis.delivery.ConsignmentWrapper
                .get_customer_list(),
                customer=customer, pagination=pagination)

@delivery_page.route("/product/<int:id_>", methods=["POST", "GET"])
@decorators.templated("delivery/consignment-product.html")
@decorators.nav_bar_set
def consignment_product(id_):
    from flask.ext.principal import Permission

    Permission.union(CargoClerkPermission, AccountantPermission).test()

    import lite_mms.apis as apis

    current_product = apis.delivery.ConsignmentProductWrapper.get_product(id_)
    if current_product:
        if request.method == "GET":
            return dict(current=current_product,
                        product_types=apis.product.get_product_types(),
                        products=json.dumps(apis.product.get_products()),
                        team_list=apis.manufacture.get_team_list(),
                        titlename=u"发货产品详情")
        else:
            class ProductForm(Form):
                team_id = IntegerField("team_id")
                product_id = IntegerField("product_id")
                weight = IntegerField("weight")
                returned_weight = IntegerField("returned_weight")
                spec = TextField("spec")
                type = TextField("type")
                unit = TextField("unit")

            form = ProductForm(request.form)
            current_product.update(**form.data)
            return redirect(
                request.form.get("url") or url_for("delivery.consignment",
                                                   id_=current_product.consignment.id))
    else:
        return _(u"没有该产品编号:%d" + id_), 404


@consignment_page.route("/")
def index():
    return redirect(consigment_model_view.url_for_list(order_by="create_time", desc=1))

from flask.ext.principal import PermissionDenied
from flask.ext.databrowser import ModelView
from flask.ext.databrowser.column_spec import ColumnSpec, InputColumnSpec, LinkColumnSpec, TableColumnSpec
from flask.ext.databrowser.action import BaseAction, ReadOnlyAction
from flask.ext.databrowser import filters
from lite_mms.models import Consignment, ConsignmentProduct, Product

class PayAction(BaseAction):

    def op(self, obj):
        obj.is_paid = True
        db.session.commit()

class PreviewConsignment(ReadOnlyAction):
    
    def op_upon_list(self, objs, model_view):
        return redirect(url_for("delivery.consignment_preview", id_=objs[0].id, url=request.url))


class ConsignmentModelView(ModelView):

    def try_create(self):
        raise PermissionDenied

    as_radio_group = True

    def get_customized_actions(self, processed_objs=None):
        ret = [PreviewConsignment(u"打印预览")]
        from lite_mms.permissions.roles import AccountantPermission
        if AccountantPermission.can() and isinstance(processed_objs, (list, tuple)):
            if any(obj.pay_in_cash and not obj.is_paid for obj in processed_objs):
                ret.append(PayAction(u"支付"))
        return ret

    def __list_filters__(self):
        from lite_mms.permissions.roles import AccountantPermission
        if AccountantPermission.can():
            return [filters.EqualTo("pay_in_cash", value=True)]
        return []
    
    def get_list_columns(self):
        return ["id", "consignment_id", "delivery_session", "actor", "create_time", "customer", "pay_in_cash",
                ColumnSpec("is_paid", formatter=lambda v, obj: u"是" if v else u"否"), ColumnSpec("notes", trunc=8)]



    __column_labels__ = {"consignment_id": u"发货单编号", "customer": u"客户", "delivery_session": u"车牌号",
                         "actor": u"发起人", "delivery_session.id": u"发货会话", "create_time": u"创建时间", "is_paid": u"是否支付",
                         "pay_in_cash": u"支付方式", "notes": u"备注"}

    __column_formatters__ = {"actor": lambda v, obj: u"--" if v is None else v,
                             "pay_in_cash": lambda v, obj: u"现金支付" if v else u"月结"}

    __column_filters__ = [filters.EqualTo("customer", name=u"是"),
                          filters.Only("is_paid", display_col_name=u"只展示未付款发货单", test=lambda col: col == False,
                                       notation=u"is_paid", default_value=False),
                          filters.Only("MSSQL_ID", display_col_name=u"只展示未导出发货单", test=lambda col: col == None,
                                       notation="is_export", default_value=False)
                          ]

    def get_form_columns(self, obj=None):
        self.__form_columns__ = OrderedDict()
        self.__form_columns__[u"发货单详情"] = [
            ColumnSpec("consignment_id"),
            ColumnSpec("actor"),
            ColumnSpec("create_time"),
            ColumnSpec("customer"),
            ColumnSpec("delivery_session"),
            ColumnSpec("notes", trunc=24),
            ColumnSpec("is_paid", formatter=lambda v, obj: u"是" if v else u"否"),
        ]
        if obj and self.preprocess(obj).measured_by_weight:
            col_specs = ["id", ColumnSpec("product", label=u"产品",
                                          formatter=lambda v, obj: unicode(v.product_type) + "-" + unicode(v)),
                         ColumnSpec("weight", label=u"重量"),
                         ColumnSpec("returned_weight",
                                    label=u"退镀重量"),
                         ColumnSpec("team", label=u"生产班组")]

        else:
            col_specs = ["id", ColumnSpec("product", label=u"产品",
                                          formatter=lambda v, obj: unicode(v.product_type) + "-" + unicode(v)),
                         ColumnSpec("weight", label=u"重量"),
                         ColumnSpec("spec", label=u"型号"),
                         ColumnSpec("type", label=u"规格"),
                         ColumnSpec("quantity", label=u"数量"),
                         ColumnSpec("unit", label=u"单位"),
                         ColumnSpec("returned_weight",
                                    label=u"退镀重量"),
                         ColumnSpec("team", label=u"生产班组")]

        self.__form_columns__[u"产品列表"] = [
                TableColumnSpec("product_list_unwrapped", label="", col_specs=col_specs,
                                sum_fields=["weight", "returned_weight"])
            ]
        return self.__form_columns__


    def preprocess(self, obj):
        return apis.delivery.ConsignmentWrapper(obj)


consigment_model_view = ConsignmentModelView(Consignment, u"发货单")


class ConsignmentProductModelView(ModelView):
    __column_labels__ = {"product": u"产品", "weight": u"净重", "returned_weight": u"退镀重量", "team": u"班组",
                         "quantity": u"数量", "unit": u"单位", "spec": u"型号", "type": u"规格"}
    
    def try_edit(self, processed_objs=None):
        from lite_mms import permissions
        permissions.CargoClerkPermission.test() 
        if processed_objs[0].consignment.MSSQL_ID is not None:
            raise PermissionDenied

    def edit_hint_message(self, obj, read_only=False):
        from lite_mms import permissions
        if not permissions.CargoClerkPermission.can():
            return u"您不能修改本发货单，因为您不是收发员"
        if obj.consignment.MSSQL_ID is not None:
            return u"您不能修改本发货单，该发货单已经插入原有系统"
        return super(ConsignmentProductModelView, self).edit_hint_message(obj, read_only)

    def get_form_columns(self, obj=None):
        #if obj and apis.delivery.ConsignmentWrapper(obj.consignment).measured_by_weight:
            #return [InputColumnSpec("product", group_by=Product.product_type), "weight", "returned_weight", "team"]
        #else:
            #return [InputColumnSpec("product", group_by=Product.product_type), "weight", "quantity", "unit", "spec",
                    #"type", "returned_weight", "team"]
        return ['unit']
        #return [InputColumnSpec("product", group_by=Product.product_type), "weight", "quantity", "unit", "spec",
                #"type", "returned_weight", "team"]

consigment_product_model_view = ConsignmentProductModelView(ConsignmentProduct, u"发货单项")
    
