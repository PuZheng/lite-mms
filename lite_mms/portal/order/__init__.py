from flask import Blueprint
from flask.ext.principal import PermissionDenied
from lite_mms.permissions import CargoClerkPermission,AdminPermission

order_page = Blueprint("order", __name__, static_folder="static",
    template_folder="templates")

@order_page.before_request
def _():
    if not CargoClerkPermission.can() and not AdminPermission.can():
        raise PermissionDenied

from lite_mms.portal.order import ajax, views
