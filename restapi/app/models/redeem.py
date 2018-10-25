#!/usr/bin/python
# -*- coding: utf-8 -*-

from app import db
from app.models.base import BaseModel
from sqlalchemy import func

class Redeem(BaseModel):
	__tablename__ = 'redeem'
	__json_public__ = ['id', 'used_user']
	
	code = db.Column(db.String(255), unique=True, nullable=False)
	used_user = db.Column(db.Integer,
							server_default=str(0),
							default=0)

	@classmethod
	def find_redeem_by_code(cls, code):
		return Redeem.query.filter(Redeem.code == func.binary(code)).first()

	@classmethod
	def find_redeem_by_user(cls, user_id):
		return Redeem.query.filter(Redeem.used_user == user_id).first()

	def __repr__(self):
		return '<redeem {}>'.format(self.id)
