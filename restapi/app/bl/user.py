from flask import g
from sqlalchemy import and_, func, Date, cast, asc, desc, bindparam
from datetime import date
from app import db
from app.models import User, Handshake, Shaker, Outcome
from app.constants import Handshake as HandshakeStatus
from app.helpers.utils import utc_to_local
from datetime import datetime
from app.helpers.utils import local_to_utc

import app.constants as CONST
import time


def count_user_free_bet(user_id):
	# check win or lose
	hs_count = db.session.query(func.count(Handshake.id)).filter(Handshake.free_bet == 1, Handshake.user_id == user_id).scalar()
	s_count = db.session.query(func.count(Shaker.id)).filter(Shaker.free_bet == 1, Shaker.shaker_id == user_id).scalar()
	return (hs_count if hs_count is not None else 0) + (s_count if s_count is not None else 0)


def check_user_is_able_to_create_new_free_bet(user_id):
	# Lastest handshake query
	hs_last = db.session.query(Handshake.date_created.label("created_time"), Outcome.id, Outcome.result, Handshake.side, Handshake.id)\
	.filter(Handshake.outcome_id == Outcome.id)\
	.filter(Handshake.status != HandshakeStatus['STATUS_PENDING'])\
	.filter(Handshake.user_id == user_id, Handshake.free_bet == 1)

	# Lastest shaker query
	s_last = db.session.query(Shaker.date_created.label("created_time"), Outcome.id, Outcome.result, Shaker.side, Shaker.id)\
	.filter(Shaker.handshake_id == Handshake.id)\
	.filter(Handshake.outcome_id == Outcome.id)\
	.filter(Shaker.status != HandshakeStatus['STATUS_PENDING'])\
	.filter(Shaker.shaker_id == user_id, Shaker.free_bet == 1)

	# Execute query
	item = hs_last.union_all(s_last).order_by(desc('created_time')).first()

	total_count_free_bet = count_user_free_bet(user_id)
	can_free_bet = True
	is_win = None
	if item is None:
		return can_free_bet, is_win, total_count_free_bet

	if item[2] == CONST.RESULT_TYPE['PENDING']:
		now = time.mktime(datetime.now().timetuple())
		create_time = time.mktime(utc_to_local(item[0].timetuple()))
		time_next_free_bet = now - create_time - CONST.DURATION_TIME_FREE_BET
		if time_next_free_bet < 0:
			can_free_bet = False

	elif item[2] != CONST.RESULT_TYPE['SUPPORT_WIN'] and \
		item[2] != CONST.RESULT_TYPE['AGAINST_WIN'] and \
		item[2] != CONST.RESULT_TYPE['DRAW']:
		can_free_bet = False

	if total_count_free_bet >= CONST.MAXIMUM_FREE_BET:
		can_free_bet = False

	if item[2] != item[3]:
		is_win = False
	else:
		is_win = True

	return can_free_bet, is_win, total_count_free_bet