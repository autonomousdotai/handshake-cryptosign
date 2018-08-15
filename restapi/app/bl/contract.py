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