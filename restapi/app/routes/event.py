from flask import Blueprint, request
from app.helpers.response import response_ok, response_error
from app import db
from app.constants import Handshake as HandshakeStatus, CRYPTOSIGN_OFFCHAIN_PREFIX
from app.models import Handshake, Outcome, Shaker
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

		outcome = Outcome.find_outcome_by_hid(hid)
		if outcome is None:
			return response_error(MESSAGE.INVALID_BET)

		if 'report' in offchain:
			side = offchain.replace('report', '')
			if len(side) > 0:
				side = int(side)
				outcome.result = side
				db.session.commit()

			return response_ok()
	
		handshake_bl.save_handshake_for_event(event_name, offchain)
		db.session.commit()

		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
