# -*- coding: UTF-8 -*-

from datetime import datetime

def get_filter(db, model_map):
    today = datetime.today()
    first_day_of_this_month = datetime(today.year, today.month, 1)
    return WorkCommand.compeleted_time < first_day_of_this_month

