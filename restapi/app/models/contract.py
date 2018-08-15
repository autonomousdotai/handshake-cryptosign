#!/usr/bin/python
# -*- coding: utf-8 -*-

import app.constants as CONST

from app import db
from app.models.base import BaseModel

class Contract(BaseModel):
	__tablename__ = 'contract'
	__json_public__ = ['id', 'contract_name', 'contract_address', 'json_name']
	
	contract_name = db.Column(db.String(255))
	contract_address = db.Column(db.String(255))
	json_name = db.Column(db.String(50))
	outcomes = db.relationship('Outcome', backref='contract', primaryjoin="Contract.id == Outcome.contract_id", lazy='dynamic')

	def find_contract_by_id(cls, contract_id):
		return db.session.query(Contract).filter_by(id=contract_id).first()

	def __repr__(self):
		return '<contract {}, {}>'.format(self.id, self.address)
