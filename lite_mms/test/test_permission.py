# -*- coding: utf-8 -*-
import random
from mock import patch
from hashlib import md5
from flask import url_for
import flask.ext.principal as principal
from lite_mms.test import BaseTest
from lite_mms.apis import auth
from lite_mms.basemain import app


class TestPermission(BaseTest):
    def config(self):
        self.ECHO_DB = False

    def prepare_data(self):
        # create a foo permission
        from lite_mms import models

        foo_permission = models.Permission(name="foo_permission")
        self.db.session.add(foo_permission)
        self.db.session.commit()
        # create a group with foo_permission
        foo_group = models.Group("foo_group")
        foo_group.id = random.randint(99999, 199999)
        foo_group.permissions.append(foo_permission)
        self.db.session.add(foo_group)
        self.db.session.commit()
        # create a group without foo_permission 
        non_foo_group = models.Group("non_foo_group")
        non_foo_group.id = random.randint(99999, 199999)
        self.db.session.add(non_foo_group)
        self.db.session.commit()
        # create a user of foo_group
        self.foo_user = models.User("foo", md5("foo").hexdigest(), [foo_group])
        self.db.session.add(self.foo_user)
        self.db.session.commit()
        # create a user 
        self.non_foo_user = models.User("non_foo", md5("non_foo").hexdigest(),
                                        [non_foo_group])
        self.db.session.add(self.non_foo_user)
        self.db.session.commit()

    def test(self):
        with app.test_request_context():
            with app.test_client() as c:
                # first we assert foo has foo_permissions

                foo_user = auth.get_user(self.foo_user.id)
                assert len(foo_user.permissions) == 1
                assert "foo_permission" in [f.name for f in
                                            foo_user.permissions]

                non_foo_user = auth.get_user(self.non_foo_user.id)
                assert len(non_foo_user.permissions) == 0

                from collections import namedtuple

                foo_need = namedtuple("foo_need", [])
                FooPermission = principal.Permission(foo_need)
                with patch.dict('lite_mms.permissions.permissions',
                                {
                                    "foo_permission": {
                                        "needs": [foo_need],
                                    }
                                }, clear=True):
                    rv = c.post(url_for("auth.login"),
                                data=dict(username="foo", password="foo"))
                    assert rv.status_code == 302
                    assert FooPermission.can()
                    rv = c.post(url_for("auth.login"),
                                data=dict(username="non_foo",
                                          password="non_foo"))
                    assert rv.status_code == 302
                    assert not FooPermission.can()
