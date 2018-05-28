from flask import request
from app import db
from app.models.base import BaseModel

import app.constants as CONST
import requests


class Wallet(BaseModel):
	__tablename__ = 'wallet'
	__json_public__ = ['id', 'address', 'source']

	address = db.Column(db.String(255))
	private_key = db.Column(db.String(255))
	user_id = db.Column('user_id', db.ForeignKey('user.id'))
	status = db.Column(db.Integer,
                       server_default=str(CONST.Wallet['STATUS_ACTIVE']),
                       default=CONST.Wallet['STATUS_ACTIVE'])
	source = db.Column(db.String(50))

	@classmethod
	def find_wallet_by_address(cls, address):
		return Wallet.query.filter_by(address=address).first()

	@classmethod
	def find_wallet_by_list_address(cls, list_address):
		return Wallet.query.filter(Wallet.address.in_(list_address)).all()

	def __repr__(self):
		# return '<wallet {}>'.format(self.id)
		return '<Wallet(address=%s)' % (self.address)
