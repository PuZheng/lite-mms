# -*- coding: UTF-8 -*-
from flask import request, render_template
from flask.ext.login import current_user

import lite_task_flow
from lite_task_flow import get_task, get_task_from_doc

from lite_mms.portal.task_flow import task_flow_page
from lite_mms.database import codernity_db


@task_flow_page.route('/task/<id_>', methods=['GET', 'POST'])
def task(id_):
    if request.method == 'POST':
        task = get_task(id_)
        action = request.args.get('action').lower()
        if action == 'approve':
            task.task_flow.approve(task)
        elif action == 'refuse':
            task.task_flow.refuse(task)
        return 'ok'

from lite_mms.basemain import data_browser, nav_bar

@task_flow_page.route('/task-flow-list')
def task_list():
        
    tasks = codernity_db.get_many('task_with_group', current_user.group, with_doc=True)
    tasks = [get_task_from_doc(task['doc']) for task in tasks]
    total_cnt = len(tasks)
    if request.args.get('handled_only'):
        tasks = [task for task in tasks if task.approved or task.task_flow.status != lite_task_flow.constants.TASK_FLOW_PROCESSING]
        handled_tasks_cnt = len(tasks)
        unhandled_tasks_cnt = total_cnt - handled_tasks_cnt
    else:
        tasks = [task for task in tasks if not task.approved and task.task_flow.status == lite_task_flow.constants.TASK_FLOW_PROCESSING]
        unhandled_tasks_cnt = len(tasks)
        handled_tasks_cnt = total_cnt - unhandled_tasks_cnt 
    return render_template('task-flow/task-list.html', tasks=tasks, nav_bar=nav_bar, 
                           titlename=u'工作流列表', 
                           constants=lite_task_flow.constants, 
                          handled_tasks_cnt=handled_tasks_cnt,
                          unhandled_tasks_cnt=unhandled_tasks_cnt)
