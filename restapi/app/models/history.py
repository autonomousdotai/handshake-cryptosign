#!/usr/bin/python
# -*- coding: utf-8 -*-

from app import db
from app.models.base import BaseModel

class History(BaseModel):
	__tablename__ = 'history'
	__json_public__ = ['id', 'shaker_id', 'handshake_id']

	shaker_id = db.Column(db.Integer)
	handshake_id = db.Column(db.Integer)
	
	def __repr__(self):
		return '<history {}>'.format(self.id)
