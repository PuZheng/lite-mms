#-*- coding:utf-8 -*-
from datetime import datetime
from flask.ext.login import UserMixin
from lite_todo import db


class Message(db.Document):
    message = db.StringField(required=True)
    author = db.ReferenceField("User", dbref=True)
    create_time = db.DateTimeField(default=datetime.now)
    obj_cls = db.StringField()
    obj_pk = db.StringField()
    priority = db.IntField()
    next_actor = db.ReferenceField("User", dbref=True)
    meta = {
        'ordering': ['-create_time']
    }


class User(db.Document, UserMixin):
    username = db.StringField(required=True, unique=True, max_length=15)
    password = db.StringField(required=True, max_length=30)
    to_read_messages = db.ListField(db.ReferenceField("Message", dbref=True))

    @property
    def messages(self):
        return Message.objects.filter(next_actor=self)

    @property
    def create_messages(self):
        return Message.objects.filter(author=self)
