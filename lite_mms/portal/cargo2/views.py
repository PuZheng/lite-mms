# -*- coding: utf-8 -*-
import json
from flask import request, render_template, redirect, abort
from flask.ext.databrowser import ModelView
from flask.ext.databrowser.column_spec import InputColumnSpec, ColumnSpec, PlaceHolderColumnSpec, ListColumnSpec
from wtforms import Form, IntegerField, validators, ValidationError
from sqlalchemy.orm.exc import NoResultFound
from flask.ext.databrowser import ModelView
from flask.ext.databrowser.column_spec import InputColumnSpec, ColumnSpec

from lite_mms.basemain import app, data_browser, nav_bar
from lite_mms.permissions import CargoClerkPermission,AdminPermission
from lite_mms import apis
from lite_mms.apis import wraps
from lite_mms.models import UnloadSession, Plate, GoodsReceipt, Customer, UnloadTask, Product
from lite_mms.constants import cargo as cargo_const
from lite_mms.utilities import dictview, decorators
from lite_mms.portal.cargo2 import cargo2_page, fsm

@cargo2_page.route("/goods-receipt", methods=["POST", "GET"])
def goods_receipt():
    pass

g_status_desc = {
    cargo_const.STATUS_LOADING: u"正在卸货",
    cargo_const.STATUS_WEIGHING: u"等待称重",
    cargo_const.STATUS_CLOSED: u"关闭",
    cargo_const.STATUS_DISMISSED: u"取消",
}


