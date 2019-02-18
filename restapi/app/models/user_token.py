from app import db
from app.models.base import BaseModel
from sqlalchemy import func

import app.constants as CONST
import json


class UserToken(BaseModel):
	__tablename__ = 'user_token'
	__json_public__ = ['id', 'user_id', 'address', 'token_id', 'status', 'hash']

	user_id = db.Column('user_id', db.ForeignKey('user.id'), primary_key=True)
	address = db.Column(db.String(255))
	token_id = db.Column('token_id', db.ForeignKey('token.id'), primary_key=True)
	status = db.Column(db.Integer,
							server_default=str(CONST.USER_TOKEN_STATUS['PENDING']),
							default=CONST.USER_TOKEN_STATUS['PENDING'])
	hash = db.Column(db.String(255))

	@classmethod
	def find_by_user_id_and_address(cls, user_id, address):
		return UserToken.query.filter(UserToken.user_id == user_id, UserToken.address== func.binary(address)).first()

	@classmethod
	def find_user_token_with_id(cls, _id):
		return UserToken.query.filter_by(id=_id).first()

	def __repr__(self):
		return '<UserToken {}>'.format(self.id)
