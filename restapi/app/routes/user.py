# -*- coding: utf-8 -*-
import os
import sys
from flask import Blueprint, request, g
from app import db, sg, s3
from app.models import User
from app.bl.handshake import update_to_address_for_user
from datetime import datetime
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, get_jwt_identity)

from app.tasks import add_request_eth_transaction
from app.helpers.message import MESSAGE
from app.helpers.response import response_ok, response_error
from app.helpers.utils import is_valid_email

import app.bl.user as user_bl
import app.bl.wallet as wallet_bl

user_routes = Blueprint('user', __name__)

'''
	This /auth API is used for web only
'''
@user_routes.route('/auth', methods=['POST'])
def auth():
	try:
		email = request.form.get('email', '').lower().strip()
		user_id = int(request.form.get('id', ''))
		name = request.form.get('name', '')
		print 'before auth'
		print email
		print user_id
		if is_valid_email(email):
			json = user_bl.autonomous_verify_email(email)
			print json
			if json.get('status', 0) != 1:
				return response_error(MESSAGE.USER_INVALID_INPUT)
			else:
				customer = json['data']
				autonomous_email = customer['email']
				autonomous_id = int(customer['id'])
				autonomous_name = customer['name']
				autonomous_eth_address = customer['eth_address']
				autonomous_eth_private_key = customer['eth_private_key']

				if email == autonomous_email and \
						user_id == autonomous_id:
					user = user_bl.sync_user(autonomous_id, autonomous_name, autonomous_email, autonomous_eth_address,
					                 autonomous_eth_private_key)

					update_to_address_for_user(user)
					db.session.commit()

					access_token = create_access_token(identity=user.id, fresh=True)
					refresh_token = create_refresh_token(identity=user.id)

					amount = wallet_bl.get_eth_amount(user.wallet, user.chain_id)

					user_json = user.to_json()
					user_wallet = user_json.get('wallet', {})
					user_wallet['amount'] = amount

					return response_ok({
						'user': user_json,
						'access_token': access_token,
						'refresh_token': refresh_token,
					})
				else:
					return response_error(MESSAGE.USER_INVALID_INPUT)
		else:
			return response_error(MESSAGE.USER_INVALID_EMAIL)
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)

@user_routes.route('/sign-in', methods=['POST'])
def sign_in():
	try:
		email = request.form.get('email', '').lower().strip()
		name = request.form.get('name', '').strip()
		password = request.form.get('password', '')

		if is_valid_email(email):
			json = user_bl.autonomous_auth_user(email, password)
			if json.get('status', 0) == 1:
				pass
			else:
				json = user_bl.autonomous_sign_in(email, password)
				if json.get('status', 0) != 1:
					return response_error(json.get('message', MESSAGE.USER_CANNOT_REGISTRY))

			customer = json['customer']
			autonomous_email = customer['email']
			autonomous_id = int(customer['id'])
			autonomous_name = customer.get('name', '')

			autonomous_eth_address = customer['eth_address']
			autonomous_eth_private_key = customer['eth_private_key']

			user = user_bl.sync_user(autonomous_id, autonomous_name, autonomous_email, autonomous_eth_address,
			                 autonomous_eth_private_key)

			if len(user.name) == 0:
				user.name = name
			elif len(name) > 0 and name != user.name:
				user.name = name

			update_to_address_for_user(user)
			db.session.commit()

			access_token = create_access_token(identity=user.id, fresh=True)
			refresh_token = create_refresh_token(identity=user.id)

			amount = wallet_bl.get_eth_amount(user.wallet, user.chain_id)

			user_json = user.to_json()
			user_wallet = user_json.get('wallet', {})
			user_wallet['amount'] = amount

			return response_ok({
				'user': user_json,
				'access_token': access_token,
				'refresh_token': refresh_token
			})
		else:
			return response_error(MESSAGE.USER_INVALID_EMAIL)

	except Exception, ex:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("sign_in", exc_type, fname, exc_tb.tb_lineno)
		db.session.rollback()
		return response_error(ex.message)

@user_routes.route('/social-login', methods=['POST'])
def social_login():
	try:
		access_token = request.form.get('access_token', '').strip()
		source = request.form.get('source', '')
		name = request.form.get('name', '').strip()

		if len(access_token) > 0:
			if source not in ['google+', 'facebook']:
				return response_error(MESSAGE.USER_INVALID_SOURCE)
			else:
				json = user_bl.autonomous_social_login(source, access_token)
				if json.get('status', 0) != 1:
					return response_error(json.get('message', MESSAGE.USER_CANNOT_REGISTRY))

				customer = json['customer']
				autonomous_email = customer['email']
				autonomous_id = int(customer['id'])
				autonomous_name = customer.get('name', '')
				autonomous_eth_address = customer['eth_address']
				autonomous_eth_private_key = customer['eth_private_key']
				user = user_bl.sync_user(autonomous_id, autonomous_name, autonomous_email, autonomous_eth_address,
								autonomous_eth_private_key)

				if len(user.name) == 0:
					user.name = name
				elif len(name) > 0 and name != user.name:
					user.name = name

				update_to_address_for_user(user)
				db.session.commit()

				access_token = create_access_token(identity=user.id, fresh=True)
				refresh_token = create_refresh_token(identity=user.id)

				amount = wallet_bl.get_eth_amount(user.wallet, user.chain_id)

				user_json = user.to_json()
				user_wallet = user_json.get('wallet', {})
				user_wallet['amount'] = amount

				return response_ok({
					'user': user_json,
					'access_token': access_token,
					'refresh_token': refresh_token
				})

				return response_ok(json)
		else:
			return response_error(MESSAGE.USER_INVALID_ACCESS_TOKEN)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)

@user_routes.route('/forgot-password', methods=['POST'])
def forgot_password():
	try:
		email = request.form.get('email', '').lower().strip()

		if is_valid_email(email):
			json = user_bl.autonomous_forgot_password(email)
			if json.get('status', 0) == 1:
				return response_ok("The reset password email has been sent to {}".format(email))
			else:
				return response_error(json.get('message', 'Your email not in our system.'))
		else:
			return response_error(MESSAGE.USER_INVALID_EMAIL)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)

@user_routes.route('/update-profile', methods=['POST'])
@jwt_required
def update_profile():
	try:
		user_id = get_jwt_identity()
		user = User.query.get(user_id)

		name = request.form.get('name', '').strip()
		user.name = name
		user_bl.autonomous_update_user_info(user)

		amount = wallet_bl.get_eth_amount(user.wallet, user.chain_id)
		user_json = user.to_json()
		user_wallet = user_json.get('wallet', {})
		user_wallet['amount'] = amount
		db.session.commit()

		return response_ok({
			'user': user_json
		})

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
