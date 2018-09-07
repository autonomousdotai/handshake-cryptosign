# -*- coding: utf-8 -*-
import os
import sys
import hashlib
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

user_routes = Blueprint('user', __name__)

@user_routes.route('/auth', methods=['POST'])
@login_required
def auth():
	try:
		data = request.json
		if data is None:
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

@user_routes.route('/hook/dispatcher', methods=['POST'])
@admin_required
def user_hook():
	try:
		data = request.json
		print data
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)
		
		type_change = data['type_change']
		user_id = data['user_id']
		email = data['email']
		meta_data = data['meta_data']

		print type_change
		print user_id
		print email
		print meta_data

		return response_ok(response)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
