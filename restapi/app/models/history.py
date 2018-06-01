#!/usr/bin/python
# -*- coding: utf-8 -*-

from app import db
from app.models.base import BaseModel

class History(BaseModel):
	__tablename__ = 'history'
	__json_public__ = ['id', 'shaker_id', 'handshake_id', 'maker_odds', 'shaker_odds', 'maker_amount', 'shaker_amount']

	shaker_id = db.Column(db.Integer)
	handshake_id = db.Column(db.Integer)
	maker_amount = db.Column(db.Float)
	maker_odds = db.Column(db.Float)
	shaker_amount = db.Column(db.Float)
	shaker_odds = db.Column(db.Float)

	def __repr__(self):
		return '<history {}>'.format(self.id)
