from flask import Blueprint

cargo_ws = Blueprint("cargo_ws", __name__, static_folder="static", 
    template_folder="templates")

from lite_mms.portal.cargo_ws import webservices
