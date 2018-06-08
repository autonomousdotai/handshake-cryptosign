# -*- coding: utf-8 -*-
import os
import sys
from flask import Blueprint, request, g
from app import db, sg, s3
from app.models import User
from app.bl.handshake import update_to_address_for_user
from datetime import datetime
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, get_jwt_identity)

from app.helpers.message import MESSAGE
from app.helpers.response import response_ok, response_error
from app.helpers.utils import is_valid_email

import app.bl.user as user_bl

user_routes = Blueprint('user', __name__)

'''
	This /auth API is used for web only
'''
@user_routes.route('/auth', methods=['POST'])
def auth():
	try:
		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)

@user_routes.route('/sign-in', methods=['POST'])
def sign_in():
	try:
		return response_ok()

	except Exception, ex:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("sign_in", exc_type, fname, exc_tb.tb_lineno)
		db.session.rollback()
		return response_error(ex.message)

@user_routes.route('/social-login', methods=['POST'])
def social_login():
	try:
		return response_ok()

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)

@user_routes.route('/forgot-password', methods=['POST'])
def forgot_password():
	try:
		return response_ok()

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)

@user_routes.route('/update-profile', methods=['POST'])
@jwt_required
def update_profile():
	try:
		return response_ok()

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
