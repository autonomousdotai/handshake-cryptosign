from flask import g
from sqlalchemy import and_, func, cast, asc, desc
from datetime import date
from app import db
from app.models import User, Handshake, Shaker, Outcome
from app.constants import Handshake as HandshakeStatus
from app.core import mail_services
from datetime import datetime
from app.helpers.utils import local_to_utc
from app.helpers.mail_content import render_email_notify_result_content

import app.constants as CONST
import app.bl.outcome as outcome_bl
import time
import requests


def get_last_user_free_bet(user_id):
	# Lastest handshake query
	hs_last = db.session.query(Handshake.date_created.label("created_time"), Outcome.id, Handshake.side)\
	.filter(Handshake.outcome_id == Outcome.id)\
	.filter(Handshake.status != HandshakeStatus['STATUS_PENDING'])\
	.filter(Handshake.user_id == user_id, Handshake.free_bet == 1)

	# Lastest shaker query
	s_last = db.session.query(Shaker.date_created.label("created_time"), Outcome.id, Shaker.side)\
	.filter(Shaker.handshake_id == Handshake.id)\
	.filter(Handshake.outcome_id == Outcome.id)\
	.filter(Shaker.status != HandshakeStatus['STATUS_PENDING'])\
	.filter(Shaker.shaker_id == user_id, Shaker.free_bet == 1)

	# Execute query
	item = hs_last.union_all(s_last).order_by(desc('created_time')).first()
	return item


def is_able_to_create_new_free_bet(user_id):
	item = get_last_user_free_bet(user_id)
	can_free_bet = True
	last_bet_status = None
	if item is not None:
		outcome_id = item[1]
		user_side = item[2]
		outcome = Outcome.find_outcome_by_id(outcome_id)
		if outcome_bl.has_result(outcome):
			can_free_bet = (CONST.MAXIMUM_FREE_BET - user.free_bet) > 0
			last_bet_status = outcome.result == user_side
		else:
			can_free_bet = False
	
	return can_free_bet, last_bet_status


def check_email_existed_with_dispatcher(app, payload):
	# Subscribe email
	endpoint = '{}/user/profile'.format(app.config["DISPATCHER_SERVICE_ENDPOINT"])
	data_headers = {
		"Payload": payload
	}
	res = requests.get(endpoint, headers=data_headers)
	if res.status_code > 400:
		print "Subscribe email fail: {}".format(res)
		return False
	data_response = res.json()
	if data_response['status'] == 0:
		print "Subscribe email fail with status: 0"
		return False
	if data_response['data'] is None:
		print "Subscribe email fail with data is none"
		return False
	return data_response['data']['email']


def handle_mail_notif(app, user_id, from_address, oc_name, match_name, oc_result, side, status, free_bet, free_bet_available):
	user = User.find_user_with_id(user_id)
	email = user.email
	if user is None:
		return False

	if user.email is None:
		email_exist = check_email_existed_with_dispatcher(app, user.payload)
		if email_exist is False:
			return False
		user.email = email_exist
		db.session.commit()
		email = email_exist
	
	if user.is_subscribe == 1:
		email_body = render_email_notify_result_content(app, user_id, from_address, oc_name, match_name, oc_result, side, status, free_bet == 1, free_bet_available)
		mail_services.send(email, app.config['FROM_EMAIL'], "Results [{}]".format(oc_name), email_body) 
	else:
		print("send_email_result_notifcation => User did not subscribe: {}", user)
		return False
	return True
