# -*- coding: UTF-8 -*-
"""
@author: Yangminghua
@version: $
"""
import tempfile
import os
from lite_mms.basemain import app
from lite_mms.database import db, init_db

class BaseTest(object):
    def setup(self):
        self.config()

        self.db_fd, self.db_fname = tempfile.mkstemp()
        os.close(self.db_fd)
        dbstr = "sqlite:///" + self.db_fname + ".db"

        app.config["SQLALCHEMY_DATABASE_URI"] = dbstr

        init_db()
        try:
            db.init_app(app)
        except:
            # 第二次执行init_app时，由于app已经执行过request，将导致app无法再次初始化。
            pass
        self.db = db
        self.prepare_data()
        print dbstr


    def teardown(self):
        db.drop_all()
        os.unlink(self.db_fname)

    def prepare_data(self):
        assert 0, "unimplemented"

    def config(self):
        self.ECHO_DB = False
