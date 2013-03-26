from flask import Blueprint

delivery_page = Blueprint("delivery", __name__, static_folder="static", 
    template_folder="templates")

from lite_mms.portal.delivery import views, ajax
