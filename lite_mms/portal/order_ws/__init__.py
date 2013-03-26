from flask import Blueprint

order_ws = Blueprint("order_ws", __name__, static_folder="static",
    template_folder="templates")

from lite_mms.portal.order_ws import webservices

