from functools import wraps
from flask_jwt_extended import get_jwt
from flask_jwt_extended import verify_jwt_in_request
from flask import jsonify, make_response


def superAdmin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            try:
                if claims["designation"] == 100:
                    return fn(*args, **kwargs)
            except KeyError:
                return make_response(jsonify(msg="Super admin only!"), 403)
        return decorator
    return wrapper

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            try:
                if claims["designation"] == 101:
                    return fn(*args, **kwargs)
            except KeyError:
                return make_response(jsonify(msg="admin only!"), 403)
        return decorator
    return wrapper



def teacher_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            try:
                if claims["designation"] == 102:
                    return fn(*args, **kwargs)
            except KeyError:
                return make_response(jsonify(msg="Teacher only!"), 403)

        return decorator

    return wrapper


def principal_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            try:
                if claims["designation"] == 103:
                    return fn(*args, **kwargs)
            except KeyError:
                return make_response(jsonify(msg="Principal only!"), 403)

        return decorator

    return wrapper