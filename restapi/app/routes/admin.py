# -*- coding: utf-8 -*-
import os
import sys
import hashlib
import json
import app.bl.user as user_bl
import app.constants as CONST

from flask import Blueprint, request, g
from app import db, sg, s3
from datetime import datetime

from app.models import Match, Outcome, Task
from app.helpers.message import MESSAGE, CODE
from app.helpers.decorators import admin_required
from app.helpers.response import response_ok, response_error
from app.tasks import factory_reset
from flask_jwt_extended import jwt_required

admin_routes = Blueprint('admin', __name__)


@admin_routes.route('/create_market', methods=['POST'])
@admin_required
def create_market():
	try:
		fixtures_path = os.path.abspath(os.path.dirname(__file__)) + '/fixtures.json'
		data = {}
		with open(fixtures_path, 'r') as f:
			data = json.load(f)

		matches = []
		if 'fixtures' in data:
			fixtures = data['fixtures']
			for item in fixtures:
				if len(item['homeTeamName']) > 0 and len(item['awayTeamName']) > 0:
					match = Match(
								homeTeamName=item['homeTeamName'],
								awayTeamName=item['awayTeamName'],
								name='{} vs {}'.format(item['homeTeamName'], item['awayTeamName']),
								source=item['source'],
								market_fee=item['market_fee'],
								date=item['date'],
								reportTime=item['reportTime'],
								disputeTime=item['disputeTime']
							)
					matches.append(match)
					db.session.add(match)
					db.session.flush()
					
					for o in item['outcomes']:
						outcome = Outcome(
							name=o.get('name', ''),
							match_id=match.id,
							public=1
						)
						db.session.add(outcome)
						db.session.flush()

					# add Task
					task = Task(
						task_type=CONST.TASK_TYPE['REAL_BET'],
						data=json.dumps(match.to_json()),
						action=CONST.TASK_ACTION['CREATE_MARKET'],
						status=-1
					)
					db.session.add(task)
					db.session.flush()

		db.session.commit()
		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@admin_routes.route('/init_default_outcomes', methods=['POST'])
@admin_required
def init_default_outcomes():
	try:
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		for item in data:
			outcome_id = item['outcome_id']
			outcome_data = item['outcomes']
			outcome = Outcome.find_outcome_by_id(outcome_id)
			if outcome is None:
				return response_error(MESSAGE.OUTCOME_INVALID, CODE.OUTCOME_INVALID)

			if outcome.result != CONST.RESULT_TYPE['PENDING']:
				return response_error(MESSAGE.OUTCOME_HAS_RESULT, CODE.OUTCOME_HAS_RESULT)
			
			match = Match.find_match_by_id(outcome.match_id)
			for o in outcome_data:
				o['outcome_id'] = outcome_id
				o['hid'] = outcome.hid
				o['match_date'] = match.date
				o['match_name'] = match.name
				o['outcome_name'] = outcome.name

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


@admin_routes.route('/factory_reset', methods=['POST'])
@jwt_required
def reset_all():
	try:
		factory_reset.delay()
		return response_ok()
	except Exception, ex:
		return response_error(ex.message)


@admin_routes.route('/test_market', methods=['POST'])
def test_market():
	try:
		data = request.data
		matches = []
		if 'fixtures' in data:
			fixtures = data['fixtures']
			for item in fixtures:
				if len(item['homeTeamName']) > 0 and len(item['awayTeamName']) > 0:
					match = Match(
								homeTeamName=item['homeTeamName'],
								awayTeamName=item['awayTeamName'],
								name='{} vs {}'.format(item['homeTeamName'], item['awayTeamName']),
								source=item['source'],
								market_fee=item['market_fee'],
								date=item['date'],
								reportTime=item['reportTime'],
								disputeTime=item['disputeTime']
							)
					matches.append(match)
					db.session.add(match)
					db.session.flush()
					
					for o in item['outcomes']:
						outcome = Outcome(
							name=o.get('name', ''),
							match_id=match.id,
							public=1
						)
						db.session.add(outcome)
						db.session.flush()

					# add Task
					task = Task(
						task_type=CONST.TASK_TYPE['REAL_BET'],
						data=json.dumps(match.to_json()),
						action=CONST.TASK_ACTION['CREATE_MARKET'],
						status=-1
					)
					db.session.add(task)
					db.session.flush()

		db.session.commit()
		return response_ok()
	except Exception, ex:
		return response_error(ex.message)