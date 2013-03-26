from flask import Blueprint
from lite_mms.permissions import CargoClerkPermission

cargo_page = Blueprint("cargo", __name__, static_folder="static", 
    template_folder="templates")


@cargo_page.before_request
def _():
    with CargoClerkPermission.require():
        pass

from lite_mms.portal.cargo import views, ajax
