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

def check_user_is_able_to_create_new_free_bet():
	data = db.session.query(func.sum(User.free_bet).label('amount')).filter(cast(User.date_created,Date) == date.today()).first()
	if data[0] is not None and int(data[0]) >= 100:
		return False
	return True

def count_user_free_bet(user_id):
	# check win or lose
	hs_count = db.session.query(func.count(Handshake.id)).filter(Handshake.free_bet == 1, Handshake.user_id == user_id).scalar()
	s_count = db.session.query(func.count(Shaker.id)).filter(Shaker.free_bet == 1, Shaker.shaker_id == user_id).scalar()
	return (hs_count if hs_count is not None else 0) + (s_count if s_count is not None else 0)


def get_first_bet(user_id):
	# check first bet is real-bet or free-bet
	# Oldest handshake query
	hs_first = db.session.query(Handshake.date_created.label("created_at"), Handshake.free_bet, bindparam("is_hs", 1)).filter(Handshake.user_id == user_id)
	# Oldest shaker query
	s_first = db.session.query(Shaker.date_created.label("created_at"), Shaker.free_bet, bindparam("is_hs", 0)).filter(Shaker.shaker_id == user_id)
	# Execute query
	first_item = hs_first.union_all(s_first).order_by(asc('created_at')).first()

	if first_item is None:
		return None, None

	date_created = first_item[0]
	is_free_bet = first_item[1]
	is_handshake = first_item[2]

	# Return date_created, is_free_bet
	return date_created, is_free_bet

def get_last_free_bet(user_id):
	# Lastest handshake query
	hs_last = db.session.query(Handshake.date_created.label("created_at") , Handshake.id, bindparam("is_hs", 1))\
	.filter(Handshake.outcome_id == Outcome.id)\
	.filter(Outcome.result == CONST.RESULT_TYPE['PENDING'])\
	.filter(Handshake.user_id == user_id, Handshake.free_bet == 1)
	# Lastest shaker query
	s_last = db.session.query(Shaker.date_created.label("created_at"), Shaker.id, bindparam("is_hs", 1))\
	.filter(Shaker.handshake_id == Handshake.id)\
	.filter(Handshake.outcome_id == Outcome.id)\
	.filter(Outcome.result == CONST.RESULT_TYPE['PENDING'])\
	.filter(Shaker.shaker_id == user_id, Shaker.free_bet == 1)
	# Execute query
	last_item = hs_last.union_all(s_last).order_by(desc('created_at')).first()

	if last_item is None:
		return None

	date_created = last_item[0]
	item_id = last_item[1]
	is_handshake = last_item[2]

	# Return date_created of lastest item
	return date_created

def check_time_last_free_bet_by_user_id(user_id):
	date_created = get_last_free_bet(user_id)

	# User hasn't any free_bet
	if date_created is None:
		return True, 0

	now = time.mktime(datetime.now().timetuple())
	create_time = time.mktime(utc_to_local(date_created.timetuple()))
	time_next_free_bet = now - create_time - CONST.DURATION_TIME_FREE_BET

	if time_next_free_bet < 0:
		return False, time_next_free_bet
	return True, 0
