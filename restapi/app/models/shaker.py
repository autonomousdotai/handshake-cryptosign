#!/usr/bin/python
# -*- coding: utf-8 -*-

from app import db
from app.models.base import BaseModel
import app.constants as CONST

class Shaker(BaseModel):
	__tablename__ = 'shaker'
	__json_public__ = ['id', 'handshake_id', 'shaker_id', 'amount', 'currency', 'side', 'odds', 'win_value']

	shaker_id = db.Column(db.Integer)
	amount = db.Column(db.Float)
	currency = db.Column(db.String(10))
	odds = db.Column(db.Float)
	win_value = db.Column(db.Float)
	side = db.Column(db.Integer,
					server_default=str(CONST.SIDE_TYPE['SUPPORT']),
					default=CONST.SIDE_TYPE['SUPPORT'])

	handshake_id = db.Column('handshake_id', db.ForeignKey('handshake.id'))

	def __repr__(self):
		return '<shaker {}>'.format(self.id)
