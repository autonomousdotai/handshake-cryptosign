#!/usr/bin/python
# -*- coding: utf-8 -*-

from app import db
from app.models.base import BaseModel

class Outcome(BaseModel):
	__tablename__ = 'outcome'
	__json_public__ = ['id', 'name']

	name = db.Column(db.String(255))
	match_id = db.Column('match_id', db.ForeignKey('match.id'))

	def __repr__(self):
		return '<outcome {}, {}>'.format(self.id, self.name)
