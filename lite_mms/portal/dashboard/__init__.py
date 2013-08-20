#-*- coding:utf-8 -*-
from flask import Blueprint, render_template
from lite_mms.utilities.decorators import templated, nav_bar_set

dashboard = Blueprint(name="dashboard", import_name=__name__, static_folder="static", template_folder="templates")


class Widget(object):
    def __init__(self, name, description, template_file=None):
        self.name = name
        self.description = description
        self.template_file = template_file or "dashboard/widget.html"

    def template(self):
        return render_template(self.template_file, widget=self)

    @property
    def data(self):
        return self.query()

    def query(self):
        return NotImplemented


DASHBOARD_WIDGETS = []
from . import widgets


def _get_widgets():
    if not DASHBOARD_WIDGETS:
        raise NotImplementedError
    return DASHBOARD_WIDGETS


@dashboard.route("/")
@templated("dashboard/index.html")
@nav_bar_set
def index():
    return {"titlename": u"仪表盘", "widgets": _get_widgets()}


