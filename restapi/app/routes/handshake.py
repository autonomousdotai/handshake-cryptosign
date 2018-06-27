# -*- coding: utf-8 -*-
from __future__ import division
import base64
import time
import os
import sys
import simplejson as json
import logging

import app.constants as CONST
import app.bl.handshake as handshake_bl
import app.bl.match as match_bl
import app.bl.user as user_bl

from decimal import *
from flask import Blueprint, request, g
from sqlalchemy import or_, and_, text, func

from app.helpers.response import response_ok, response_error
from app.helpers.message import MESSAGE, CODE
from app.helpers.bc_exception import BcException
from app.helpers.decorators import login_required
from app.helpers.utils import is_equal
from app import db
from app.models import User, Handshake, Shaker, Outcome, Match, Task
from app.constants import Handshake as HandshakeStatus
from app.tasks import update_feed

handshake_routes = Blueprint('handshake', __name__)
getcontext().prec = 18
logfile = logging.getLogger('file')

@handshake_routes.route('/', methods=['POST'])
@login_required
def handshakes():
	uid = int(request.headers['Uid'])
	try:
		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		outcome_id = data.get('outcome_id', -1)
		outcome = Outcome.find_outcome_by_id(outcome_id)
		if outcome is None:
			return response_error(MESSAGE.INVALID_BET, CODE.INVALID_BET)
		
		match = Match.find_match_by_id(outcome.match_id)
		supports = handshake_bl.find_available_support_handshakes(outcome_id)
		against = handshake_bl.find_available_against_handshakes(outcome_id)

		total = Decimal('0', 2)

		traded_volumns = db.session.query(func.sum(Handshake.amount*Handshake.odds).label('traded_volumn')).filter(and_(Handshake.outcome_id==outcome_id, Handshake.status==CONST.Handshake['STATUS_INITED'])).group_by(Handshake.odds).all()
		for traded in traded_volumns:
			total += traded[0]

		arr_supports = []
		for support in supports:
			data = {}
			data['odds'] = support[0]
			data['amount'] = support[1]
			arr_supports.append(data)

		arr_against = []
		for against in against:
			data = {}
			data['odds'] = against[0]
			data['amount'] = against[1]
			arr_against.append(data)

		response = {
			"support": arr_supports,
			"against": arr_against,
			"traded_volumn": total,
			"market_fee": match.market_fee
		}

		return response_ok(response)

	except Exception, ex:
		return response_error(ex.message)
	
	return response_ok()

