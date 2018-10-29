#!/usr/bin/python
# -*- coding: utf-8 -*-

from app import db
from app.models.base import BaseModel

class Match(BaseModel):
	__tablename__ = 'match'
	__json_public__ = ['id', 'homeTeamName', 'homeTeamCode', 'homeTeamFlag', 'awayTeamName', 'awayTeamCode', 'awayTeamFlag', 'date', 'reportTime', 'disputeTime', 'outcomes', 'homeScore', 'awayScore', 'name', 'public', 'market_fee', 'grant_permission', 'source_id', 'category_id', 'creator_wallet_address', 'image_url']
	__json_modifiers__ = {
        'outcomes': lambda outcomes, _: [outcome.to_json() for outcome in outcomes]
    }
	homeTeamName = db.Column(db.String(255))
	homeTeamCode = db.Column(db.String(10))
	homeTeamFlag = db.Column(db.String(512))
	awayTeamName = db.Column(db.String(255))
	awayTeamCode = db.Column(db.String(10))
	awayTeamFlag = db.Column(db.String(512))
	name = db.Column(db.String(512))
	homeScore = db.Column(db.Integer)
	awayScore = db.Column(db.Integer)
	market_fee = db.Column(db.Integer,
							server_default=str(1),
	                      	default=1)
	date = db.Column(db.BigInteger) #closingTime

	reportTime = db.Column(db.BigInteger)
	disputeTime = db.Column(db.BigInteger)
	index = db.Column(db.Integer,
							server_default=str(1),
	                      	default=1)
	public = db.Column(db.Integer,
						server_default=str(1),
						default=0)
	# this field help admin set outcome for creator
	grant_permission = db.Column(db.Integer,
						server_default=str(0),
						default=0)
	creator_wallet_address = db.Column(db.String(255))
	image_url = db.Column(db.String(512))
	category_id = db.Column('category_id', db.ForeignKey('category.id'))
	source_id = db.Column('source_id', db.ForeignKey('source.id'))
	outcomes = db.relationship('Outcome', backref='match', primaryjoin="Match.id == Outcome.match_id", lazy='dynamic')

	@classmethod
	def find_match_by_id(cls, match_id):
		return Match.query.filter_by(id=match_id).first()

	def __repr__(self):
		return '<match {}, {}, {}>'.format(self.id, self.homeTeamName, self.awayTeamName)
