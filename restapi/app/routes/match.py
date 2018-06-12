import os
import json
import app.constants as CONST
import app.bl.match as match_bl

from flask import Blueprint, request, current_app as app
from app.helpers.response import response_ok, response_error
from app.helpers.decorators import login_required, admin_required
from app.helpers.utils import parse_date_string_to_timestamp
from app import db
from app.models import User, Match, Outcome
from app.helpers.message import MESSAGE

match_routes = Blueprint('match', __name__)

@match_routes.route('/', methods=['GET'])
@login_required
def matches():
	try:
		matches = Match.query.all()
		data = []

		for match in matches:
			#  find best odds which match against
			match_json = match.to_json()

			arr_outcomes = []
			for outcome in match.outcomes:
				outcome_json = outcome.to_json()
				odds, amount = match_bl.find_best_odds_which_match_support_side(outcome.id)
				outcome_json["market_odds"] = odds
				outcome_json["market_amount"] = amount
				arr_outcomes.append(outcome_json)
				
			match_json["outcomes"] = arr_outcomes
			data.append(match_json)

		return response_ok(data)
	except Exception, ex:
		return response_error(ex.message)


@match_routes.route('/add', methods=['POST'])
@login_required
def add():
	try:
		data = request.json
		if data is None:
			raise Exception(MESSAGE.INVALID_DATA)

		matches = []
		outcomes = []
		response_json = []
		for item in data:
			match = Match(
				homeTeamName=item['homeTeamName'],
				homeTeamCode=item['homeTeamCode'],
				homeTeamFlag=item['homeTeamFlag'],
				awayTeamName=item['awayTeamName'],
				awayTeamCode=item['awayTeamCode'],
				awayTeamFlag=item['awayTeamFlag'],
				name=item['name'],
				source=item['source'],
				market_fee=int(item['market_fee']),
				date=parse_date_string_to_timestamp(item['date'])
			)
			matches.append(match)
			db.session.add(match)
			db.session.flush()

			if 'outcomes' in item:
				for outcome_data in item['outcomes']:
					outcome = Outcome(
						name=outcome_data['name'],
						match_id=match.id
					)
					outcomes.append(outcome)
			response_json.append(match.to_json())

		db.session.add_all(outcomes)
		db.session.commit()

		return response_ok(response_json)
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@match_routes.route('/create_market', methods=['POST'])
@admin_required
def create_market():
	try:
		fixtures_path = os.path.abspath(os.path.dirname(__file__)) + '/fixtures.json'
		data = {}
		with open(fixtures_path, 'r') as f:
			data = json.load(f)

		matches = []
		outcomes = []
		if 'fixtures' in data:
			fixtures = data['fixtures']
			for item in fixtures:
				if len(item['homeTeamName']) > 0 and len(item['awayTeamName']) > 0:
					match = Match(
								homeTeamName=item['homeTeamName'],
								awayTeamName=item['awayTeamName'],
								name='{} vs {}'.format(item['homeTeamName'], item['awayTeamName']),
								source='football-data.org',
								market_fee=0,
								date=parse_date_string_to_timestamp(item['date'])
							)
					matches.append(match)
					db.session.add(match)
					db.session.flush()
					
					outcome = Outcome(
						name='{} wins'.format(item['homeTeamName']),
						match_id=match.id
					)
					outcomes.append(outcome)

		db.session.add_all(outcomes)
		db.session.commit()
		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@match_routes.route('/remove/<int:id>', methods=['POST'])
@login_required
# @admin_required
def remove(id):
	try:
		match = Match.find_match_by_id(id)
		if match is not None:
			db.session.delete(match)
			db.session.commit()
			return response_ok("{} has been deleted!".format(match.id))
		else:
			return response_error(MESSAGE.MATCH_NOT_FOUND)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@match_routes.route('/report/<int:match_id>', methods=['POST'])
@login_required
# @admin_required
def report(match_id):
	try:
		data = request.json
		if data is None:
			raise Exception(MESSAGE.INVALID_DATA)

		match = Match.find_match_by_id(match_id)
		if match is not None:
			homeScore = data['homeScore'] if 'homeScore' in data else ''
			awayScore = data['awayScore'] if 'awayScore' in data else ''
			result = data['result']

			match.homeScore = homeScore
			match.awayScore = awayScore
			for o in result:
				outcome = Outcome.find_outcome_by_id(o['outcome_id'])
				if outcome is not None:
					outcome.result = o['side']
				else:
					return response_error(MESSAGE.INVALID_OUTCOME)

			return response_ok()
		else:
			return response_error(MESSAGE.MATCH_NOT_FOUND)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)

