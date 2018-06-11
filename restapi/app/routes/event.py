from flask import Blueprint, request
from app.helpers.response import response_ok, response_error
from app import db
from app.constants import Handshake as HandshakeStatus, CRYPTOSIGN_OFFCHAIN_PREFIX
from app.models import Handshake, Outcome, Shaker, Match
from app.helpers.message import MESSAGE
import app.bl.handshake as handshake_bl

event_routes = Blueprint('event', __name__)


@event_routes.route('/', methods=['POST'])
def event():
	
	data = request.json
	print 'event = {}'.format(data)

	if data is None:
		return response_error(MESSAGE.INVALID_DATA)

	try:
		data = data['events']
		contract = data['contract']
		event_name = data['eventName']
		offchain = data['offchain']
		hid = int(data['hid'])

		if 'createMaket' in offchain:
			offchain = offchain.replace('createMaket', '')
			match = Match.find_match_by_id(offchain)
			if match is None:
				return response_error(MESSAGE.MATCH_NOT_FOUND)
			else:
				match.hid = hid
				db.session.flush()

		else:
			outcome = Outcome.find_outcome_by_hid(hid)
			if outcome is None:
				return response_error(MESSAGE.INVALID_BET)
	
		handshake_bl.save_handshake_for_event(event_name, offchain, outcome)
		db.session.commit()

		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
