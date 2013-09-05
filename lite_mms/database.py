# -*- coding: utf-8 -*-
from lite_mms.basemain import app
app.config["SQLALCHEMY_DATABASE_URI"] = app.config["DBSTR"]
from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

from CodernityDB.database import Database

codernity_db = Database(app.config['CODERNITY_DATABASE_PATH'])
if codernity_db.exists():
    codernity_db.open()
    codernity_db.reindex()
else:
    codernity_db.create()
    from lite_task_flow.indexes import add_index
    add_index(codernity_db)
    from lite_mms.indexes import TaskWithGroup
    codernity_db.add_index(TaskWithGroup(codernity_db.path, TaskWithGroup.TAG))

app.config["MONGODB_DB"] = "localhost"

def init_db():
    # 必须要import models, 否则不会建立表
    from lite_mms import models
    db.create_all()

