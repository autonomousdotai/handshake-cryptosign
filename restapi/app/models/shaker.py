#!/usr/bin/python
# -*- coding: utf-8 -*-

from app import db
from app.models.base import BaseModel
import app.constants as CONST

class Shaker(BaseModel):
	__tablename__ = 'shaker'
	__json_public__ = ['id', 'handshake_id', 'shaker_id', 'amount', 'currency', 'side', 'odds', 'win_value', 'status', 'bk_status']

	shaker_id = db.Column(db.Integer)
	amount = db.Column(db.Float)
	currency = db.Column(db.String(10))
	odds = db.Column(db.Float)
	win_value = db.Column(db.Float)
	side = db.Column(db.Integer,
					server_default=str(CONST.SIDE_TYPE['SUPPORT']),
					default=CONST.SIDE_TYPE['SUPPORT'])
	status = db.Column(db.Integer,
	                   server_default=str(CONST.Handshake['STATUS_PENDING']),
	                   default=CONST.Handshake['STATUS_PENDING'])
	bk_status = db.Column(db.Integer,
	                      server_default=str(CONST.Handshake['STATUS_PENDING']),
	                      default=CONST.Handshake['STATUS_PENDING'])

	handshake_id = db.Column('handshake_id', db.ForeignKey('handshake.id'))

	@classmethod
	def find_shaker_by_id(cls, _id):
		return Shaker.query.filter_by(id=_id).first()

	def __repr__(self):
		return '<shaker {}>'.format(self.id)