@handshake_routes.route('/<int:id>')
@login_required
def detail(id):
	uid = int(request.headers['Uid'])
	chain_id = int(request.headers.get('ChainId', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
	user = User.find_user_with_id(uid)		

	try:
		handshake = db.session.query(Handshake).filter(and_(Handshake.id==id, Handshake.user_id==uid)).first()
		if handshake is not None:
			return response_ok(handshake.to_json())

		return response_error(MESSAGE.HANDSHAKE_NOT_FOUND, CODE.HANDSHAKE_NOT_FOUND)

	except Exception, ex:
		return response_error(ex.message)


@handshake_routes.route('/init', methods=['POST'])
@login_required
def init():
	try:
		uid = int(request.headers['Uid'])
		chain_id = int(request.headers.get('ChainId', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
		user = User.find_user_with_id(uid)		

		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		hs_type = data.get('type', -1)
		extra_data = data.get('extra_data', '')
		description = data.get('description', '')
		is_private = data.get('is_private', 1)
		outcome_id = data.get('outcome_id')
		odds = Decimal(data.get('odds'))
		amount = Decimal(data.get('amount'))
		currency = data.get('currency', 'ETH')
		side = int(data.get('side', CONST.SIDE_TYPE['SUPPORT']))
		chain_id = int(data.get('chain_id', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
		from_address = data.get('from_address', '')

		if hs_type != CONST.Handshake['INDUSTRIES_BETTING']:
			return response_error(MESSAGE.HANDSHAKE_INVALID_BETTING_TYPE, CODE.HANDSHAKE_INVALID_BETTING_TYPE)

		if len(from_address) == 0:
			return response_error(MESSAGE.INVALID_ADDRESS, CODE.INVALID_ADDRESS)

		outcome = Outcome.find_outcome_by_id(outcome_id)
		if outcome is None:
			return response_error(MESSAGE.OUTCOME_INVALID, CODE.OUTCOME_INVALID)

		if outcome.result != CONST.RESULT_TYPE['PENDING']:
			return response_error(MESSAGE.OUTCOME_HAS_RESULT, CODE.OUTCOME_HAS_RESULT)

		if odds <= 1:
			return response_error(MESSAGE.INVALID_ODDS, CODE.INVALID_ODDS)

		# filter all handshakes which able be to match first
		handshakes = handshake_bl.find_all_matched_handshakes(side, odds, outcome_id, amount)
		if len(handshakes) == 0:
			handshake = Handshake(
				hs_type=hs_type,
				extra_data=extra_data,
				description=description,
				chain_id=chain_id,
				is_private=is_private,
				user_id=user.id,
				outcome_id=outcome_id,
				odds=odds,
				amount=amount,
				currency=currency,
				side=side,
				remaining_amount=amount,
				from_address=from_address
			)
			db.session.add(handshake)
			db.session.commit()

			update_feed.delay(handshake.id)

			# response data
			arr_hs = []
			hs_json = handshake.to_json()
			hs_json['hid'] = outcome.hid
			hs_json['type'] = 'init'
			hs_json['offchain'] = CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + 'm' + str(handshake.id)
			arr_hs.append(hs_json)

			logfile.debug("Uid -> {}, json --> {}".format(uid, arr_hs))
			return response_ok(arr_hs)
		else:
			arr_hs = []
			shaker_amount = amount

			hs_feed = []
			sk_feed = []
			for handshake in handshakes:
				if shaker_amount.quantize(Decimal('.00000000000000001'), rounding=ROUND_DOWN) <= 0:
					break

				handshake.shake_count += 1
				handshake_win_value = handshake.remaining_amount*handshake.odds
				shaker_win_value = shaker_amount*odds
				subtracted_amount_for_shaker = 0
				subtracted_amount_for_handshake = 0


				if is_equal(handshake_win_value, shaker_win_value):
					subtracted_amount_for_shaker = shaker_amount
					subtracted_amount_for_handshake = handshake.remaining_amount

				elif handshake_win_value >= shaker_win_value:
					subtracted_amount_for_shaker = shaker_amount
					subtracted_amount_for_handshake = shaker_win_value - subtracted_amount_for_shaker

				else:
					subtracted_amount_for_handshake = handshake.remaining_amount
					subtracted_amount_for_shaker = handshake_win_value - subtracted_amount_for_handshake

				handshake.remaining_amount -= subtracted_amount_for_handshake
				shaker_amount -= subtracted_amount_for_shaker
				db.session.merge(handshake)

				# create shaker
				shaker = Shaker(
					shaker_id=user.id,
					amount=subtracted_amount_for_shaker,
					currency=currency,
					odds=odds,
					side=side,
					handshake_id=handshake.id,
					from_address=from_address,
					chain_id=chain_id
				)

				db.session.add(shaker)
				db.session.flush()
				sk_feed.append(shaker)
				
				shaker_json = shaker.to_json()
				shaker_json['maker_address'] = handshake.from_address
				shaker_json['maker_odds'] = handshake.odds
				hs_json['hid'] = outcome.hid
				shaker_json['type'] = 'shake'
				shaker_json['offchain'] = CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + 's' + str(shaker.id)
				arr_hs.append(shaker_json)

			if shaker_amount.quantize(Decimal('.00000000000000001'), rounding=ROUND_DOWN) > CONST.CRYPTOSIGN_MINIMUM_MONEY:
				handshake = Handshake(
					hs_type=hs_type,
					extra_data=extra_data,
					description=description,
					chain_id=chain_id,
					is_private=is_private,
					user_id=user.id,
					outcome_id=outcome_id,
					odds=odds,
					amount=shaker_amount,
					currency=currency,
					side=side,
					remaining_amount=shaker_amount,
					from_address=from_address
				)
				db.session.add(handshake)
				db.session.flush()
				hs_feed.append(handshake)			

				hs_json = handshake.to_json()
				hs_json['hid'] = outcome.hid
				hs_json['type'] = 'init'
				hs_json['offchain'] = CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + 'm' + str(handshake.id)
				arr_hs.append(hs_json)
			
			db.session.commit()
			logfile.debug("Uid -> {}, json --> {}".format(uid, arr_hs))

			handshake_bl.update_handshakes_feed(hs_feed, sk_feed)
			return response_ok(arr_hs)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@handshake_routes.route('/rollback', methods=['POST'])
@login_required
def rollback():
	# rollback init (real, free): DONE
	# rollback shake (real, free): DONE
	try:
		uid = int(request.headers['Uid'])
		chain_id = int(request.headers.get('ChainId', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
		user = User.find_user_with_id(uid)

		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		offchain = data.get('offchain')
		if offchain is None or len(offchain) == 0:
			return response_error(MESSAGE.MISSING_OFFCHAIN, CODE.MISSING_OFFCHAIN)

		offchain = offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')
		
		handshakes = []
		shakers = []
		response = None

		if 'm' in offchain:
			offchain = int(offchain.replace('m', ''))
			handshake = db.session.query(Handshake).filter(and_(Handshake.id==offchain, Handshake.user_id==uid)).first()
			if handshake is not None:	
				if handshake_bl.is_init_pending_status(handshake): # rollback maker init state
					handshake.status = HandshakeStatus['STATUS_MAKER_UNINIT_FAILED']
					if handshake.free_bet == 1:
						user.free_bet = 0
					
					db.session.flush()
					handshakes.append(handshake)

				else:
					return response_error(MESSAGE.CANNOT_ROLLBACK, CODE.CANNOT_ROLLBACK)

				response = handshake.to_json()

			else:
				return response_error(MESSAGE.HANDSHAKE_EMPTY, CODE.HANDSHAKE_EMPTY)

		else:
			offchain = int(offchain.replace('s', ''))
			shaker = db.session.query(Shaker).filter(and_(Shaker.id==offchain, Shaker.shaker_id==uid)).first()

			if shaker is not None:
				if shaker.status == HandshakeStatus['STATUS_PENDING']:
					shaker = handshake_bl.rollback_shake_state(shaker)
					if shaker.free_bet == 1:
						user.free_bet = 0

					shakers.append(shaker)

				else:
					return response_error(MESSAGE.CANNOT_ROLLBACK, CODE.CANNOT_ROLLBACK)

				response = shaker.to_json()

			else:
				return response_error(MESSAGE.SHAKER_NOT_FOUND, CODE.SHAKER_NOT_FOUND)

		db.session.commit()
		handshake_bl.update_handshakes_feed(handshakes, shakers)

		return response_ok(response)
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@handshake_routes.route('/create_free_bet', methods=['POST'])
@login_required
def create_bet():
	try:
		uid = int(request.headers['Uid'])
		chain_id = int(request.headers.get('ChainId', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
		user = User.find_user_with_id(uid)

		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		odds = Decimal(data.get('odds'))
		amount = Decimal('0.001')
		side = int(data.get('side', CONST.SIDE_TYPE['SUPPORT']))

		if user.free_bet > 0:
			return response_error(MESSAGE.USER_RECEIVED_FREE_BET_ALREADY, CODE.USER_RECEIVED_FREE_BET_ALREADY)

		outcome_id = data.get('outcome_id')
		outcome = Outcome.find_outcome_by_id(outcome_id)
		if outcome is None:
			return response_error(MESSAGE.OUTCOME_INVALID, CODE.OUTCOME_INVALID)

		elif outcome.result != -1:
			return response_error(MESSAGE.OUTCOME_HAS_RESULT, CODE.OUTCOME_HAS_RESULT)

		match = Match.find_match_by_id(outcome.match_id)
		data['hid'] = outcome.hid
		data['outcome_name'] = outcome.name
		data['match_date'] = match.date
		data['match_name'] = match.name

		if user_bl.check_user_is_able_to_create_new_free_bet():
			user.free_bet = 1
			task = Task(
				task_type=CONST.TASK_TYPE['FREE_BET'],
				data=json.dumps(data),
				action=CONST.TASK_ACTION['INIT'],
				status=-1
			)
			db.session.add(task)
			db.session.commit()

			# this is for frontend
			handshakes = handshake_bl.find_all_matched_handshakes(side, odds, outcome_id, amount)
			response = {}
			if len(handshakes) == 0:
				response['match'] = 0
			else:
				response['match'] = 1
			return response_ok(response)

		else:
			return response_error(MESSAGE.MAXIMUM_FREE_BET, CODE.MAXIMUM_FREE_BET)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)

@handshake_routes.route('/uninit_free_bet/<int:handshake_id>', methods=['POST'])
@login_required
def uninit_free_bet(handshake_id):
	try:
		uid = int(request.headers['Uid'])
		chain_id = int(request.headers.get('ChainId', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
		user = User.find_user_with_id(uid)

		handshake = db.session.query(Handshake).filter(and_(Handshake.id==handshake_id, Handshake.chain_id==chain_id, Handshake.user_id==uid, Handshake.status==CONST.Handshake['STATUS_INITED'], Handshake.free_bet==1)).first()
		if handshake is not None:
			if handshake_bl.can_uninit(handshake) == False:
				return response_error(MESSAGE.HANDSHAKE_CANNOT_UNINIT, CODE.HANDSHAKE_CANNOT_UNINIT)
			else:
				outcome = Outcome.find_outcome_by_id(handshake.outcome_id)
				if outcome is None:
					return response_error(MESSAGE.OUTCOME_INVALID, CODE.OUTCOME_INVALID)
				else:
					handshake.status = CONST.Handshake['STATUS_MAKER_UNINIT_PENDING']
					db.session.flush()
					update_feed.delay(handshake.id)
					
					data = {
						'hid': outcome.hid,
						'side': handshake.side,
						'odds': handshake.odds,
						'maker': handshake.from_address,
						'value': handshake.amount,
						'offchain': CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + 'm{}'.format(handshake.id)
					}
					task = Task(
						task_type=CONST.TASK_TYPE['FREE_BET'],
						data=json.dumps(data, use_decimal=True),
						action=CONST.TASK_ACTION['UNINIT'],
						status=-1
					)
					db.session.add(task)
					db.session.commit()

					return response_ok(handshake.to_json())
					
		else:
			return response_error(MESSAGE.HANDSHAKE_NOT_FOUND, CODE.HANDSHAKE_NOT_FOUND)	


	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@handshake_routes.route('/collect_free_bet', methods=['POST'])
@login_required
def collect_free_bet():
	try:
		uid = int(request.headers['Uid'])
		chain_id = int(request.headers.get('ChainId', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
		user = User.find_user_with_id(uid)

		data = request.json
		if data is None:
			return response_error(MESSAGE.INVALID_DATA, CODE.INVALID_DATA)

		offchain = data.get('offchain', '')
		if len(offchain) == 0:
			return response_error(MESSAGE.MISSING_OFFCHAIN, CODE.MISSING_OFFCHAIN)

		h = []
		s = []
		offchain = offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')
		if 's' in offchain:
			offchain = int(offchain.replace('s', ''))
			shaker = db.session.query(Shaker).filter(and_(Shaker.id==offchain, Shaker.shaker_id==user.id)).first()
			msg = handshake_bl.can_withdraw(handshake=None, shaker=shaker)
			if len(msg) != 0:
				return response_error(msg, CODE.CANNOT_WITHDRAW)
			
			hs = Handshake.find_handshake_by_id(shaker.handshake_id)
			outcome = Outcome.find_outcome_by_id(hs.outcome_id)
			h = db.session.query(Handshake).filter(and_(Handshake.user_id==user.id, Handshake.outcome_id==hs.outcome_id, Handshake.side==shaker.side, Handshake.status==HandshakeStatus['STATUS_INITED'])).all()
			s = db.session.query(Shaker).filter(and_(Shaker.shaker_id==user.id, Shaker.side==shaker.side, Shaker.status==HandshakeStatus['STATUS_SHAKER_SHAKED'], Shaker.handshake_id.in_(db.session.query(Handshake.id).filter(Handshake.outcome_id==hs.outcome_id)))).all()

			data['hid'] = outcome.hid
			data['winner'] = shaker.from_address

		else:
			offchain = int(offchain.replace('m', ''))
			handshake = db.session.query(Handshake).filter(and_(Handshake.id==offchain, Handshake.user_id==user.id)).first()
			msg = handshake_bl.can_withdraw(handshake)
			if len(msg) != 0:
				return response_error(msg, CODE.CANNOT_WITHDRAW)

			outcome = Outcome.find_outcome_by_id(handshake.outcome_id)
			h = db.session.query(Handshake).filter(and_(Handshake.user_id==user.id, Handshake.outcome_id==handshake.outcome_id, Handshake.side==handshake.side, Handshake.status==HandshakeStatus['STATUS_INITED'])).all()
			s = db.session.query(Shaker).filter(and_(Shaker.shaker_id==user.id, Shaker.side==handshake.side, Shaker.status==HandshakeStatus['STATUS_SHAKER_SHAKED'], Shaker.handshake_id.in_(db.session.query(Handshake.id).filter(Handshake.outcome_id==handshake.outcome_id)))).all()

			data['hid'] = outcome.hid
			data['winner'] = handshake.from_address


		handshakes = []
		shakers = []
		response = {}
		# update status
		for hs in h:
			hs.status = HandshakeStatus['STATUS_COLLECT_PENDING']
			db.session.flush()
			handshakes.append(hs)

			if hs.id == offchain:
				response = hs.to_json()
			
		for sk in s:
			sk.status = HandshakeStatus['STATUS_COLLECT_PENDING']
			db.session.flush()
			shakers.append(sk)

			if sk.id == offchain:
				response = sk.to_json()

		# add task
		task = Task(
			task_type=CONST.TASK_TYPE['FREE_BET'],
			data=json.dumps(data),
			action=CONST.TASK_ACTION['COLLECT'],
			status=-1
		)
		db.session.add(task)
		db.session.commit()

		handshake_bl.update_handshakes_feed(handshakes, shakers)
		return response_ok(response)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)

@handshake_routes.route('/check_free_bet', methods=['GET'])
@login_required
def has_received_free_bet():
	try:
		uid = int(request.headers['Uid'])
		chain_id = int(request.headers.get('ChainId', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
		user = User.find_user_with_id(uid)

		if user.free_bet > 0:
			return response_error(MESSAGE.USER_RECEIVED_FREE_BET_ALREADY, CODE.USER_RECEIVED_FREE_BET_ALREADY)

		elif user_bl.check_user_is_able_to_create_new_free_bet() is False:
			return response_error(MESSAGE.MAXIMUM_FREE_BET, CODE.MAXIMUM_FREE_BET)

		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)