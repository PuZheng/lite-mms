from flask import Blueprint

manufacture_ws = Blueprint("manufacture_ws", __name__, static_folder="static",
                             template_folder="templates")

from lite_mms.portal.manufacture_ws import webservices

