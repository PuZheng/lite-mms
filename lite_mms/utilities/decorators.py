# -*- coding: utf-8 -*-
"""
handy decorators
"""
from flask import request, abort
from flask.templating import render_template, TemplateNotFound
from functools import wraps
import types


def templated(template):
    """This is a method to put a named arguments into the template file
    :param template:the file to be added a argument
    """

    def decorator(f):
        @wraps(f)
        def func(*args, **kwargs):
            template_temp = template
            if template_temp is None:
                template_temp = request.endpoint.replace('.', '/') + ".html"
            result = f(*args, **kwargs)
            if result is None:
                result = dict()
            elif not isinstance(result, dict):
                return result
            try:
                # pylint: disable=W0142
                return render_template(template_temp, **result)
                # pylint: enable=W0142
            except TemplateNotFound:
                abort(404)

        return func

    return decorator


def title_postfix(postfix):
    """join a value of titlename into the dict
    :param postfix:the url which going to access
    """

    def decoator(f):
        def func(*args, **kwargs):
            inner_dict = f(*args, **kwargs)
            if isinstance(inner_dict, dict):
                inner_dict['titlename'] = postfix
                # pylint: disable=W0142
            return render_template(postfix, **inner_dict)
            # pylint: enable=W0142

        return func

    return decoator


def ajax_call(f):
    """
    modify the name of the function(view), since there should be no 2 functions
    with the same in one bluepring
    """

    def decorator(*args, **kwargs):
        return f(*args, **kwargs)

    decorator.__name__ = f.__name__ + "_ajax_call"
    return decorator


def webservice_call(response_format):
    """
    1. modify the name of the function(view), since there should be no 2
    functions
    with the same in one bluepring
    2. modfiy the output of the view, change the "Content-Type" header
    @param response_format: the format of the result, only "json" supported
    @type response_format: str
    """

    def decorator(f):
        def innerfunc(*args, **kwargs):
            rv = f(*args, **kwargs)
            if isinstance(rv, types.TupleType) or \
                    isinstance(rv, types.ListType):
                response = rv[0]
                code = rv[1]
                headers = rv[2] if len(rv) == 3 else {}
            else:
                response = rv
                code = 200
                headers = {}
            if response_format == "json":
                headers.update({'Content-Type': "application/json"})
            else:
                pass
            return response, code, headers

        innerfunc.__name__ = f.__name__
        return innerfunc

    return decorator


def nav_bar_set(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        rv = f(*args, **kwargs)
        if isinstance(rv, dict):
            from lite_mms.basemain import nav_bar

            rv.update({'nav_bar': nav_bar})
        else:
            pass
        return rv

    return decorator


def committed(f):
    def _f(*args, **kwargs):
        ret = f(*args, **kwargs)
        from lite_mms.database import db

        if isinstance(ret, db.Model):
            from lite_mms.utilities import do_commit

            do_commit(ret)
        return ret

    return _f


def permission_required(permission, methods=("GET",)):
    def decorator(f):
        def _f(*args, **kwargs):
            if request.method in methods:
                permission.test()
            return f(*args, **kwargs)

        return _f

    return decorator
