import os
import json
import requests
import app.constants as CONST
import app.bl.match as match_bl
import app.bl.contract as contract_bl

from sqlalchemy import and_, or_, desc, func
from flask_jwt_extended import jwt_required, decode_token
from flask import g, Blueprint, request, current_app as app
from datetime import datetime
from app.helpers.response import response_ok, response_error
from app.helpers.decorators import login_required, admin_required
from app.helpers.utils import local_to_utc
from app.bl.match import is_validate_match_time, get_total_user_and_amount_by_match_id
from app import db
from app.models import User, Match, Outcome, Task, Source, Category, Contract, Handshake, Shaker, Source, Token
from app.helpers.message import MESSAGE, CODE

match_routes = Blueprint('match', __name__)

@match_routes.route('/', methods=['GET'])
@login_required
def matches():
	try:
		source = request.args.get('source')
		response = []
		matches = []

		t = datetime.now().timetuple()
		seconds = local_to_utc(t)
		
		matches = db.session.query(Match)\
				.filter(\
					Match.deleted == 0,\
					Match.date > seconds,\
					Match.public == 1,\
					Match.id.in_(db.session.query(Outcome.match_id).filter(and_(Outcome.result == -1, Outcome.hid != None)).group_by(Outcome.match_id)))\
				.order_by(Match.index.desc(), Match.date.asc())\
				.all()
		if source is not None:
			s = Source.find_source_by_url(source)
			if s is not None:
				matches = sorted(matches, key=lambda m: m.source_id != s.id)

		for match in matches:
			match_json = match.to_json()
			total_user, total_bets = get_total_user_and_amount_by_match_id(match.id)
			match_json["total_users"] = total_user
			match_json["total_bets"] = total_bets
			
			arr_outcomes = []
			for outcome in match.outcomes:
				if outcome.hid is not None:
    					arr_outcomes.append(outcome.to_json())

			match_json["outcomes"] = arr_outcomes
			if len(arr_outcomes) > 0:
				response.append(match_json)

		return response_ok(response)
	except Exception, ex:
		return response_error(ex.message)


@match_routes.route('/add', methods=['POST'])
@login_required
def add_match():
	try:
		uid = int(request.headers['Uid'])
		token_id = request.args.get('token_id')

		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		if token_id is None:
			contract = contract_bl.get_active_smart_contract()
			if contract is None:
				return response_error(MESSAGE.CONTRACT_EMPTY_VERSION, CODE.CONTRACT_EMPTY_VERSION)

		else:
			token = Token.find_token_by_id(token_id)
			if token is None:
				return response_error(MESSAGE.TOKEN_NOT_FOUND, CODE.TOKEN_NOT_FOUND)
			
			token_id = token.id
			# refresh erc20 contract
			contract = contract_bl.get_active_smart_contract(contract_type=CONST.CONTRACT_TYPE['ERC20'])
			if contract is None:
				return response_error(MESSAGE.CONTRACT_EMPTY_VERSION, CODE.CONTRACT_EMPTY_VERSION)

		matches = []
		response_json = []
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
					source = db.session.query(Source).filter(and_(Source.name==item["source"]["name"], Source.url==item["source"]["url"])).first()
					if source is not None:
						return response_error(MESSAGE.SOURCE_EXISTED_ALREADY, CODE.SOURCE_EXISTED_ALREADY)

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
				public=item['public'],
				market_fee=int(item.get('market_fee', 0)),
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
						contract_id=contract.id,
						modified_user_id=uid,
						created_user_id=uid,
						token_id=token_id
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
			return response_error(MESSAGE.MATCH_NOT_FOUND, CODE.MATCH_NOT_FOUND)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@match_routes.route('/report/<int:match_id>', methods=['POST'])
