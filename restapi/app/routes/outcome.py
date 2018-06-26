from flask import Blueprint, request, current_app as app
from app.helpers.response import response_ok, response_error
from app.helpers.decorators import login_required, admin_required
from app import db
from app.models import User, Outcome, Match, Task
from app.helpers.message import MESSAGE, CODE

import json
import app.constants as CONST
import app.bl.outcome as outcome_bl

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


@outcome_routes.route('/init_default_outcomes', methods=['POST'])
@login_required
@admin_required
def init_default_outcomes():
	try:
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		for item in data:
			outcome_id = item['outcome_id']
			outcome_data = item['outcomes']
			for o in outcome_data:
				o['id'] = outcome_id
				task = Task(
					task_type=CONST.TASK_TYPE['REAL_BET'],
					data=json.dumps(o),
					action=CONST.TASK_ACTION['INIT'],
					status=-1
				)
				db.session.add(task)
				db.session.flush()
		
		return response_ok()
	except Exception, ex:
		return response_error(ex.message)


@outcome_routes.route('/add/<int:match_id>', methods=['POST'])
@login_required
def add(match_id):
	try:
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		match = Match.find_match_by_id(match_id)
		if match is None:
			return response_error(MESSAGE.MATCH_NOT_FOUND, CODE.MATCH_NOT_FOUND)

		outcomes = []
		response_json = []
		for item in data:
			outcome = Outcome(
				name=item['name'],
				match_id=match_id
			)
			db.session.add(outcome)
			db.session.flush()
			
			outcomes.append(outcome)
			response_json.append(outcome.to_json())

		db.session.add_all(outcomes)
		db.session.commit()

		return response_ok(response_json)

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
			return response_error(MESSAGE.OUTCOME_INVALID, CODE.OUTCOME_INVALID)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
