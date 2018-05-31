from flask import Blueprint, request, current_app as app
from app.helpers.response import response_ok, response_error
from app.helpers.decorators import login_required
from app import db
from app.models import User, Outcome, Match
from app.helpers.message import MESSAGE

outcome_routes = Blueprint('outcome', __name__)


@outcome_routes.route('/', methods=['GET'])
@login_required
def outcomes():
	try:
		outcomes = Outcome.query.all()
		data = []
		for outcome in outcomes:
			data.append(outcome.to_json())

		return response_ok(data)
	except Exception, ex:
		return response_error(ex.message)


@outcome_routes.route('/add/<int:match_id>', methods=['POST'])
@login_required
def add(match_id):
	try:
		data = request.json
		if data is None:
			raise Exception(MESSAGE.INVALID_DATA)

		

		outcomes = []
		for item in data:
			outcome = Outcome(
				name=item['name'],
				match_id=match_id
			)
			outcomes.append(outcome)

		db.session.add_all(outcomes)
		db.session.commit()

		return response_ok()

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@outcome_routes.route('/remove', methods=['POST'])
@login_required
def remove():
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
