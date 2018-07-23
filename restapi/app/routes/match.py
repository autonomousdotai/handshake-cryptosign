import os
import json
import requests
import app.constants as CONST
import app.bl.match as match_bl

from sqlalchemy import and_
from flask_jwt_extended import jwt_required
from flask import g, Blueprint, request, current_app as app
from datetime import datetime
from app.helpers.response import response_ok, response_error
from app.helpers.decorators import login_required, admin_required
from app.helpers.utils import local_to_utc
from app.bl.match import is_validate_match_time
from app import db
from app.models import User, Match, Outcome, Task
from app.helpers.message import MESSAGE, CODE

match_routes = Blueprint('match', __name__)

@match_routes.route('/', methods=['GET'])
@login_required
def matches():
	try:
		report = int(request.args.get('report', 0))
		response = []
		matches = []

		t = datetime.now().timetuple()
		seconds = local_to_utc(t)

		if report == 1:
			matches = db.session.query(Match).filter(Match.date <= seconds, Match.id.in_(db.session.query(Outcome.match_id).filter(and_(Outcome.result == -1, Outcome.hid != None)).order_by(Outcome.date_created.desc()).group_by(Outcome.match_id))).all()
		else:
			matches = db.session.query(Match).filter(Match.date > seconds, Match.id.in_(db.session.query(Outcome.match_id).filter(and_(Outcome.result == -1, Outcome.hid != None)).order_by(Outcome.date_created.desc()).group_by(Outcome.match_id))).all()
			
		print matches

		for match in matches:	
			#  find best odds which match against
			match_json = match.to_json()
			
			total_users = db.engine.execute('SELECT count(shaker_id) AS total FROM (SELECT shaker.shaker_id FROM outcome JOIN handshake ON outcome.id = handshake.outcome_id JOIN shaker ON handshake.id = shaker.handshake_id WHERE outcome.match_id = {} GROUP BY shaker_id) AS tmp'.format(match.id)).scalar()
			match_json["total_users"] = total_users

			total_bets = db.engine.execute('SELECT count(id) AS total FROM (SELECT shaker.id FROM outcome JOIN handshake ON outcome.id = handshake.outcome_id JOIN shaker ON handshake.id = shaker.handshake_id WHERE outcome.match_id = {}) AS tmp'.format(match.id)).scalar()
			match_json["total_bets"] = total_bets

			arr_outcomes = []
			for outcome in match.outcomes:
				outcome_json = outcome.to_json()
				odds, amount = match_bl.find_best_odds_which_match_support_side(outcome.id)
				outcome_json["market_odds"] = odds
				outcome_json["market_amount"] = amount

				if report == 1:
					if outcome.result != CONST.RESULT_TYPE['PROCESSING']:
						arr_outcomes.append(outcome_json)
				else:
					arr_outcomes.append(outcome_json)

			if len(arr_outcomes) > 0:
				match_json["outcomes"] = arr_outcomes
			else:
				match_json["outcomes"] = []
			response.append(match_json)

		return response_ok(response)
	except Exception, ex:
		return response_error(ex.message)


@match_routes.route('/user/<int:user_id>', methods=['POST'])
@login_required
def matches_for_user(user_id):
	try:
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		public = int(data.get('public', 1))
		response = []

		matches = db.session.query(Match).filter(Match.id.in_(db.session.query(Outcome.match_id).filter(and_(Outcome.created_user_id==user_id, Outcome.public==public)))).all()
		for match in matches:
			#  find best odds which match against
			match_json = match.to_json()

			arr_outcomes = []
			for outcome in match.outcomes:
				if outcome.result == -1 and outcome.hid is not None:
					outcome_json = outcome.to_json()
					odds, amount = match_bl.find_best_odds_which_match_support_side(outcome.id)
					outcome_json["market_odds"] = odds
					outcome_json["market_amount"] = amount
					arr_outcomes.append(outcome_json)
			
			if len(arr_outcomes) > 0:
				match_json["outcomes"] = arr_outcomes
				response.append(match_json)

		return response_ok(response)
	except Exception, ex:
		return response_error(ex.message)


