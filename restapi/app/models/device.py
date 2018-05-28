#!/usr/bin/python
# -*- coding: utf-8 -*-


from app import db, g
from app.models.base import BaseModel

import app.constants as CONST

#TODO: do we need save device to redis???
class Device(BaseModel):
	__tablename__ = 'device'
	__json_public__ = ['id', 'device_token', 'device_type']

	device_token = db.Column(db.String(255))
	device_type = db.Column(db.String(25))
	user_id = db.Column('user_id', db.ForeignKey('user.id'))

	@classmethod
	def find_devices_with_user_id(cls, user_id):
		return Device.query.filter_by(user_id=user_id).all()

	@classmethod
	def find_device_with_device_id(cls, device_id):
		return Device.query.filter_by(device_id=device_id).all()

	@classmethod
	def find_device_with_device_id_and_user_id(cls, device_id, user_id):
		return Device.query.filter_by(id=device_id, user_id=user_id).first()

	@classmethod
	def find_device_with_device_token_and_user_id(cls, device_token, user_id):
		return Device.query.filter_by(device_token=device_token, user_id=user_id).all()

	def __repr__(self):
		return '<device {}>'.format(self.id)
