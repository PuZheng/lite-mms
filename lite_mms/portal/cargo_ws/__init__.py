from flask import Blueprint

cargo_ws = Blueprint("cargo_ws", __name__, static_folder="static", 
    template_folder="templates")

from lite_mms.apis.auth import load_user_from_token
cargo_ws.before_request(load_user_from_token)

from lite_mms.portal.cargo_ws import webservices
