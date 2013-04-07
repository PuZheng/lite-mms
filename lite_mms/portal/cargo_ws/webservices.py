from datetime import datetime
import json
import os.path
from flask import request
from wtforms import validators, Form, IntegerField, StringField
from lite_mms.portal.cargo_ws import cargo_ws
from lite_mms.utilities.decorators import webservice_call
from lite_mms.basemain import app


@cargo_ws.route("/unload-session-list", methods=["GET"])
@webservice_call("json")
def unload_session_list():
    """
    get **unfinished** unload sessions from database, accept no arguments
    """
    import lite_mms.apis as apis

    unload_sessions, total_cnt = apis.cargo.get_unload_session_list(
        unfinished_only=True)
    data = [{'plateNumber': us.plate, 'sessionID': us.id,
             'isLocked': int(us.is_locked)} for us in
            unload_sessions]
    return json.dumps(dict(data=data, total_cnt=total_cnt))


@cargo_ws.route("/harbour-list", methods=["GET"])
@cargo_ws.route("/harbor-list", methods=["GET"])
def harbour_list():
    from lite_mms.apis.harbor import get_harbor_list

    return json.dumps([harbor.name for harbor in get_harbor_list()])


@cargo_ws.route("/unload-task", methods=["POST"])
def unload_task():
    class _ValidationForm(Form):
        session_id = IntegerField("session id", [validators.DataRequired()])
        harbour = StringField("harbour", [validators.DataRequired()])
        customer_id = IntegerField("customer id", [validators.DataRequired()])
        is_finished = IntegerField("is finished", default=0)
        actor_id = IntegerField("actor id", [validators.DataRequired()])

    try:
        f = request.files.values()[0]
    except IndexError:
        f = None
    pic_path = ""
    if f:
        pic_path = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.jpg")
        f.save(os.path.join(app.config["UPLOAD_FOLDER"], pic_path))
    form = _ValidationForm(request.args)
    if not form.validate():
        return json.dumps(form.errors), 403
    import lite_mms.apis as apis

    try:
        new_task = apis.cargo.new_unload_task(session_id=form.session_id.data,
                                              harbor=form.harbour.data,
                                              customer_id=form.customer_id.data,
                                              creator_id=form.actor_id.data,
                                              pic_path=pic_path, is_last=form.is_finished.data)
        if form.is_finished.data:
            from lite_mms.portal.cargo2.fsm import fsm
            from lite_mms.constants import cargo as cargo_const
            fsm.reset_obj(new_task.unload_session)
            fsm.next(cargo_const.ACT_CLOSE, new_task.creator)
    except ValueError, e:
        return unicode(e), 403
    return json.dumps(new_task.id)

if __name__ == "__main__":
    try:
        # pylint: disable=F0401,W0611
        import lite_mms.instance.portal.cargo.webservices_main
        # pylint: enable=F0401,W0611
    except ImportError:
        print "can't import webservices_main"
        import traceback

        traceback.print_exc()
