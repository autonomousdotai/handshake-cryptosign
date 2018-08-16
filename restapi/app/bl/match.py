from flask import g
from datetime import *

from app import db
from app.models import User, Handshake, Match, Outcome, Contract
from app.helpers.utils import local_to_utc
from app.helpers.message import MESSAGE, CODE

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