#!/usr/bin/python
# -*- coding: utf-8 -*-

import app.constants as CONST

from app import db
from app.models.base import BaseModel

class OnchainTask(BaseModel):
	__tablename__ = 'onchain_task'
	__json_public__ = ['id', 'description', 'is_erc20', 'address', 'contract_name', 'method_name', 'data', 'status', 'task_id']
	
	description = db.Column(db.String(255))
	is_erc20 = db.Column(db.Integer,
							server_default=str(0),
	                      	default=0)
	address = db.Column(db.String(255))
	contract_name = db.Column(db.String(255))
	method_name = db.Column(db.String(255))
	data = db.Column(db.Text)
	task_id = db.Column(db.Integer)
	status = db.Column(db.Integer,
						server_default=str(-1),
						default=-1)

	@classmethod
	def __repr__(self):
		return '<onchain_task {}>'.format(self.id)
