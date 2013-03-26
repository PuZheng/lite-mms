from flask import Blueprint

delivery_ws = Blueprint("delivery_ws", __name__, static_folder="static",
                        template_folder="templates")

from lite_mms.portal.delivery_ws import webservices

