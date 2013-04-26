# -*- coding: utf-8 -*-
from flask.ext.mongoengine import MongoEngine
from lite_mms.basemain import app
app.config["SQLALCHEMY_DATABASE_URI"] = app.config["DBSTR"]
from flask.ext.sqlalchemy import SQLAlchemy
app.config["SQLALCHEMY_ECHO"] = False
db = SQLAlchemy(app)

app.config["MONGODB_DB"] = "localhost"
mongo = MongoEngine()

try:
    mongo.init_app(app)
except:
    pass

def init_db():
    # 必须要import models, 否则不会建立表
    from lite_mms import models
    db.create_all()
