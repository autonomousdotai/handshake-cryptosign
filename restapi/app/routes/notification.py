from flask import Blueprint, request, current_app as app
from app.helpers.response import response_ok, response_error
from app.helpers.decorators import login_required, admin_required
from app import db
from app.models import Notification
from app.helpers.message import MESSAGE, CODE
from sqlalchemy import or_, and_, text, func
from app.helpers.utils import local_to_utc, utc_to_local
from app.core import firebase
from datetime import datetime

import re
import json
import time
import app.constants as CONST

notif_routes = Blueprint('notif', __name__)


@notif_routes.route('/', methods=['GET'])
@login_required
def notifications():
	try:
		notifs = Notification.find_public_notification_by_status(CONST.NOTIF_STATUS['ACTIVE'])
		data = []
		for notif in notifs:
			notif.expire_time = time.mktime(notif.expire_time.timetuple())
			notif.start_time = time.mktime(notif.start_time.timetuple())
			data.append(notif.to_json())

		return response_ok(data)
	except Exception, ex:
		return response_error(ex.message)


@notif_routes.route('/add', methods=['POST'])
@admin_required
def add():
	try:
		uid = int(request.headers['Uid'])
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		response_json = []
		for item in data:
			if 'start_time' not in item or 'expire_time' not in item or item['start_time'] >= item['expire_time']:
				return response_error(MESSAGE.NOTIF_TIME_INVALID, CODE.INVALID_DATA)

			notif = Notification(
				name 			= item['name'],
				start_time 		= datetime.fromtimestamp(item['start_time']),
				expire_time 	= datetime.fromtimestamp(item['expire_time']),
				to 				= "" if 'to' not in item else item["to"],
				data 			= "{}" if 'to' not in data else item["data"],
				type 			= CONST.COMMUNITY_TYPE['PRIVATE'] if 'type' not in item else int(item["type"]),
				status 			= NOTIF_STATUS['INACTIVE'] if 'status' not in item else int(item["status"]),
				modified_user_id=int(uid),
				created_user_id	=int(uid)
			)

			db.session.add(notif)
			db.session.flush()

			# Send firebase
			if notif.status == CONST.NOTIF_STATUS['ACTIVE'] and notif.type == CONST.COMMUNITY_TYPE['PUBLIC']:
				firebase.push_data(notif.data, uid)

			response_json.append(notif.to_json())

		db.session.commit()
		return response_ok(response_json)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)

@notif_routes.route('/remove/<int:notif_id>', methods=['DELETE'])
@admin_required
def remove(notif_id):
	try:
		notif = Notification.find_notif_by_id(notif_id)
		if notif is not None:
			db.session.delete(notif)
			db.session.commit()
			return response_ok("{} has been deleted!".format(notif.id))
		else:
			return response_error(MESSAGE.NOTIF_INVALID, CODE.NOTIF_INVALID)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)

@notif_routes.route('/edit/<int:notif_id>', methods=['PUT'])
@admin_required
def edit(notif_id):
	try:
		uid = int(request.headers['Uid'])
		notif = Notification.find_notif_by_id(notif_id)
		if notif is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		# now_utc = local_to_utc(datetime.now().timetuple())
		data = request.json

		if 'name' in data:
			notif.name = data['name']
		# if 'start_time'in data and data['start_time'] < time.mktime(utc_to_local(notif.start_time.timetuple())):
		if 'start_time'in data:
			notif.start_time = datetime.fromtimestamp(data['start_time'])
		# if 'expire_time' in data and data['expire_time'] > data['start_time']:
		if 'expire_time' in data:
			notif.expire_time = datetime.fromtimestamp(data['expire_time'])
		if 'to' in data:
			notif.to = data['to']
		if 'type' in data:
			notif.type = data['type']
		if 'status' in data:
			notif.status = data['status']

		notif.modified_user_id = uid
		notif.date_modified = db.func.utc_timestamp()
		db.session.commit()

		notif.start_time = time.mktime(notif.start_time.utctimetuple())
		notif.expire_time = time.mktime(notif.expire_time.utctimetuple())

		return response_ok(notif.to_json())
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)

# TODO: Resend notif