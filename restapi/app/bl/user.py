from flask import g
from sqlalchemy import and_, func, cast, asc, desc, bindparam
from datetime import date
from app import db
from app.models import User, Handshake, Shaker, Outcome, Redeem
from app.constants import Handshake as HandshakeStatus
from datetime import datetime
from app.helpers.utils import local_to_utc

import time
import requests
import app.constants as CONST
import app.bl.outcome as outcome_bl


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


def is_able_to_create_new_free_bet(user):
	item = get_last_user_free_bet(user.id)
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


def is_able_to_have_redeem_code(user):
	redeems = db.session.query(Redeem).filter(Redeem.reserved_id==user.id, Redeem.used_user==user.id).all()
	if redeems is not None:
		if len(redeems) > 0:
		return False

	return True


def claim_redeem_code_for_user(user):
	if is_able_to_have_redeem_code(user):
		redeems = db.session.query(Redeem).filter(Redeem.reserved_id==0, Redeem.used_user==0).limit(2).all()
		if redeems is not None and len(redeems) == 2:
			for re in redeems:
				re.reserved_id = user.id
				db.session.flush()
			return True, redeems[0].code, redeems[1].code
	return False, None, None


def check_email_existed_with_dispatcher(payload):
	endpoint = '{}/user/profile'.format(g.DISPATCHER_SERVICE_ENDPOINT)
	data_headers = {
		"Payload": payload
	}
	res = requests.get(endpoint, headers=data_headers)
	if res.status_code > 400:
		return False
	data_response = res.json()
	if data_response['status'] == 0:
		return False
	if data_response['data'] is None:
		return False
	return data_response['data']['email']


def is_user_subscribed_but_still_not_have_redeem_code(user, be_able_to_have_redeem_code):
	if user is None:
		return False

	if user.email is not None and len(user.email) > 0 and user.is_subscribe == 1 and be_able_to_have_redeem_code:
		return True

	return False


def is_email_subscribed(email):
	user = db.session.query(User).filter(User.email==email).first()
	if user is not None:
		return True

	return False