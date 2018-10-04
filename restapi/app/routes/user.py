# -*- coding: utf-8 -*-
import os
import sys
import json
import hashlib
import requests
import app.bl.user as user_bl

from flask import Blueprint, request, g
from app import db
from app.models import User, Token
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


@user_routes.route('/unsubscribe', methods=['GET'])
def user_check_unsubscribe():
	try:
		token = request.args.get('token')
		uid = request.args.get('id')

		if token is None or uid is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		confirm = hashlib.md5('{}{}'.format(uid, g.PASSPHASE)).hexdigest()
		if confirm != token:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)
		
		user = User.find_user_with_id(uid)
		if user is None:
			return response_error(MESSAGE.CANNOT_UNSUBSCRIBE_EMAIL, CODE.CANNOT_UNSUBSCRIBE_EMAIL)
		
		user.is_subscribe = 0
		db.session.commit()
		return response_ok()

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@user_routes.route('/approve_token', methods=['POST'])
@login_required
def user_approve_new_token():
	"""
	" Add token that approved by user. It's used for ERC20 function.
	"""
	try:
		data = request.json
		if data is None or \
			'token_id' not in data:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		uid = int(request.headers['Uid'])
		token_id = data['token_id']

		token = Token.find_token_by_id(token_id)
		if token is None or \
			token.tid is None or \
			token.status == -1:
			return response_error(MESSAGE.TOKEN_NOT_FOUND, CODE.TOKEN_NOT_FOUND)
		
		user = User.find_user_with_id(uid)

		if token not in user.tokens:
			user.tokens.append(token)
		else:
			return response_error('121212', '121221')
		
		db.session.commit()
		return response_ok(user.to_json())

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