@match_routes.route('/add', methods=['POST'])
@login_required
def add():
	try:
		uid = int(request.headers['Uid'])

		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		matches = []
		response_json = []
		for item in data:

			if match_bl.is_validate_match_time(item) == False:				
				return response_error(MESSAGE.MATCH_INVALID_TIME, CODE.MATCH_INVALID_TIME)

			match = Match(
				homeTeamName=item['homeTeamName'],
				homeTeamCode=item['homeTeamCode'],
				homeTeamFlag=item['homeTeamFlag'],
				awayTeamName=item['awayTeamName'],
				awayTeamCode=item['awayTeamCode'],
				awayTeamFlag=item['awayTeamFlag'],
				name=item['name'],
				market_fee=int(item['market_fee']),
				date=item['date'],
				reportTime=item['reportTime'],
				disputeTime=item['disputeTime']
			)
			matches.append(match)
			db.session.add(match)
			db.session.flush()

			if 'outcomes' in item:
				for outcome_data in item['outcomes']:
					outcome = Outcome(
						name=outcome_data['name'],
						match_id=match.id,
						public=item.get('public', 0),
						modified_user_id=uid,
						created_user_id=uid
					)
					db.session.add(outcome)
					db.session.flush()

			response_json.append(match.to_json())

		db.session.commit()

		return response_ok(response_json)
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@match_routes.route('/remove/<int:id>', methods=['POST'])
@login_required
@admin_required
def remove(id):
	try:
		match = Match.find_match_by_id(id)
		if match is not None:
			db.session.delete(match)
			db.session.commit()
			return response_ok(message="{} has been deleted!".format(match.id))
		else:
			return response_error(MESSAGE.MATCH_NOT_FOUND)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)

@match_routes.route('/report/<int:match_id>', methods=['POST'])
@login_required
@jwt_required
def report(match_id):
	try:
		dispute = int(request.args.get('dispute', 0))
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		match = Match.find_match_by_id(match_id)
		if match is not None:
			result = data['result']
			if result is None:
				return response_error(MESSAGE.MATCH_RESULT_EMPTY)
			
			if not match_bl.is_exceed_closing_time(match.id):
				return response_error(MESSAGE.MATCH_CANNOT_SET_RESULT)

			for item in result:
				if 'side' not in item:
					return response_error(MESSAGE.OUTCOME_INVALID_RESULT)
				
				if 'outcome_id' not in item:
					return response_error(MESSAGE.OUTCOME_INVALID)

				outcome = Outcome.find_outcome_by_id(item['outcome_id'])
				if outcome is not None:
					if outcome.result > CONST.RESULT_TYPE['PENDING']:
						return response_error(MESSAGE.OUTCOME_HAS_RESULT)

					if outcome.result == CONST.RESULT_TYPE['PROCESSING']:
						return  response_error(MESSAGE.OUTCOME_REPORTED)

					if dispute == 1 and outcome.result != CONST.RESULT_TYPE['DISPUTED']:
						return response_error(MESSAGE.OUTCOME_DISPUTE_INVALID)

					outcome.result = CONST.RESULT_TYPE['PROCESSING']

				else:
					return response_error(MESSAGE.OUTCOME_INVALID)

				report = {}
				report['offchain'] = CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + 'report' + str(item['side'])
				report['hid'] = outcome.hid
				report['outcome_result'] = item['side']

				task = Task(
					task_type=CONST.TASK_TYPE['REAL_BET'],
					data=json.dumps(report),
					action=CONST.TASK_ACTION['REPORT' if dispute != 1 else 'RESOLVE'],
					status=-1
				)

				db.session.add(task)
				db.session.flush()

			db.session.commit()
			return response_ok()
		else:
			return response_error(MESSAGE.MATCH_NOT_FOUND)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
