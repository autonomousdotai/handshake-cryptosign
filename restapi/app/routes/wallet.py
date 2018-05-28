from datetime import datetime
from flask import Blueprint, request
from sqlalchemy import func
import json

from app.helpers.response import response_ok, response_error
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.tasks import add_request_eth_transaction
from app.models import User, Tx
from app.helpers.message import MESSAGE

import app.bl.wallet as wallet_bl
import app.bl.user as user_bl

wallet_routes = Blueprint('wallet', __name__)

@wallet_routes.route('/', methods=['GET'])
@jwt_required
def wallet():
	try:
		data = request.args
		chain_id = data.get('chain_id', 4, type=int)

		source = 'Test Network'
		if chain_id is not 4: source = 'Main Network'

		user_id = get_jwt_identity()
		user = User.find_user_with_id(user_id)

		wallet = user.wallets.filter_by(source='Both').first()

		if wallet is None:
			wallet = user.wallets.filter_by(source=source).first()
			if wallet is None and source is 'Main Network':
				print wallet
				user_info = user_bl.autonomous_update_user_info(user)
				print user_info['data']['eth_address']
				if user_info['status'] is 1:
					wallet = wallet_bl.create_main_wallet(user_info['data']['eth_address'], user_info['data']['eth_private_key'])
					user.wallets.append(wallet)

		amount = wallet_bl.get_eth_amount(wallet, chain_id)
		wallet_info = {'address': wallet.address, 'amount': amount}
		return response_ok(wallet_info)

	except Exception, ex:
		return response_error(ex.message)

@wallet_routes.route('/balance', methods=['GET'])
@jwt_required
def balance():
	try:
		data = request.args
		chain_id = data.get('chain_id', 4, type=int)

		source = 'Test Network'
		if chain_id is not 4: source = 'Main Network'

		user_id = get_jwt_identity()
		user = User.find_user_with_id(user_id)

		wallet = user.wallets.filter_by(source='Both').first()

		if wallet is None:
			wallet = user.wallets.filter_by(source=source).first()
			if wallet is None and source is 'Main Network':
				user_info = user_bl.autonomous_update_user_info(user)
				if user_info.status is 1:
					wallet = wallet_bl.create_main_wallet(user_info['data'].eth_address, user_info['data'].eth_private_key)

		amount = wallet_bl.get_eth_amount(wallet, chain_id)

		return response_ok(amount)

	except Exception, ex:
		return response_error(ex.message)

@wallet_routes.route('/check-request-eth')
@jwt_required
def check_request_eth():
	try:
		user_id = get_jwt_identity()
		user = User.find_user_with_id(user_id)
		# tmp remove check beta user Mar 31, 2018
		# logic check user if valid
		# response = user_bl.autonomous_free_handshake_beta(user.email)
		# if response.get('status', 0) != 1:
		# 	raise Exception('Hmm.. something went wrong. Please try again.')
		#
		# if response.get('data', 0) != 1:
		# 	raise Exception('Hmm.. you are not in our beta users.')

		tx = Tx.query.filter(Tx.contract_method == 'free-transfer', Tx.user_id == user.id).first()

		if tx:
			raise Exception(MESSAGE.WALLET_RECEIVE_ETH_ALREADY)

		return response_ok(1)
	except:
		return response_ok(0)


@wallet_routes.route('/request-eth')
@jwt_required
def request_eth():
	try:
		data = request.args
		chain_id = data.get('chain_id', 4, type=int)

		if chain_id is not 4:
			raise Exception(MESSAGE.WALLET_REJECT_FREE_ETH)

		user_id = get_jwt_identity()
		user = User.find_user_with_id(user_id)

		# tmp remove check beta user Mar 31, 2018
		# logic check user if valid
		# response = user_bl.autonomous_free_handshake_beta(user.email)
		#
		# if response.get('status', 0) != 1:
		# 	raise Exception('Hmm.. something went wrong. Please try again.')
		#
		# if response.get('data', 0) != 1:
		# 	raise Exception('Hmm.. you are not in our beta users.')

		source = 'Test Network'
		if chain_id is not 4: source = 'Main Network'

		wallet = user.wallet
		user.chain_id = chain_id
		user.current_network = source

		tx = Tx.query.filter(Tx.contract_method == 'free-transfer', Tx.user_id == user.id).first()

		if tx:
			raise Exception(MESSAGE.WALLET_RECEIVE_ETH_ALREADY)

		total_free_today = Tx.query.filter(Tx.contract_method == 'free-transfer',
		                              func.datediff(Tx.date_created, func.date(func.now()))).count()

		if total_free_today >= 1000:
			raise Exception(MESSAGE.WALLET_EXCEED_FREE_ETH)


		bc_json = wallet_bl.free_transfer(wallet, '1', chain_id) # 0.0011 for main net, 1 for test net

		add_request_eth_transaction.delay(bc_json, user_id, chain_id)

		hash = bc_json['data']['hash']
		return response_ok(hash)

	except Exception, ex:
		return response_error(ex.message)
