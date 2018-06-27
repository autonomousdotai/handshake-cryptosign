import app.bl.handshake as handshake_bl

from flask import Blueprint, request
from app.helpers.response import response_ok, response_error
from app import db
from app.constants import Handshake as HandshakeStatus, CRYPTOSIGN_OFFCHAIN_PREFIX
from app.models import Handshake, Outcome, Shaker, Match
from app.helpers.message import MESSAGE, CODE
from app.tasks import update_feed, add_shuriken

event_routes = Blueprint('event', __name__)


@event_routes.route('/', methods=['POST'])
def event():
	
	# TODO:
	# Uninit free bet/ real bet: state failed
	# Collect free bet/ real bet: state failed
	
	data = request.json
	print 'event = {}'.format(data)

	if data is None:
		return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

	try:
		status = data.get('status', 1)
		
		handshakes = []
		shakers = []

		if status == 1:
			event_name = data['eventName']
			inputs = data['inputs']

			# parse inputs
			offchain = inputs['offchain']
			hid = int(inputs['hid'])

			response_json = []
			if '__createMarket' in event_name:
				offchain = int(offchain.replace('createMarket', ''))
				outcome = Outcome.find_outcome_by_id(offchain)
				if outcome is None:
					return response_error(MESSAGE.OUTCOME_INVALID, CODE.OUTCOME_INVALID)
				else:
					outcome.hid = hid
					db.session.flush()

					response_json.append(outcome.to_json())

			else:
				outcome = Outcome.find_outcome_by_hid(hid)
				if outcome is None:
					return response_error(MESSAGE.OUTCOME_INVALID, CODE.OUTCOME_INVALID)
				
				handshakes, shakers = handshake_bl.save_handshake_for_event(event_name, offchain, outcome)

			db.session.commit()

		else:
			# TODO:
			method = data.get('methodName', '')
			inputs = data['inputs']


		# update feed
		if handshakes is not None:
			for handshake in handshakes:
				response_json.append(handshake.to_json())
				update_feed.delay(handshake.id)
				if '__init' in event_name:
					add_shuriken(handshake.user_id)

		if shakers is not None:
			for shaker in shakers:
				response_json.append(shaker.to_json())
				update_feed.delay(shaker.handshake_id)
				if '__shake' in event_name:
					add_shuriken(shaker.shaker_id)

		return response_ok(response_json)
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
