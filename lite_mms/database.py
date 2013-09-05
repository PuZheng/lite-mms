# -*- coding: utf-8 -*-
from lite_mms.basemain import app
app.config["SQLALCHEMY_DATABASE_URI"] = app.config["DBSTR"]
from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

from CodernityDB.database import Database

codernity_db = Database(app.config['CODERNITY_DATABASE_PATH'])
codernity_db.open()
codernity_db.reindex()

app.config["MONGODB_DB"] = "localhost"

def init_db():
    # 必须要import models, 否则不会建立表
    from lite_mms import models
    db.create_all()

