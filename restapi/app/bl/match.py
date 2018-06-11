from flask import g

from app import db
from app.models import User, Handshake, Match
import app.constants as CONST


def find_all_markets():
	return db.session.query(Match).order_by(Match.date.asc()).all()

def find_best_odds_which_match_support_side(outcome_id):
	handshake = db.session.query(Handshake).filter(Handshake.outcome_id==outcome_id, Handshake.side==CONST.SIDE_TYPE['AGAINST']).order_by(Handshake.odds.asc()).first()
	if handshake is not None:
		win_value = handshake.amount * handshake.odds
		return win_value/(win_value-handshake.amount)
	return 0