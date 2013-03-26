# -*- coding: utf-8 -*-
from lite_mms.basemain import app
app.config["SQLALCHEMY_DATABASE_URI"] = app.config["DBSTR"]
from flask.ext.sqlalchemy import SQLAlchemy
app.config["SQLALCHEMY_ECHO"] = False
db = SQLAlchemy(app)

def init_db():
    # 必须要import models, 否则不会建立表
    from lite_mms import models
    db.create_all()
