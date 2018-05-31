#!/usr/bin/python
# -*- coding: utf-8 -*-

from app import db
from app.models.base import BaseModel

class History(BaseModel):
	__tablename__ = 'history'
	__json_public__ = ['id', 'shaker_id', 'handshake_id']

	def __repr__(self):
		return '<history {}>'.format(self.id)
