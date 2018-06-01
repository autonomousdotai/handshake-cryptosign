from flask import g
from app import db

from app.helpers.bc_exception import BcException

import requests

def create_wallet(eth_address, eth_private_key):
	wallet = Wallet(address=eth_address, private_key=eth_private_key, source='Both')
	db.session.add(wallet)
	return wallet

def create_main_wallet(eth_address, eth_private_key):
	wallet = Wallet(address=eth_address, private_key=eth_private_key, source='Main Network')
	db.session.add(wallet)
	return wallet

def create_bc_wallet(chain_id):
	params = {'chain_id': chain_id}
	bc_res = requests.get(g.BLOCKCHAIN_SERVER_ENDPOINT + '/wallet/create', params=params)
	bc_json = bc_res.json()
	if bc_json['status'] != 1:
		raise Exception('Create wallet failed!')

	wallet = Wallet(address=bc_json['data']['address'], private_key=bc_json['data']['privateKey'], source='Test Network')
	return wallet

def get_eth_amount(wallet, chain_id):
	amount = 0.0
	params = {'address': wallet.address, 'privateKey': wallet.private_key, 'chain_id': chain_id}
	bc_res = requests.get(g.BLOCKCHAIN_SERVER_ENDPOINT + '/wallet/balance', params=params)
	bc_json = bc_res.json()
	if bc_json['status'] == 1:
		amount = bc_json['data']
	return amount

def free_transfer(wallet, amount, chain_id):
	params = {
		'address': wallet.address,
		'privateKey': wallet.private_key,
		'amount': amount,
		'chain_id': chain_id
	}

	bc_res = requests.get(g.BLOCKCHAIN_SERVER_ENDPOINT + '/cryptosign/free-transfer', params=params)
	bc_json = bc_res.json()

	if bc_json['status'] != 1:
		raise BcException(bc_json['message'])

	return bc_json

