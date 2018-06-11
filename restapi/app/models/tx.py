from app import db
from app.models.base import BaseModel

import app.constants as CONST
import json


class Tx(BaseModel):
	__tablename__ = 'tx'
	__json_public__ = ['id', 'hash', 'contract_address', 'contract_method',
	                   'payload', 'status', 'chain_id']

	hash = db.Column(db.String(255))
	contract_address = db.Column(db.String(255))
	contract_method = db.Column(db.String(255))
	payload = db.Column(db.Text)
	status = db.Column(db.Integer,
	                   server_default=str(CONST.Tx['STATUS_PENDING']),
	                   default=CONST.Tx['STATUS_PENDING'])
	chain_id = db.Column(db.Integer, default=CONST.BLOCKCHAIN_NETWORK['RINKEBY'], server_default=str(CONST.BLOCKCHAIN_NETWORK['RINKEBY']))

	@classmethod
	def find_tx_with_id(cls, tx_id):
		return Tx.query.filter_by(id=tx_id).first()

	@classmethod
	def find_tx_with_hand_shake_id(cls, handshake_id):
		return Tx.query.filter_by(scope='handshake', scope_id=handshake_id).order_by(Tx.date_created.desc()).all()

	def __repr__(self):
		return '<Tx {}>'.format(self.hash)
