from flask import Blueprint, request
from app.helpers.response import response_ok, response_error
from app import db
from app.constants import Handshake as HandshakeStatus, CRYPTOSIGN_OFFCHAIN_PREFIX
from app.models import Tx, Handshake, Outcome, Shaker
from app.helpers.message import MESSAGE
import app.bl.handshake as handshake_bl
from app.tasks import create_signed_handshake_file, add_payee_signature

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
	
		handshake_bl.save_handshake_for_event(event_name, offchain)
		db.session.commit()

		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


def parse_data(data):
	offchain = None
	hid = None
	state = -1
	if 'hid' in data:
		hid = data['hid']

	if 'offchain' in data:
		offchain = data['offchain']

	if 'state' in data:
		state = int(data['state'])

	return (hid, offchain, state)
