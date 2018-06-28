import app.bl.handshake as handshake_bl

from flask import Blueprint, request
from app.helpers.response import response_ok, response_error
from app import db
from app.constants import Handshake as HandshakeStatus, CRYPTOSIGN_OFFCHAIN_PREFIX
from app.models import Handshake, Outcome, Shaker, Match, Tx
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
		tx_id = int(data['id'])

		handshakes = []
		shakers = []
		tx = Tx.find_tx_by_id(tx_id)
		if status == 1:
			event_name = data['eventName']
			inputs = data['inputs']
			handshakes, shakers = handshake_bl.save_handshake_for_event(event_name, inputs)

			if tx is not None:
				tx.status = 1
				db.session.flush()

		else:
			# TODO:
			method = data.get('methodName', '')
			inputs = data['inputs']

			if tx is not None:
				tx.status = 0
				db.session.flush()

		db.session.commit()
		# update feed
		if handshakes is not None:
			for handshake in handshakes:
				update_feed.delay(handshake.id)
				if '__init' in event_name:
					add_shuriken(handshake.user_id)

		if shakers is not None:
			for shaker in shakers:
				update_feed.delay(shaker.handshake_id)
				if '__shake' in event_name:
					add_shuriken(shaker.shaker_id)

		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
