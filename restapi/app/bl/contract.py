from flask import g
from datetime import *

from app import db
from app.models import Contract

import app.constants as CONST


def all_contracts():
	c = []
	contracts = db.session.query(Contract).all()
	for contract in contracts:
		c.append(contract.to_json())
	return c

def filter_contract_id_in_contracts(j, contracts):
	if j is not None and 'contract_id' in j:
		contract_id = j['contract_id']
		del j['contract_id']
		j['contract'] = None
		for c in contracts:
			if c['id'] == contract_id:
				j['contract'] = c
				break
	return j
	