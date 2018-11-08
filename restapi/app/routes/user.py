# -*- coding: utf-8 -*-
import os
import sys
import json
import hashlib
import requests
import app.bl.user as user_bl
import app.bl.outcome as outcome_bl
import app.bl.match as match_bl

from flask import Blueprint, request, g
from app import db
from app.models import User, Token, Match, Handshake, Shaker, Outcome
from datetime import datetime
from flask_jwt_extended import (create_access_token)

from app.helpers.message import MESSAGE, CODE
from app.helpers.decorators import login_required, admin_required
from app.helpers.response import response_ok, response_error
from app.helpers.utils import is_valid_email, now_to_strftime
from app.tasks import subscribe_email_dispatcher, recombee_sync_user_data
from app.constants import Handshake as HandshakeStatus

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
	"""
	" Popup subscribe email will appear after user plays on match_id
	"""
	try:
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		if 'email' not in data or is_valid_email(data["email"]) is False:
			return response_error(MESSAGE.USER_INVALID_EMAIL, CODE.USER_INVALID_EMAIL)

		match = Match.find_match_by_id(data['match_id'])
		if match is None:
			return response_error(MESSAGE.MATCH_NOT_FOUND, CODE.MATCH_NOT_FOUND)

		email = data["email"]
		uid = request.headers["Uid"]

		user = User.find_user_with_id(uid)
		user.email = email
		db.session.commit()

		subscribe_email_dispatcher.delay(email, match.id, request.headers["Fcm-Token"], request.headers["Payload"], uid)
		return response_ok()

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@user_routes.route('/unsubscribe', methods=['GET'])
def user_click_unsubscribe():
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
			return response_error(MESSAGE.TOKEN_APPROVED_ALREADY, CODE.TOKEN_APPROVED_ALREADY)
		
		db.session.commit()
		return response_ok(user.to_json())

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)

@user_routes.route('/user/habit', methods=['POST'])
@login_required
def user_habit():
	"""
	request body:
	[{
		"view_type": "",
		"ids": [1,2,3],
		"options": {}
	}]
	"""
	try:
		data = request.json

		if data is None or len(data) == 0:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		uid = int(request.headers['Uid'])
		recombee_sync_user_data.delay(uid, data, now_to_strftime())
		return response_ok()

	except Exception, ex:
		return response_error(ex.message)

@user_routes.route('/reputation/<int:user_id>', methods=['GET'])
@login_required
def get_reputation_user(user_id):
	try:
		user = User.find_user_with_id(user_id)
		if user is None:
			return response_error(MESSAGE.USER_INVALID, CODE.USER_INVALID)

		# get all outcome created by user_id
		disputed_status = [HandshakeStatus['STATUS_DISPUTE_PENDING'], HandshakeStatus['STATUS_USER_DISPUTED'], HandshakeStatus['STATUS_DISPUTED']]
		outcomes = db.session.query(Outcome)\
			.filter(Outcome.hid != None)\
			.filter(Outcome.created_user_id == user_id)\
			.all()

		outcome_ids = list(map(lambda x: x.id, outcomes))
		
		# get all bet of outcome created by user_id
		hs_all_bets = db.session.query(Handshake.user_id.label("user_id"), Handshake.status.label("status"), Handshake.amount)\
			.filter(Handshake.outcome_id.in_(outcome_ids))

		s_all_bets = db.session.query(Shaker.shaker_id.label("user_id"), Shaker.status.label("status"), Shaker.amount)\
			.filter(Shaker.handshake_id == Handshake.id)\
			.filter(Handshake.outcome_id.in_(outcome_ids))

		data_response = {}

		bets_result = hs_all_bets.union_all(s_all_bets).all()

		data_response['total_events'] = len(outcome_ids)
		data_response['total_bets'] = len(bets_result)
		data_response['total_amount'] = sum(float(amount) for user_id,status,amount in bets_result)

		disputed_bets = list(filter(lambda x: x.status in disputed_status, bets_result))

		data_response['total_disputed_bets'] = len(disputed_bets)
		data_response['total_disputed_events'] = len(list(filter(lambda x: x.result == -3, outcomes)))
		data_response['total_disputed_amount'] = sum(float(amount) for user_id,status,amount in disputed_bets)

		return response_ok(data_response)

	except Exception, ex:
		return response_error(ex.message)


@user_routes.route('/reputation/<int:user_id>/match', methods=['GET'])
@login_required
def get_created_event_by_user(user_id):
	try:
		response = []
		matches = db.session.query(Match)\
				.filter(\
					Match.created_user_id == user_id,\
					Match.deleted == 0,\
					Match.public == 1,\
					Match.id.in_(db.session.query(Outcome.match_id).filter(Outcome.hid != None).group_by(Outcome.match_id)))\
				.order_by(Match.date.asc())\
				.all()
		for match in matches:
			arr_outcomes = outcome_bl.check_outcome_valid(match.outcomes)

			if len(arr_outcomes) > 0:
				match_json = match.to_json()
				total_user, total_bets = match_bl.get_total_user_and_amount_by_match_id(match.id)
				match_json["total_users"] = total_user
				match_json["total_bets"] = total_bets

				response.append(match_json)
		return response_ok(response)
	except Exception, ex:
		return response_error(ex.message)
