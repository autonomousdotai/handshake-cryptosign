#!/usr/bin/python
# -*- coding: utf-8 -*-

import app.constants as CONST

from app import db
from app.models.base import BaseModel

class Outcome(BaseModel):
	__tablename__ = 'outcome'
	__json_public__ = ['id', 'name', 'handshakes', 'hid', 'result']
	__json_modifiers__ = {
        'handshakes': lambda handshakes, _: [handshake.to_json() for handshake in handshakes]
    }

	name = db.Column(db.String(255))
	match_id = db.Column('match_id', db.ForeignKey('match.id'))
	hid = db.Column(db.BigInteger)
	result = db.Column(db.Integer,
						server_default=str(CONST.RESULT_TYPE['PENDING']),
	                   	default=CONST.RESULT_TYPE['PENDING'])
	tx = db.Column(db.String(255))
	handshakes = db.relationship('Handshake', backref='outcome', primaryjoin="Outcome.id == Handshake.outcome_id",
	                             lazy='dynamic')

	@classmethod
	def find_outcome_by_id(cls, outcome_id):
		return Outcome.query.filter_by(id=outcome_id).first()

	@classmethod
	def find_outcome_by_hid(cls, hid):
		return Outcome.query.filter_by(hid=hid).first()

	def __repr__(self):
		return '<outcome {}, {}>'.format(self.id, self.name)
