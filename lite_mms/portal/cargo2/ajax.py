# -*- coding: UTF-8 -*-
from flask import request

from lite_mms.constants import cargo as cargo_const
from lite_mms.portal.cargo2 import cargo2_page, fsm
from lite_mms.utilities import do_commit, get_or_404
from lite_mms.models import UnloadTask
from lite_mms.utilities.decorators import ajax_call

@cargo2_page.route("/ajax/unload-task/<int:id_>", methods=["POST"])
@ajax_call
def unload_task(id_):
    if request.form["action"] == "delete":
        ut = get_or_404(UnloadTask, id_)
        if ut.weight != 0:
            return "已经称重的卸货任务不能删除"
        do_commit(ut.model, "delete")
    from portal.cargo2.fsm import fsm
    fsm.reset_obj(ut.unload_session) 
    from flask.ext.login import current_user
    fsm.next(cargo_const.ACT_WEIGH, current_user.username) 
    return "success"
