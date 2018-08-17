# -*- coding: utf-8 -*-
import os
import sys
import hashlib
import json
import app.bl.user as user_bl
import app.constants as CONST
import app.bl.match as match_bl
import app.bl.contract as contract_bl

from flask import Blueprint, request, g
from app import db, sg, s3
from datetime import datetime
from app.helpers.utils import local_to_utc
from sqlalchemy import and_

from app.models import Match, Outcome, Task, Handshake, Shaker, Contract
from app.helpers.message import MESSAGE, CODE
from app.helpers.decorators import admin_required, dev_required
from app.helpers.response import response_ok, response_error
from app.tasks import update_contract_feed
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

		contract = contract_bl.get_active_smart_contract()
		if contract is None:
			return response_error(MESSAGE.CONTRACT_EMPTY_VERSION, CODE.CONTRACT_EMPTY_VERSION)

		matches = []
		if 'fixtures' in data:
			fixtures = data['fixtures']
			for item in fixtures:
				print item
				match = Match(
							homeTeamName=item['homeTeamName'],
							awayTeamName=item['awayTeamName'],
							name=item['name'],
							market_fee=item['market_fee'],
							source_id=int(item['source_id']),
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
						contract_id=contract.id,
						public=1
					)
					db.session.add(outcome)
					db.session.flush()

				# add Task
				task = Task(
					task_type=CONST.TASK_TYPE['REAL_BET'],
					data=json.dumps(match.to_json()),
					action=CONST.TASK_ACTION['CREATE_MARKET'],
					status=-1,
					contract_address=g.PREDICTION_SMART_CONTRACT,
					contract_json=g.PREDICTION_JSON
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
					status=-1,
					contract_address=g.PREDICTION_SMART_CONTRACT,
					contract_json=g.PREDICTION_JSON
				)
				db.session.add(task)
				db.session.flush()
		
		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@admin_routes.route('/match/report', methods=['GET'])
@jwt_required
def matches_need_report_by_admin():
	try:
		response = []
		matches = []

		t = datetime.now().timetuple()
		seconds = local_to_utc(t)
		
		matches_by_admin = db.session.query(Match).filter(Match.date < seconds, Match.reportTime >= seconds, Match.id.in_(db.session.query(Outcome.match_id).filter(and_(Outcome.created_user_id.is_(None), Outcome.result == -1, Outcome.hid != None)).group_by(Outcome.match_id))).order_by(Match.index.desc(), Match.date.asc()).all()
		matches_disputed = db.session.query(Match).filter(Match.id.in_(db.session.query(Outcome.match_id).filter(and_(Outcome.result == CONST.RESULT_TYPE['DISPUTED'], Outcome.hid != None)).group_by(Outcome.match_id))).order_by(Match.index.desc(), Match.date.asc()).all()

		for match in matches_by_admin:
			match_json = match.to_json()
			arr_outcomes = []
			for outcome in match.outcomes:
				if outcome.created_user_id is None:
					arr_outcomes.append(outcome.to_json())

			match_json["outcomes"] = arr_outcomes
			response.append(match_json)

		for match in matches_disputed:
			match_json = match.to_json()
			arr_outcomes = []
			for outcome in match.outcomes:
				if outcome.result == CONST.RESULT_TYPE['DISPUTED']:
					outcome_json = outcome.to_json()
					arr_outcomes.append(outcome_json)

			match_json["outcomes"] = arr_outcomes if len(arr_outcomes) > 0 else []
			match_json["is_disputed"] = 1
			response.append(match_json)

		return response_ok(response)
	except Exception, ex:
		return response_error(ex.message)


@admin_routes.route('match/report/<int:match_id>', methods=['POST'])
@jwt_required
def report_match(match_id):
	try:
		t = datetime.now().timetuple()
		seconds = local_to_utc(t)
		disputed = False
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		match = db.session.query(Match).filter(Match.date > seconds, Match.id == match_id).first()
		if match is not None:
			result = data['result']
			if result is None:
				return response_error(MESSAGE.MATCH_RESULT_EMPTY)

			for item in result:
				if 'side' not in item:
					return response_error(MESSAGE.OUTCOME_INVALID_RESULT)

				if 'outcome_id' not in item:
					return response_error(MESSAGE.OUTCOME_INVALID)

				outcome = Outcome.find_outcome_by_id(item['outcome_id'])
				if outcome is not None:
					message, code = match_bl.is_able_to_set_result_for_outcome(outcome)
					if message is not None and code is not None:
						return message, code
					
					if outcome.result == CONST.RESULT_TYPE['DISPUTED']:
						disputed = True

					outcome.result = CONST.RESULT_TYPE['PROCESSING']

				else:
					return response_error(MESSAGE.OUTCOME_INVALID)

				contract = Contract.find_contract_by_id(outcome.contract_id)
				if contract is None:
					return response_error(MESSAGE.CONTRACT_INVALID, CODE.CONTRACT_INVALID)

				report = {}
				report['offchain'] = CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + ('resolve' if disputed else 'report') + str(outcome.id) + '_' + str(item['side'])
				report['hid'] = outcome.hid
				report['outcome_id'] = outcome.id
				report['outcome_result'] = item['side']

				task = Task(
					task_type=CONST.TASK_TYPE['REAL_BET'],
					data=json.dumps(report),
					action=CONST.TASK_ACTION['REPORT' if disputed else 'RESOLVE'],
					status=-1,
					contract_address= contract.contract_address,
					contract_json= contract.contract_json
				)

				db.session.add(task)
				db.session.flush()

			db.session.commit()
			return response_ok(match.to_json())
		else:
			return response_error(MESSAGE.MATCH_NOT_FOUND, CODE.MATCH_NOT_FOUND)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@admin_routes.route('/change-contract', methods=['POST'])
@admin_required
def change_contract():
	""" Change contract: 
    This is used for change contract json and contract json.
	Input: 
		from_id
		to_id
		contract_address
		contract_json
    """
	try:
		data = request.json
		from_id = int(data.get('from', 0))
		to_id = int(data.get('to', 0))
		contract_address = data.get('contract_address', None)
		contract_json = data.get('contract_json', None)

		if from_id > to_id or contract_address is None or contract_json is None or len(contract_address) == 0 or len(contract_json) == 0:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		handshakes = db.session.query(Handshake).filter(Handshake.id >= from_id, Handshake.id <= to_id).all()
		arr_id = []
		for hs in handshakes:
			if hs.contract_address is None and hs.contract_json is None:
				arr_id.append(hs.id)
				hs.contract_address = contract_address
				hs.contract_json = contract_json
				db.session.flush()
				
				shakers = db.session.query(Shaker).filter(Shaker.handshake_id == hs.id).all()
				for sk in shakers:
					sk.contract_address = contract_address
					sk.contract_json = contract_json
					db.session.flush()
		db.session.commit()
		if len(arr_id) > 0:
			update_contract_feed.delay(arr_id, contract_address, contract_json)
		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@admin_routes.route('/source/approve/<int:source_id>', methods=['POST'])
@jwt_required
def approve_source(source_id):
	try:
		
		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)