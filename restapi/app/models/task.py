#!/usr/bin/python
# -*- coding: utf-8 -*-

import app.constants as CONST

from app import db
from app.models.base import BaseModel

class Task(BaseModel):
	__tablename__ = 'task'
	__json_public__ = ['id', 'task_type', 'data', 'status']
	
	task_type = db.Column(db.String(255))
	data = db.Column(db.Text)
	action = db.Column(db.String(100))
	status = db.Column(db.Integer,
						server_default=str(-1),
	                   	default=-1)

	def __repr__(self):
		return '<task {}, {}>'.format(self.id, self.task_type)
