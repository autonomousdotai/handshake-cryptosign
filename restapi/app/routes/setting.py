import os
import json
import app.constants as CONST

from flask import Blueprint, request, current_app as app
from app.helpers.response import response_ok, response_error
from app.helpers.decorators import login_required, admin_required
from app import db
from app.models import Setting
from app.helpers.message import MESSAGE

setting_routes = Blueprint('setting', __name__)

@setting_routes.route('/', methods=['GET'])
@login_required
def settings():
	try:
		settings = Setting.query.all()
		data = []

		for setting in settings:
			data.append(setting.to_json())

		return response_ok(data)
	except Exception, ex:
		return response_error(ex.message)


@setting_routes.route('/add', methods=['POST'])
@login_required
@admin_required
def add():
	try:
		data = request.json
		if data is None:
			raise Exception(MESSAGE.INVALID_DATA)

		settings = []
		response_json = []
		for item in data:
			setting = Setting(
				name=item['name'],
				status=int(item['status'])
			)
			settings.append(setting)
			db.session.add(setting)
			db.session.flush()

			response_json.append(setting.to_json())

		db.session.add_all(settings)
		db.session.commit()

		return response_ok(response_json)
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@setting_routes.route('/remove/<int:id>', methods=['POST'])
@login_required
@admin_required
def remove(id):
	try:
		setting = Setting.find_setting_by_id(id)
		if setting is not None:
			db.session.delete(setting)
			db.session.commit()
			return response_ok(message="{} has been deleted!".format(setting.id))
		else:
			return response_error(message=MESSAGE.INVALID_DATA)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@setting_routes.route('/update/<int:id>', methods=['POST'])
@login_required
@admin_required
def update(id):
	try:
		data = request.json
		if data is None:
			raise Exception(MESSAGE.INVALID_DATA)

		setting = Setting.find_setting_by_id(id)
		if setting is not None:
			status = int(data['status'])
			setting.status = status
			db.session.commit()

			return response_ok(message='{} has been updated'.format(setting.id))
		else:
			return response_error(message=MESSAGE.INVALID_DATA)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)