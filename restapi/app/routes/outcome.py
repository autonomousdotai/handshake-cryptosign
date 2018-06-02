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

		match = Match.find_match_by_id(match_id)
		if match is None:
			return response_error(MESSAGE.MATCH_NOT_FOUND)

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


@outcome_routes.route('/remove/<int:outcome_id>', methods=['POST'])
@login_required
def remove(outcome_id):
	try:
		outcome = Outcome.find_outcome_by_id(outcome_id)
		if outcome is not None:
			db.session.delete(outcome)
			db.session.commit()
			return response_ok("{} has been deleted!".format(outcome.id))
		else:
			return response_error(MESSAGE.INVALID_OUTCOME)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@outcome_routes.route('/report/<int:outcome_id>', methods=['POST'])
@login_required
def report(outcome_id):
	try:
		data = request.json
		if data is None:
			raise Exception(MESSAGE.INVALID_DATA)

		outcome = Outcome.find_outcome_by_id(outcome_id)
		if outcome is not None:
			side = data.get('side', -2)
			if(side == -2):
				return response_error(MESSAGE.INVALID_OUTCOME)

			# TODO: call nodejs
			return response_ok()
		else:
			return response_error(MESSAGE.INVALID_OUTCOME)


	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
