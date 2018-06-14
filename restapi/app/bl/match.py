from flask import g
from datetime import *

from app import db
from app.models import User, Handshake, Match
from app.helpers.utils import local_to_utc

import app.constants as CONST


def find_all_markets():
	return db.session.query(Match).order_by(Match.date.asc()).all()

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
	t = datetime.now().timetuple()
	seconds = local_to_utc(t)

	if seconds > match.date + 4*60*60: #4hrs later
		return True

def is_exceed_dispute_time(match_id):
	match = Match.find_match_by_id(match_id)
	t = datetime.now().timetuple()
	seconds = local_to_utc(t)

	if seconds > match.date + (4*60*60) * 2: #8hrs later
		return True