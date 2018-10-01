from flask import g
from datetime import *

from sqlalchemy import func
from app import db
from app.models import User, Handshake, Match, Outcome, Contract, Shaker
from app.helpers.utils import local_to_utc
from app.helpers.message import MESSAGE, CODE
from app.constants import Handshake as HandshakeStatus

import app.constants as CONST


def find_best_odds_which_match_support_side(outcome_id):
	handshake = db.session.query(Handshake).filter(Handshake.outcome_id==outcome_id, Handshake.side==CONST.SIDE_TYPE['AGAINST']).order_by(Handshake.odds.asc()).first()
	if handshake is not None:
		win_value = handshake.amount * handshake.odds
		best_odds = win_value/(win_value-handshake.amount)
		best_amount = handshake.amount * (handshake.odds - 1)
		return best_odds, best_amount
	return 0, 0


def is_exceed_report_time(match_id):
	match = Match.find_match_by_id(match_id)
	if match.reportTime is not None:
		t = datetime.now().timetuple()
		seconds = local_to_utc(t)

		if seconds > match.reportTime:
			return True
	return False


def is_exceed_closing_time(match_id):
	match = Match.find_match_by_id(match_id)
	if match.date is not None:
		t = datetime.now().timetuple()
		seconds = local_to_utc(t)
		if seconds > match.date:
			return True
	return False


def is_exceed_dispute_time(match_id):
	match = Match.find_match_by_id(match_id)
	if match.disputeTime is not None:
		t = datetime.now().timetuple()
		seconds = local_to_utc(t)

		if seconds > match.disputeTime:
			return True
	return False


def is_validate_match_time(data):
	if 'date' not in data or 'reportTime' not in data or 'disputeTime' not in data:
		return False
	
	t = datetime.now().timetuple()
	seconds = local_to_utc(t)

	if seconds >= data['date'] or seconds >= data['reportTime'] or seconds >= data['disputeTime']:
		return False

	if data['date'] < data['reportTime'] and data['reportTime'] < data['disputeTime']:
		return True
	
	return False


def is_able_to_set_result_for_outcome(outcome):
	if outcome.result == CONST.RESULT_TYPE['SUPPORT_WIN'] or \
		outcome.result == CONST.RESULT_TYPE['AGAINST_WIN'] or \
		outcome.result == CONST.RESULT_TYPE['DRAW']:

		return MESSAGE.OUTCOME_HAS_RESULT, CODE.OUTCOME_HAS_RESULT

	if outcome.result == CONST.RESULT_TYPE['PROCESSING']:
		return MESSAGE.OUTCOME_IS_REPORTING, CODE.OUTCOME_IS_REPORTING

	return None, None


def get_total_user_and_amount_by_match_id(match_id):
	# Total User
	hs_count_user = db.session.query(Handshake.user_id.label("user_id"))\
		.filter(Outcome.match_id == match_id)\
		.filter(Handshake.outcome_id == Outcome.id)\
		.filter(Handshake.status != HandshakeStatus['STATUS_PENDING'])\
		.group_by(Handshake.user_id)

	s_count_user = db.session.query(Shaker.shaker_id.label("user_id"))\
		.filter(Outcome.match_id == match_id)\
		.filter(Handshake.outcome_id == Outcome.id)\
		.filter(Handshake.id == Shaker.handshake_id)\
		.filter(Shaker.status != HandshakeStatus['STATUS_PENDING'])\
		.group_by(Shaker.shaker_id)

	user_union = hs_count_user.union(s_count_user)
	total_user = db.session.query(func.count(user_union.subquery().columns.user_id).label("total")).scalar()

	# Total Amount
	hs_amount = db.session.query(func.sum((Handshake.amount * Handshake.odds)).label("total_amount_hs"))\
		.filter(Outcome.match_id == match_id)\
		.filter(Handshake.outcome_id == Outcome.id)

	s_amount = db.session.query(func.sum((Shaker.amount * Shaker.odds)).label("total_amount_s"))\
		.filter(Outcome.match_id == match_id)\
		.filter(Handshake.outcome_id == Outcome.id)\
		.filter(Handshake.id == Shaker.handshake_id)

	total_amount = db.session.query(hs_amount.label("total_amount_hs"), s_amount.label("total_amount_s")).first()
	
	total_users = total_user if total_user is not None else 0			
	total_bets = (total_amount.total_amount_hs if total_amount.total_amount_hs is not None else 0)  + (total_amount.total_amount_s if total_amount.total_amount_s is not None else 0)

	return total_users, total_bets


def clean_source_with_valid_format(source):
	if source is None:
		return source
		
	if 'https://www.' in source:
		source = source.replace('https://www.', '')

	elif 'http://www.' in source:
		source = source.replace('http://www.', '')

	elif 'http://' in source:
		source = source.replace('http://', '')

	elif 'https://' in source:
		source = source.replace('https://', '')

	return source