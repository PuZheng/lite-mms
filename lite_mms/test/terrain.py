# -*- coding: utf-8 -*-
import re
import tempfile
import os

from pyfeature import before_each_feature, after_each_feature

@before_each_feature
def setup(feature):
    from lite_mms.basemain import app
    from lite_mms.database import db, init_db
    db_fd, db_fname = tempfile.mkstemp()
    os.close(db_fd)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    try:
        db.init_app(app)
    except AssertionError:  # 这是因为flask禁止在一次请求之后再次init_app, 而
                            # 使用lettuce, 这是不可避免的
        pass 
    init_db()
    feature.db = db
    feature.db_fname = db_fname

    _models_dict = {}
    for model in db.Model.__subclasses__():
        try:
            _models_dict[model.__label__] = model
        except AttributeError:
            _models_dict[model.__name__] = model

    from pyfeature import step
    @step(u"create a (\w+)(.*)")
    @step(u"创建(\w+)(.*)")
    def _(step, model_name, desc, *args, **kwargs):
        """
        特别注意__hinter__这里的写法, 若不加"()", 那么"创建ProductType"就
        包含两种含义, 创建一个名字是Type的Product(Product是model类), 
        创建一个ProductType(ProductType是model类)
        """
        try:
            __hinter__ = kwargs.pop("__hinter__")
        except KeyError:
            __hinter__ = "\((?P<name>.+)\)"
        if __hinter__:
            m = re.match(__hinter__, desc)
            if m:
                args = m.groups() + args
        try:
            model = _models_dict[model_name] 
            ret = model(*args, **kwargs)
            db.session.add(ret)
            db.session.commit()
            return ret
        except KeyError, e:
            raise NotImplementedError()

    from lite_mms.utilities.contexts import keep_db_session_alive
    c = keep_db_session_alive()
    c.gen.next()

@after_each_feature
def teardown(feature):
    feature.db.session.remove()
    os.unlink(feature.db_fname)
    try:
        c.gen.next()
    except StopIteration:
        pass
