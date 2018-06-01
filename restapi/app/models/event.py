#!/usr/bin/python
# -*- coding: utf-8 -*-


from app import db, g
from app.models.base import BaseModel

import app.constants as CONST

class Event(BaseModel):
	__tablename__ = 'event'
	__json_public__ = ['id', 'address', 'event_name', 'value', 'block', 'log_index']

	address = db.Column(db.String(255))
	event_name = db.Column(db.String(50))
	value = db.Column(db.Text)
	block = db.Column(db.BigInteger)
	log_index = db.Column(db.Integer)	

	def __repr__(self):
		return '<event {}>'.format(self.id)
