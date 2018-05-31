#!/usr/bin/python
# -*- coding: utf-8 -*-
import app.constants as CONST
import time

from app import db
from app.models.base import BaseModel

class Handshake(BaseModel):
	__tablename__ = 'handshake'
	__json_public__ = ['id', 'extra_data', 'chain_id', 'is_private', 'description', 'status', 'bk_status', 'user_id', 'odds', 'amount', 'remaining_amount', 'currency', 'side', 'shakers', 'outcome_id']
	__json_modifiers__ = {
        'shakers': lambda shakers, _: [shaker.to_json() for shaker in shakers]
    }

	hs_type = db.Column(db.Integer)
	extra_data = db.Column(db.Text)
	chain_id = db.Column(db.Integer,
						server_default=str(CONST.BLOCKCHAIN_NETWORK['RINKEBY']),
						default=CONST.BLOCKCHAIN_NETWORK['RINKEBY'])
	state = db.Column(db.Integer,
						server_default=str(CONST.STATE_TYPE['PUBLISH']),
	                   	default=CONST.STATE_TYPE['PUBLISH'])
	is_private = db.Column(db.Integer,
						server_default=str(CONST.COMMUNITY_TYPE['PUBLIC']),
	                   	default=CONST.COMMUNITY_TYPE['PUBLIC'])
	description = db.Column(db.Text)
	status = db.Column(db.Integer,
	                   server_default=str(CONST.Handshake['STATUS_PENDING']),
	                   default=CONST.Handshake['STATUS_PENDING'])
	bk_status = db.Column(db.Integer,
	                      server_default=str(CONST.Handshake['STATUS_PENDING']),
	                      default=CONST.Handshake['STATUS_PENDING'])
	shake_count = db.Column(db.Integer)
	view_count = db.Column(db.Integer)
	comment_count = db.Column(db.Integer)
	odds = db.Column(db.Float)
	amount = db.Column(db.Float)
	remaining_amount = db.Column(db.Float)
	win_value = db.Column(db.Float)
	currency = db.Column(db.String(10))
	side = db.Column(db.Integer,
						server_default=str(CONST.SIDE_TYPE['SUPPORT']),
	                   	default=CONST.SIDE_TYPE['SUPPORT'])
	user_id = db.Column('user_id', db.ForeignKey('user.id'))
	outcome_id = db.Column('outcome_id', db.ForeignKey('outcome.id'))
	shakers = db.relationship('Shaker', backref='handshake', primaryjoin="Handshake.id == Shaker.handshake_id",
	                             lazy='dynamic')

	@classmethod
	def find_handshake_by_id(cls, _id):
		handshake = Handshake.query.filter_by(id=_id).first()
		if handshake is not None:
			return handshake
		return None

	def __repr__(self):
		return '<Handshake [id] {}>'.format(self.id)
