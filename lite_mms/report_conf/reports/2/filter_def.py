# -*- coding: UTF-8 -*-
from datetime import datetime, timedelta
import calendar

def get_filter(db, model_map):
    today = datetime.today()
    first_day_of_next_month = datetime(today.year, today.month, 1) + timedelta(days=calendar.monthrange(today.year, today.month)[1])
    WorkCommand = model_map['WorkCommand']
    return WorkCommand.completed_time < first_day_of_next_month
