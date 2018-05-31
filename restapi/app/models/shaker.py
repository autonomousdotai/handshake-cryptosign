#!/usr/bin/python
# -*- coding: utf-8 -*-

from app import db
from app.models.base import BaseModel

class Shaker(BaseModel):
	__tablename__ = 'shaker'
	__json_public__ = ['id', 'handshake_id', 'shaker_id', 'amount', 'is_support', 'odds', 'win_value']

	def __repr__(self):
		return '<shaker {}>'.format(self.id)
