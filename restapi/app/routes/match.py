import os
import json
import requests
import app.constants as CONST
import app.bl.match as match_bl
import app.bl.contract as contract_bl

from sqlalchemy import and_, or_, desc
from flask_jwt_extended import jwt_required, decode_token
from flask import g, Blueprint, request, current_app as app
from datetime import datetime
from app.helpers.response import response_ok, response_error
from app.helpers.decorators import login_required, admin_required
from app.helpers.utils import local_to_utc
from app.bl.match import is_validate_match_time
from app import db
from app.models import User, Match, Outcome, Task, Source, Category, Contract
from app.helpers.message import MESSAGE, CODE

match_routes = Blueprint('match', __name__)

@match_routes.route('/', methods=['GET'])
@login_required
def matches():
	try:
		response = []
		matches = []

		t = datetime.now().timetuple()
		seconds = local_to_utc(t)
		
		matches = db.session.query(Match).filter(Match.deleted == 0, Match.date > seconds, Match.id.in_(db.session.query(Outcome.match_id).filter(and_(Outcome.result == -1, Outcome.hid != None)).group_by(Outcome.match_id))).order_by(Match.index.desc(), Match.date.asc()).all()

		for match in matches:	
			match_json = match.to_json()

			total_users_query = '( SELECT count(user_id) AS total FROM (SELECT user_id FROM outcome JOIN handshake ON outcome.id = handshake.outcome_id WHERE outcome.match_id = {} GROUP BY user_id) AS tmp) AS total_users_m, (SELECT count(shaker_id) AS total FROM (SELECT shaker.shaker_id FROM outcome JOIN handshake ON outcome.id = handshake.outcome_id JOIN shaker ON handshake.id = shaker.handshake_id WHERE outcome.match_id = {} GROUP BY shaker_id) AS tmp) AS total_users_s'.format(match.id, match.id)
			total_bets_query = '( SELECT SUM(total_amount) AS total FROM (SELECT handshake.amount * handshake.odds as total_amount FROM outcome JOIN handshake ON outcome.id = handshake.outcome_id WHERE outcome.match_id = {}) AS tmp) AS total_amount_m, (SELECT SUM(total_amount) AS total FROM (SELECT shaker.amount * shaker.odds as total_amount FROM outcome JOIN handshake ON outcome.id = handshake.outcome_id JOIN shaker ON handshake.id = shaker.handshake_id WHERE outcome.match_id = {}) AS tmp) AS total_amount_s'.format(match.id, match.id)

			total = db.engine.execute('SELECT {}, {}'.format( total_users_query, total_bets_query)).first()

			match_json["total_bets"] = (total['total_amount_s'] if total['total_amount_s'] is not None else 0)  + (total['total_amount_m'] if total['total_amount_m'] is not None else 0)
			match_json["total_users"] = (total['total_users_s'] if total['total_users_s'] is not None else 0) + (total['total_users_m'] if total['total_users_m'] is not None else 0)

			match_json["contract_address"] = g.PREDICTION_SMART_CONTRACT
			match_json["contract_json"] = g.PREDICTION_JSON

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

		contract = contract_bl.get_active_smart_contract()
		if contract is None:
			return response_error(MESSAGE.CONTRACT_EMPTY_VERSION, CODE.CONTRACT_EMPTY_VERSION)

		for item in data:
			source = None
			category = None

			if match_bl.is_validate_match_time(item) == False:				
				return response_error(MESSAGE.MATCH_INVALID_TIME, CODE.MATCH_INVALID_TIME)

			if "source_id" in item:
    			# TODO: check deleted and approved
				source = db.session.query(Source).filter(Source.id == int(item['source_id'])).first()
			else:
				if "source" in item and "name" in item["source"] and "url" in item["source"]:
					source = Source(
						name=item["source"]["name"],
						url=item["source"]["url"],
						created_user_id=uid
					)
					db.session.add(source)
					db.session.flush()

			if "category_id" in item:
				category = db.session.query(Category).filter(Category.id == int(item['category_id'])).first()
			else:
				if "category" in item and "name" in item["category"]:
					category = Category(
						name=item["category"]["name"],
						created_user_id=uid
					)
					db.session.add(category)
					db.session.flush()

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
				disputeTime=item['disputeTime'],
				created_user_id=uid,
				source_id=None if source is None else source.id,
				category_id=None if category is None else category.id
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
						contract_id=contract.id,
						modified_user_id=uid,
						created_user_id=uid
					)
					db.session.add(outcome)
					db.session.flush()
			match_json = match.to_json()
			match_json['contract'] = contract.to_json()
			match_json['source_name'] = None if source is None else source.name
			match_json['category_name'] = None if category is None else category.name
			response_json.append(match_json)

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
def report(match_id):
	"""
	"" report: report match
	"""
	try:
		data = request.json
		response = []
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
						return  response_error(MESSAGE.OUTCOME_IS_REPORTING)

					outcome.result = CONST.RESULT_TYPE['PROCESSING']
					outcome_json = outcome.to_json()

					outcome_json["contract_address"] = g.PREDICTION_SMART_CONTRACT
					outcome_json["contract_json"] = g.PREDICTION_JSON
					response.append(outcome_json)
				else:
					return response_error(MESSAGE.OUTCOME_INVALID)

			db.session.commit()
			return response_ok(response)
		else:
			return response_error(MESSAGE.MATCH_NOT_FOUND)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@match_routes.route('/report', methods=['GET'])
@login_required
def match_need_user_report():
	try:
		uid = int(request.headers['Uid'])

		if request.headers['Uid'] is None:
			return response_error(MESSAGE.USER_INVALID, CODE.USER_INVALID)

		t = datetime.now().timetuple()
		seconds = local_to_utc(t)

		response = []
		contracts = contract_bl.all_contracts()

		# Get all matchs are PENDING (-1)
		matches = db.session.query(Match).filter(and_(Match.date < seconds, Match.reportTime >= seconds, Match.id.in_(db.session.query(Outcome.match_id).filter(and_(Outcome.result == CONST.RESULT_TYPE['PENDING'], Outcome.hid != None, Outcome.created_user_id == uid)).group_by(Outcome.match_id)))).all()

		# Filter all outcome of user
		for match in matches:
			match_json = match.to_json()
			arr_outcomes = []
			for outcome in match.outcomes:
				if outcome.created_user_id == uid and outcome.hid >= 0:
					outcome_json = contract_bl.filter_contract_id_in_contracts(outcome.to_json(), contracts)
					arr_outcomes.append(outcome_json)
			
			match_json["outcomes"] = arr_outcomes
			response.append(match_json)

		return response_ok(response)
	except Exception, ex:
		return response_error(ex.message)
