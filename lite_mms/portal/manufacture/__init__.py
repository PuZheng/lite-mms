from flask import Blueprint, request
from lite_mms.permissions.work_command import view_work_command

manufacture_page = Blueprint("manufacture", __name__, static_folder="static",
                             template_folder="templates")

@manufacture_page.before_request
def _():
    pass
    # TODO need fine-grined permissions here
    #if not request.path.startswith("/manufacture/work-command/"):
        #with view_work_command.require():
            #pass

from lite_mms.portal.manufacture import views, ajax
