#!/usr/bin/python
# -*- coding: utf-8 -*-


from app import db, g
from app.models.base import BaseModel
from sqlalchemy import asc

class Industries(BaseModel):
	__tablename__ = 'industries'
	__json_public__ = ['id', 'name', 'backgroundColor', 'desc', 'order_id', 'public', 'message']

	name = db.Column(db.String(255))
	backgroundColor = db.Column(db.String(25))
	desc = db.Column(db.Text)
	public = db.Column(db.Integer, server_default=str(0), default=0)
	order_id = db.Column(db.Integer, server_default=str(0), default=0)
	message = db.Column(db.Text)

	@classmethod
	def find_all_industries_with_public_type(cls, _public):
		return Industries.query.filter_by(public=_public).order_by(asc(Industries.order_id)).all()

	@classmethod
	def find_industries_with_id(cls, industries_id):
		return Industries.query.filter_by(id=industries_id).first()

	def __repr__(self):
		return '<industries {}>'.format(self.id)
