from flask import Blueprint, request, current_app as app
from app.helpers.response import response_ok, response_error
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Device

device_routes = Blueprint('device', __name__)


@device_routes.route('/', methods=['GET'])
@jwt_required
def device():
	try:
		user_id = get_jwt_identity()
		user = User.find_user_with_id(user_id)

		data = []
		for device in user.devices:
			data.append(device.to_json())

		return response_ok(data)
	except Exception, ex:
		return response_error(ex.message)

@device_routes.route('/update', methods=['GET'])
def update():
	required_mobile_min_version = app.config['MOBILE_MIN_VERSION']
	mobile_current_version = app.config['MOBILE_CURRENT_VERSION']
	result = {'min_version': required_mobile_min_version, 'version': mobile_current_version}
	return response_ok(result)

@device_routes.route('/add', methods=['POST'])
@jwt_required
def add_device():
	try:
		user_id = get_jwt_identity()
		device_token = request.form.get('device_token')
		device_type = request.form.get('device_type')

		user = User.find_user_with_id(user_id)
		if user is not None:
			device = Device.find_device_with_device_token_and_user_id(device_token, user_id)
			if device is None:
				device = Device(device_token=device_token, device_type=device_type)
				user.devices.append(device)
				db.session.add(device)
				db.session.commit()
		return response_ok(device.to_json())
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@device_routes.route('/remove', methods=['POST'])
@jwt_required
def remove_device():
	try:
		user_id = get_jwt_identity()
		device_token = request.form.get('device_token')

		device = Device.find_device_with_device_token_and_user_id(device_token, user_id)
		if device is not None:
			db.session.delete(device)
			db.session.commit()
			return response_ok("{} has been deleted!".format(device.id))
		else:
			return response_error("Please check your device id")

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
