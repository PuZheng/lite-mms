# -*- coding: UTF-8 -*-
from sqlalchemy import func

def get_query(db, model_map):
    Team = model_map['Team']
    WorkCommand = model_map['WorkCommand']
    return db.session.query(Team.name.label(u'班组'), Team.department.name.label(u'车间'), func.sum(WorkCommand.processed_weight).label(u'总计完成重量')).join(WorkCommand).filter(WorkCommand).group_by(WorkCommand.team_id)
