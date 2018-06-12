#!/usr/bin/python
# -*- coding: utf-8 -*-
from functools import wraps
from flask import request
from app import db
from app.helpers.response import response_error
from app.models import User


trusted_proxies = ('127.0.0.1')
white_ips = ( '127.0.0.1' )


def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        remote = request.remote_addr
        route = list(request.access_route)
        while remote not in trusted_proxies:
            remote = route.pop()

        if remote not in white_ips:
            return response_error("Access deny!")       

        return f(*args, **kwargs)
    return wrap

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        print 'Uid -> {}'.format(request.headers['Uid'])
        print 'Fcm-Token -> {}'.format(request.headers['Fcm-Token'])
        print 'Payload -> {}'.format(request.headers['Payload'])
        if not request.headers["Uid"]:
            return response_error("Please login first!")
        else:
            try:
                uid = int(request.headers["Uid"])
                token = request.headers['Fcm-Token'] if 'Fcm-Token' in request.headers else ''
                payload = request.headers['Payload'] if 'Payload' in request.headers else ''
                user = User.find_user_with_id(uid)
                if user is None:
                    user = User(
                        id=uid,
                        fcm_token=token,
                        payload=payload
                    )
                    db.session.add(user)
                    db.session.commit()
                elif user.fcm_token != token:
                    user.fcm_token = token
                    db.session.commit()
            except Exception as ex:
                db.session.rollback()
                print(str(ex))

            

        return f(*args, **kwargs)
    return wrap