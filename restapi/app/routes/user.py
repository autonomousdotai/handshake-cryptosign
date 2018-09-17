# -*- coding: utf-8 -*-
import os
import sys
import json
import hashlib
import requests
import app.bl.user as user_bl

from flask import Blueprint, request, g
from app import db, sg, s3
from app.models import User
from datetime import datetime
from flask_jwt_extended import (create_access_token)

from app.helpers.message import MESSAGE, CODE
from app.helpers.decorators import login_required, admin_required
from app.helpers.response import response_ok, response_error
from app.helpers.utils import is_valid_email
from app.tasks import subscribe_email_dispatcher


user_routes = Blueprint('user', __name__)

@user_routes.route('/auth', methods=['POST'])
@login_required
def auth():
	try:
		data = request.json
		if data is None or 'email' not in data:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)
		
		email = data['email']
		password = data['password']

		confirm = hashlib.md5('{}{}'.format(email.strip(), g.PASSPHASE)).hexdigest()
		if email == g.EMAIL and password == confirm:
			response = {
			}
			if is_valid_email(email):
				response['access_token'] = create_access_token(identity=email, fresh=True)
			else:
				return response_error(MESSAGE.USER_INVALID_EMAIL, CODE.USER_INVALID_EMAIL)

			return response_ok(response)

		else:
			return response_error(MESSAGE.USER_INVALID, CODE.USER_INVALID)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)

@user_routes.route('/subscribe', methods=['POST'])
@login_required
def user_subscribe():
	try:
		data = request.json

		if data is None or 'email' not in data or is_valid_email(data["email"]) is False:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		email = data["email"]
		uid = request.headers["Uid"]

		user = User.find_user_with_id(uid)
		user.email = email
		db.session.commit()

		subscribe_email_dispatcher.delay(email, request.headers["Fcm-Token"], request.headers["Payload"], uid)

		return response_ok()

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)

@user_routes.route('/unsubscribe/<string:token>', methods=['GET'])
def user_check_unsubscribe(token):
	try:
		arr = token.split('==')
		if len(arr) != 2:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)
		
		user_id = arr[1]
		confirm = hashlib.md5('{}{}'.format(user_id, g.PASSPHASE)).hexdigest()
		confirm = "{}=={}".format(confirm, user_id)
		if confirm != token:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)
		
		user = User.find_user_with_id(user_id)
		if user is None:
			return response_error(MESSAGE.CANNOT_UNSUBSCRIBE_EMAIL, CODE.CANNOT_UNSUBSCRIBE_EMAIL)
		
		user.is_subscribe = 0
		db.session.commit()
		return response_ok()

	except Exception, ex:
		db.session.rollback()
		print ex.message
		return response_error()
