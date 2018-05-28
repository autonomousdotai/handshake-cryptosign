#!/usr/bin/python
# -*- coding: utf-8 -*-
from functools import wraps
from flask import request
from app import db
from app.helpers.response import response_error
from app.models import User

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        print 'UID -> {}'.format(request.headers['Uid'])
        if not request.headers["Uid"]:
            return response_error("Please login first!")
        else:
            uid = int(request.headers["Uid"])
            user = User.find_user_with_uid(uid)
            if user is None:
                user = User(
                    uid=uid
                )
                db.session.add(user)
                db.session.commit()

        return f(*args, **kwargs)
    return wrap