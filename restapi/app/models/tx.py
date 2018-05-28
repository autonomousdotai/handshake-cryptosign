from app import db
from app.models.base import BaseModel

import app.constants as CONST
import json


class Tx(BaseModel):
	__tablename__ = 'tx'
	__json_public__ = ['id', 'hash', 'block_number', 'block_time_stamp', 'contract_method',
	                   'from_address', 'to_address', 'transaction_status', 'status', 'user_id']

	hash = db.Column(db.String(255))
	block_number = db.Column(db.String(255))
	block_time_stamp = db.Column(db.String(255))
	scope = db.Column(db.String(255))
	scope_id = db.Column(db.Integer)
	contract_name = db.Column(db.String(255))
	contract_address = db.Column(db.String(255))
	contract_method = db.Column(db.String(255))
	arguments = db.Column(db.String(255))
	payload = db.Column(db.Text)
	from_address = db.Column(db.String(255))
	to_address = db.Column(db.String(255))
	amount = db.Column(db.String(255))
	user_id = db.Column('user_id', db.ForeignKey('user.id'))
	status = db.Column(db.Integer,
	                   server_default=str(CONST.Tx['STATUS_PENDING']),
	                   default=CONST.Tx['STATUS_PENDING'])
	transaction_status = db.Column(db.String(255))
	chain_id = db.Column(db.Integer, default=CONST.BLOCKCHAIN_NETWORK['RINKEBY'], server_default=str(CONST.BLOCKCHAIN_NETWORK['RINKEBY']))

	@classmethod
	def find_tx_with_id(cls, tx_id):
		return Tx.query.filter_by(id=tx_id).first()

	@classmethod
	def find_tx_with_hand_shake_id(cls, handshake_id):
		return Tx.query.filter_by(scope='handshake', scope_id=handshake_id).order_by(Tx.date_created.desc()).all()

	def __repr__(self):
		return '<Tx {}>'.format(self.hash)