class UnloadSessionModelView(ModelView):

    list_template = "cargo2/unload-session-list.haml"

    as_radio_group = True
    can_batchly_edit = False

    __list_columns__ = ["id", "plate", "create_time", "finish_time", "with_person", "status", "goods_receipt_list"]

    __column_labels__ = {"id": u"编号", "plate": u"车辆", "create_time": u"创建时间", "finish_time": u"结束时间", 
                         "with_person": u"驾驶室", "status": u"状态", "goods_receipt_list": u"收货单", "gross_weight": u"净重"}

    def goods_receipt_list_formatter(v, obj):
        ret = u'应建'
        if obj.customer_list:
            import cgi
            customer_list = []
            for customer in obj.customer_list:
                customer_list.append(dict(id=customer.id, name=customer.name))
            created_customers = set(gr.customer.name for gr in obj.goods_receipt_list)
            for customer in customer_list:
                customer["created"] = customer["name"] in created_customers
            content = render_template("cargo2/customer-list-popover.html", customer_list=customer_list, unload_session=obj)
            content = cgi.escape(content)
            ret += u'<a href="#" class="customer-list" data-title="客户列表" data-html="true" data-toggle="popover" data-content="%s">%d</a>' % (content, len(obj.customer_list))
        else:
            ret += '0'
        
        ret += u' - 实建'
        if v:
            # TODO compose goods receipt
            content = ""
            ret += '<a href="#" class="goods-receipt-list" data-toggle="popover" data-content="%s">%d</a>' % (content, len(v))
        else:
            ret += '0'

        return ret

    __column_formatters__ = {"create_time": lambda v, obj: v.strftime("%m-%d %H") + u"点",
                             "finish_time": lambda v, obj: v.strftime("%m-%d %H") + u"点" if v else "--",
                             "with_person": lambda v, obj: u'有人' if v else u'无人', 
                             "status": lambda v, obj: g_status_desc[v],
                             "goods_receipt_list": goods_receipt_list_formatter,
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
        from lite_mms.portal.cargo2.actions import MyDeleteAction, CloseAction, OpenAction
        if model == None: # for list
            return [MyDeleteAction(u"删除", CargoClerkPermission), CloseAction(u"关闭"), OpenAction(u"打开")]
        else:
            if model.status in [cargo_const.STATUS_CLOSED, cargo_const.STATUS_DISMISSED]:
                return [MyDeleteAction(u"删除", CargoClerkPermission), OpenAction(u"打开")]
            else:
                return [MyDeleteAction(u"删除", CargoClerkPermission), CloseAction(u"关闭")]

    # ================= FORM PART ============================
    __create_columns__ = ["plate", InputColumnSpec("with_person", label=u"驾驶室是否有人"), "gross_weight"]
    def format_log(logs, obj):
        for log in logs:
            if log.obj_cls == "UnloadSession":
                model = u"卸货会话"
            elif log.obj_cls == "UnloadTask":
                model = u"卸货任务"
            else:
                continue
            if log.action == u"create":
                yield u"[%s]: 用户%s创建了本卸货会话" % (log.create_time.strftime("%y年%m月%d日 %H点%M分").decode("utf-8"), log.actor.username)
            else: # {u"关闭", u"打开"}:
                if log.action ==  u"update":
                    log.action = u"编辑"
                s = u"[%s]: 用户%s对<i>%s</i>(%s)执行了[%s]操作" % (log.create_time.strftime("%y年%m月%d日 %H点%M分").decode("utf-8"), log.actor.username, model, log.obj, log.action)
                if log.message:
                    s += " - " + log.message
                yield s

    __form_columns__ = ["plate", 
                        InputColumnSpec("with_person", label=u"驾驶室是否有人"),
                        #InputColumnSpec("with_person", label=u"驾驶室是否有人", formatter=lambda v, obj: '<strong>' + (u'有人' if v else u'无人') + '</strong>', 
                                   #css_class="input-small uneditable-input"), 
                        ColumnSpec("status", label=u"状态", formatter=lambda v, obj: '<strong>' + g_status_desc[v] + '</strong>', 
                                   css_class="input-small uneditable-input"), 
                        InputColumnSpec("create_time", label=u"创建时间", read_only=True),
                        PlaceHolderColumnSpec(col_name="task_list", label=u"卸货任务", template_fname="cargo2/unload-task-list-snippet.haml"), 
                        ListColumnSpec(col_name="log_list", label=u"日志", formatter=format_log),
                        ]

unload_session_model_view = UnloadSessionModelView(UnloadSession, u"卸货会话")

class GoodsReceiptView(ModelView):

    def create_view(self):
        unload_session_id = request.args.get("unload_session_id")
        customer_id = request.args.get("customer_id")

        class _Form(Form):
            def validate_unload_session_id(self, field):
                try:
                    self.unload_session = wraps(UnloadSession.query.filter(UnloadSession.id==field.data).one())
                except NoResultFound:
                    raise ValidationError(u"没有id为%d的卸货会话" % field.data)
                if self.unload_session.status != cargo_const.STATUS_CLOSED:
                    raise ValidationError(u"卸货会话%d尚未结束，不能生成收货单" % field.data)


            def validate_customer_id(self, field):
                try:
                    self.customer = wraps(Customer.query.filter(Customer.id==field.data).one())
                except NoResultFound:
                    raise ValidationError(u"没有id为%d的客户" % field.data)
                if self.customer.id not in set(customer.id for customer in self.unload_session.customer_list):
                    raise ValidationError(u"卸货会话%s没有客户%s" % (unicode(self.unload_session), unicode(self.customer)))
                    
            unload_session_id = IntegerField("unload_session_id", [validators.DataRequired()])
            customer_id = IntegerField("customer_id", [validators.DataRequired()])

        form = _Form(request.args)
        if not form.validate():
            return render_template("validation-error.html", hint_message=form.errors.values()[0][0], 
                                   back_url=unload_session_model_view.url_for_list(),
                                   nav_bar=nav_bar), 403
        return render_template("cargo2/goods-receipt.haml", form=form, nav_bar=nav_bar, purl=unload_session_model_view.url_for_list())

goods_receipt_model_view = GoodsReceiptView(GoodsReceipt, u"收货单")

class plateModelView(ModelView):
    
    can_edit = False
    
    __create_columns__ = ["plate"]

plate_model_view = plateModelView(Plate, u"车辆")

@cargo2_page.route("/weigh-unload-task/<int:id_>", methods=["GET", "POST"])
@decorators.templated("/cargo2/unload-task.haml")
def weigh_unload_task(id_):
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
            fsm.fsm.next(cargo_const.ACT_WEIGH, current_user)
            return redirect(unload_session_model_view.url_for_object(model=task.unload_session.model))
        else:
            return render_template("validation-error.html", errors=form.errors,
                                   back_url=unload_session_model_view.url_for_object(model=task.unload_session.model),
                                   nav_bar=nav_bar), 403

class UnloadTaskModelView(ModelView):

    can_edit = True 

    __form_columns__ = ["harbor", "customer", "weight", InputColumnSpec("product", group_by=Product.product_type, label=u"产品"), "is_last"]
    __column_labels__ = {
        "harbor": u"装卸点", 
        "customer": u"客户",
        "weight": u"重量(公斤)",
        "is_last": u"是否全部卸货",
    }

unload_task_model_view = UnloadTaskModelView(UnloadTask, u"卸货任务")