@login_required
def report_match(match_id):
	"""
	"" report: report outcomes
	"" input:
	""		match_id
	"""
	try:
		uid = int(request.headers['Uid'])
		data = request.json
		response = []
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		match = Match.find_match_by_id(match_id)
		if match is not None:
			result = data['result']
			if result is None:
				return response_error(MESSAGE.MATCH_RESULT_EMPTY, CODE.MATCH_RESULT_EMPTY)
			
			if not match_bl.is_exceed_closing_time(match.id):
				return response_error(MESSAGE.MATCH_CANNOT_SET_RESULT, CODE.MATCH_CANNOT_SET_RESULT)

			for item in result:
				if 'side' not in item:
					return response_error(MESSAGE.OUTCOME_INVALID_RESULT, CODE.OUTCOME_INVALID_RESULT)
				
				if 'outcome_id' not in item:
					return response_error(MESSAGE.OUTCOME_INVALID, CODE.OUTCOME_INVALID)

				outcome = Outcome.find_outcome_by_id(item['outcome_id'])
				if outcome is not None and outcome.created_user_id == uid:
					message, code = match_bl.is_able_to_set_result_for_outcome(outcome)
					if message is not None and code is not None:
						return message, code

					outcome.result = CONST.RESULT_TYPE['PROCESSING']
					outcome_json = outcome.to_json()
					response.append(outcome_json)

				else:
					return response_error(MESSAGE.OUTCOME_INVALID, CODE.OUTCOME_INVALID)

			return response_ok(response)
		else:
			return response_error(MESSAGE.MATCH_NOT_FOUND, CODE.MATCH_NOT_FOUND)

	except Exception, ex:
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

@match_routes.route('/relevant-event', methods=['GET'])
@login_required
def relevant():
	try:
		match_id = int(request.args.get('match')) if request.args.get('match') is not None else None
		match = Match.find_match_by_id(match_id)

		response = []
		matches = []
		t = datetime.now().timetuple()
		seconds = local_to_utc(t)
		if match is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		matches = db.session.query(Match)\
		.filter(\
			or_(Match.source_id == match.source_id, Match.category_id == match.category_id),\
			Match.deleted == 0,\
			Match.date > seconds,\
			Match.public == 1,\
			Match.id.in_(db.session.query(Outcome.match_id).filter(and_(Outcome.result == -1, Outcome.hid != None)).group_by(Outcome.match_id)))\
		.order_by(Match.source_id, Match.category_id, Match.index.desc(), Match.date.asc())\
		.all()

		for match in matches:
			match_json = match.to_json()
			total_user, total_bets = get_total_user_and_amount_by_match_id(match.id)
			match_json["total_users"] = total_user
			match_json["total_bets"] = total_bets
			
			arr_outcomes = []
			for outcome in match.outcomes:
				if outcome.hid is not None:
					arr_outcomes.append(outcome.to_json())

			match_json["outcomes"] = arr_outcomes
			
			response.append(match_json)

		return response_ok(response)
	except Exception, ex:
		return response_error(ex.message)


@match_routes.route('/<int:match_id>', methods=['GET'])
def match_detail(match_id):
	try:
		outcome_id = None
		if request.args.get('outcome_id') is not None:
			outcome_id = int(request.args.get('outcome_id'))

		t = datetime.now().timetuple()
		seconds = local_to_utc(t)

		match = db.session.query(Match)\
				.filter(\
					Match.id == match_id,\
					Match.deleted == 0,\
					Match.date > seconds,\
					Match.id.in_(db.session.query(Outcome.match_id).filter(and_(Outcome.result == -1)).group_by(Outcome.match_id)))\
				.first()

		if match is None:
			return response_error(MESSAGE.MATCH_NOT_FOUND, CODE.MATCH_NOT_FOUND)
		
		match_json = match.to_json()
		total_user, total_bets = get_total_user_and_amount_by_match_id(match.id)
		match_json["total_users"] = total_user
		match_json["total_bets"] = total_bets

		arr_outcomes = []
		for outcome in match.outcomes:
			if outcome_id is not None:
				if outcome.id == outcome_id:
					arr_outcomes.append(outcome.to_json())
			else:
				arr_outcomes.append(outcome.to_json())

		match_json["outcomes"] = arr_outcomes
		return response_ok(match_json)

	except Exception, ex:
		return response_error(ex.message)
