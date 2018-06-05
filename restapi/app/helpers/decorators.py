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
        print 'Uid -> {}'.format(request.headers['Uid'])
        print 'Fcm-Token -> {}'.format(request.headers['Fcm-Token'])
        if not request.headers["Uid"]:
            return response_error("Please login first!")
        else:
            uid = int(request.headers["Uid"])
            token = request.headers['Fcm-Token']
            user = User.find_user_with_id(uid)
            if user is None:
                user = User(
                    id=uid,
                    fcm_token=token
                )
                db.session.add(user)
                db.session.commit()

        return f(*args, **kwargs)
    return wrap