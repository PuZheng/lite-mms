# -*- coding: UTF-8 -*-
from sqlalchemy import func

def get_query(db, model_map):
    Team = model_map['Team']
    WorkCommand = model_map['WorkCommand']
    Department = model_map['Department']
    return db.session.query(Team.name.label(u'班组'), 
                            Department.name.label(u'车间'), 
                            func.avg(WorkCommand.processed_weight).label(u'总工作量')).group_by(WorkCommand.team_id).join(WorkCommand).join(Department).filter(WorkCommand.completed_time!=None)
