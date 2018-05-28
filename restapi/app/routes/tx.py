from flask import Blueprint, request

import app.bl.tx as tx_bl
from app.helpers.response import response_ok, response_error
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.helpers.message import MESSAGE
from app import db
from app.models import Tx, User

tx_routes = Blueprint('tx', __name__)


@tx_routes.route('/<int:handshake_id>')
@jwt_required
def handshake_transactions(handshake_id):
	try:
		user_id = get_jwt_identity()
		user = User.find_user_with_id(user_id)

		if not user:
			raise Exception(MESSAGE.USER_INVALID)

		txs = Tx.find_tx_with_hand_shake_id(handshake_id)

		data = []
		for tx in txs:
			data.append(tx.to_json())

		return response_ok(data)
	except Exception, ex:
		return response_error(ex.message)

@tx_routes.route('/receipt/<hash>')
def handshake_transaction_receipt(hash):
	try:
		data = tx_bl.bc_transaction_detail(hash)
		return response_ok(data)
	except Exception, ex:
		return response_error(ex.message)