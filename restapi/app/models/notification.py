#!/usr/bin/python
# -*- coding: utf-8 -*-

import app.constants as CONST

from app import db
from app.models.base import BaseModel

class Notification(BaseModel):
	__tablename__ = 'notification'
	__json_public__ = ['id', 'name', 'type', 'status', 'start_time', 'expire_time', 'to', 'data']

	name = db.Column(db.String(255))
	to = db.Column(db.String(512))
	data = db.Column(db.Text)
	type = db.Column(db.Integer,
					server_default=str(CONST.COMMUNITY_TYPE['PUBLIC']),
					default=CONST.COMMUNITY_TYPE['PRIVATE'])
	status = db.Column(db.Integer,
					server_default=str(CONST.NOTIF_STATUS['INACTIVE']),
					default=CONST.NOTIF_STATUS['INACTIVE'])
	start_time = db.Column(db.DateTime, default=0)
	expire_time = db.Column(db.DateTime, default=0)

	@classmethod
	def find_public_notification_by_status(cls, status):
		return Notification.query.filter(Notification.type == CONST.COMMUNITY_TYPE['PUBLIC'], Notification.status == status, Notification.expire_time > db.func.utc_timestamp()).all()
	
	@classmethod
	def find_notif_by_id(cls, notif_id):
    		return Notification.query.filter_by(id=notif_id).first()

	def __repr__(self):
		return '<notification {}, {}, {}>'.format(self.id, self.name, self.type)
 