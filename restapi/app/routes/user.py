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

from app.helpers.message import MESSAGE
from app.helpers.decorators import login_required
from app.helpers.response import response_ok, response_error
from app.helpers.utils import is_valid_email

user_routes = Blueprint('user', __name__)


@user_routes.route('/auth', methods=['POST'])
@login_required
def auth():
	try:
		data = request.json
		if data is None:
			raise Exception(MESSAGE.INVALID_DATA)

		email = data['email']
		password = data['password']

		confirm = hashlib.md5('{}{}'.format(email.strip(), g.PASSPHASE)).hexdigest()
		if email == g.EMAIL and password == confirm:
			response = {
			}
			if is_valid_email(email):
				response['access_token'] = create_access_token(identity=email, fresh=True)
			else:
				raise Exception(MESSAGE.USER_INVALID_EMAIL)

			return response_ok(response)

		else:
			raise Exception(MESSAGE.USER_INVALID)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
