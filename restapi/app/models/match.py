#!/usr/bin/python
# -*- coding: utf-8 -*-

from app import db
from app.models.base import BaseModel

class Match(BaseModel):
	__tablename__ = 'match'
	__json_public__ = ['id', 'homeTeamName', 'homeTeamCode', 'homeTeamFlag', 'awayTeamName', 'awayTeamCode', 'awayTeamFlag', 'date', 'outcomes', 'homeScore', 'awayScore', 'name']	
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
	date = db.Column(db.BigInteger)
	outcomes = db.relationship('Outcome', backref='match', primaryjoin="Match.id == Outcome.match_id", lazy='dynamic')

	@classmethod
	def find_match_by_id(cls, match_id):
		return Match.query.filter_by(id=match_id).first()

	def __repr__(self):
		return '<match {}, {}, {}>'.format(self.id, self.homeTeamName, self.awayTeamName)
