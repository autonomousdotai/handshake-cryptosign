import requests

from app.helpers.bc_exception import BcException
from flask import g


def bc_transaction_detail(hash):
	bc_data = {
		'hash': hash,
	}

	bc_res = requests.post(g.BLOCKCHAIN_SERVER_ENDPOINT + '/receipt', bc_data)
	bc_json = bc_res.json()

	if bc_json['status'] != 1:
		raise BcException(bc_json['message'])

	return bc_json
