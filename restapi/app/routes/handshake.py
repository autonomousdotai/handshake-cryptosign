# -*- coding: utf-8 -*-
from __future__ import division
import base64
import time
import os
import requests
import hashlib
import sys
import json

import app.constants as CONST
import app.bl.handshake as handshake_bl

from decimal import Decimal
from flask import Blueprint, request, g
from sqlalchemy import or_, and_, text
from app.helpers.response import response_ok, response_error
from app.helpers.message import MESSAGE
from app.helpers.bc_exception import BcException
from app.helpers.decorators import login_required
from app import db, s3, ipfs
from app.models import User, Handshake, Shaker, Outcome, Match
from app.constants import Handshake as HandshakeStatus
from datetime import datetime
from app.tasks import update_feed

handshake_routes = Blueprint('handshake', __name__)


@handshake_routes.route('/', methods=['POST'])
@login_required
def handshakes():
	uid = int(request.headers['Uid'])
	try:
		data = request.json
		if data is None:
			raise Exception(MESSAGE.INVALID_DATA)

		outcome_id = data.get('outcome_id', -1)
		outcome = Outcome.find_outcome_by_id(outcome_id)
		if outcome is None:
			raise Exception(MESSAGE.INVALID_BET)
		
		match = Match.find_match_by_id(outcome.match_id)
		supports = handshake_bl.find_available_support_handshakes(outcome_id)
		against = handshake_bl.find_available_against_handshakes(outcome_id)

		total = Decimal(0, 2)
		arr_supports = []
		for support in supports:
			data = {}
			data['odds'] = support[0]
			data['amount'] = support[1]
			total += support[0] * support[1]
			arr_supports.append(data)

		arr_against = []
		for against in against:
			data = {}
			data['odds'] = against[0]/(against[0]-1)
			data['amount'] = against[1]
			total += against[0] * against[1]
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
	chain_id = int(request.headers.get('ChainId', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))

	try:
		return response_ok()

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
			raise Exception(MESSAGE.INVALID_DATA)

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
			raise Exception(MESSAGE.HANDSHAKE_INVALID_BETTING_TYPE)

		if len(from_address) == 0:
			raise Exception(MESSAGE.INVALID_ADDRESS)

		outcome = Outcome.find_outcome_by_id(outcome_id)
		if outcome is None:
			raise Exception(MESSAGE.INVALID_BET)

		if outcome.result != CONST.RESULT_TYPE['PENDING']:
			raise Exception(MESSAGE.OUTCOME_HAS_RESULT)

		if odds <= 1:
			raise Exception(MESSAGE.INVALID_ODDS)

		# filter all handshakes which able be to match first
		handshakes = handshake_bl.find_all_matched_handshakes(side, odds, outcome_id, amount)
		print 'DEBUG {}'.format(handshakes)
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
				win_value=odds*amount,
				remaining_amount=amount,
				from_address=from_address
			)
			db.session.add(handshake)
			db.session.commit()

			update_feed.delay(handshake.id, user.id)

			# response data
			arr_hs = []
			hs_json = handshake.to_json()
			hs_json['offchain'] = CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + 'm' + str(handshake.id)
			arr_hs.append(hs_json)

			return response_ok(arr_hs)
		else:
			arr_hs = []
			shaker_amount = amount

			for handshake in handshakes:
				handshake.shake_count += 1

				handshake_win_value = handshake.remaining_amount*handshake.odds
				shaker_win_value = shaker_amount*odds
				final_win_value = min(handshake_win_value, shaker_win_value)
				subtracted_amount_for_handshake = final_win_value/handshake.odds
				subtracted_amount_for_shaker = final_win_value - subtracted_amount_for_handshake
				handshake.remaining_amount -= subtracted_amount_for_handshake
				shaker_amount -= subtracted_amount_for_shaker
				
				# create shaker
				shaker = Shaker(
					shaker_id=user.id,
					amount=subtracted_amount_for_shaker,
					currency=currency,
					odds=odds,
					win_value=odds*subtracted_amount_for_shaker,
					side=side,
					handshake_id=handshake.id
				)

				db.session.add(shaker)
				db.session.flush()

				update_feed.delay(handshake.id, user.id, shaker.id)
				
				handshake_json = handshake.to_json()
				shakers = handshake_json['shakers']
				if shakers is None:
					shakers = []

				shakers.append(shaker.to_json())

				handshake_json['shakers'] = shakers
				handshake_json['offchain'] = CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + 's' + str(shaker.id)
				arr_hs.append(handshake_json)
				

				print 'shaker amount {}'.format(shaker_amount)
				if shaker_amount <= 0:
					break

			if shaker_amount > 0:
				print 'still has money'
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
					win_value=odds*shaker_amount,
					remaining_amount=shaker_amount,
					from_address=from_address
				)
				db.session.add(handshake)
				db.session.flush()

				update_feed.delay(handshake.id, user.id)				

				hs_json = handshake.to_json()
				hs_json['offchain'] = CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + 'm' + str(handshake.id)
				arr_hs.append(hs_json)

			db.session.commit()
			return response_ok(arr_hs)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@handshake_routes.route('/shake', methods=['POST'])
@login_required
def shake():
	try:
		uid = int(request.headers['Uid'])
		chain_id = int(request.headers.get('ChainId', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
		user = User.find_user_with_id(uid)

		data = request.json
		if data is None:
			raise Exception(MESSAGE.INVALID_DATA)

		amount = Decimal(data.get('amount'))
		currency = data.get('currency', 'ETH')
		side = int(data.get('side', CONST.SIDE_TYPE['SUPPORT']))
		chain_id = int(data.get('chain_id', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
		is_private = data.get('is_private', 1)
		outcome_id = data.get('outcome_id')
		from_address = data.get('from_address', '')

		if len(from_address) == 0:
			raise Exception(MESSAGE.INVALID_ADDRESS)

		outcome = Outcome.find_outcome_by_id(outcome_id)
		if outcome is None:
			raise Exception(MESSAGE.INVALID_BET)

		if outcome.result != CONST.RESULT_TYPE['PENDING']:
			raise Exception(MESSAGE.OUTCOME_HAS_RESULT)

		handshakes = handshake_bl.find_all_joined_handshakes(side, outcome_id)
		if len(handshakes) > 0:
			arr_hs = []
			shaker_amount = amount
			for handshake in handshakes:
				handshake.shake_count += 1
				amount_for_handshake = 0

				if shaker_amount > handshake.remaining_amount:
					shaker_amount -= handshake.remaining_amount
					amount_for_handshake = handshake.remaining_amount
					handshake.remaining_amount = 0

				else:
					amount_for_handshake = shaker_amount
					handshake.remaining_amount -= shaker_amount
					shaker_amount = 0

				# create shaker
				shaker_odds = handshake.amount*handshake.odds/(handshake.amount*handshake.odds-handshake.amount)
				shaker = Shaker(
					shaker_id=user.id,
					amount=amount_for_handshake,
					currency=currency,
					odds=shaker_odds,
					win_value=shaker_odds*amount_for_handshake,
					side=side,
					handshake_id=handshake.id
				)

				db.session.add(shaker)
				db.session.flush()

				update_feed.delay(handshake.id, user.id, shaker.id)

				handshake = handshake.to_json()
				handshake['offchain'] = CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + 's' + str(shaker.id)
				arr_hs.append(handshake)
				
				print shaker_amount
				if shaker_amount <= 0:
					break

			db.session.commit()	
			message = ''
			if shaker_amount > 0:
				message = 'Your remaining money: {} after shaked!'.format(shaker_amount)
			
			return response_ok(arr_hs, message=message)
		else:
			return response_error(MESSAGE.INVALID_BET)

		return response_ok()

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)

@handshake_routes.route('/uninit/<int:handshake_id>', methods=['POST'])
@login_required
def uninit(handshake_id):
	try:
		uid = int(request.headers['Uid'])
		chain_id = int(request.headers.get('ChainId', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
		user = User.find_user_with_id(uid)
		
		handshake = db.session.query(Handshake).filter(and_(Handshake.id==handshake_id, Handshake.chain_id==chain_id, Handshake.user_id==uid, Handshake.status==CONST.Handshake['STATUS_INITED'])).first()
		if handshake is not None:
			if len(handshake.shakers.all()) > 0:
				return response_error(MESSAGE.HANDSHAKE_CANNOT_UNINIT)
			else:
				handshake.status = CONST.Handshake['STATUS_BLOCKCHAIN_PENDING']
				db.session.flush()

				update_feed.delay(handshake.id, user.id)
				outcome = Outcome.find_outcome_by_id(handshake.outcome_id)

				handshake_json = handshake.to_json()
				handshake_json['hid'] = outcome.hid
				handshake_json['offchain'] = CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + 'm' + str(handshake.id)

				db.session.commit()
				return response_ok(handshake_json)
		else:
			return response_error(MESSAGE.HANDSHAKE_NOT_FOUND)		
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)

@handshake_routes.route('/collect', methods=['POST'])
@login_required
def collect():
	try:
		uid = int(request.headers['Uid'])
		chain_id = int(request.headers.get('ChainId', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
		user = User.find_user_with_id(uid)

		data = request.json
		if data is None:
			raise Exception(MESSAGE.INVALID_DATA)

		offchain = data.get('offchain', '')
		if len(offchain) == 0:
			raise Exception(MESSAGE.MISSING_OFFCHAIN)

		offchain = offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')
		handshakes = []
		shakers = []
		if 's' in offchain:
			offchain = int(offchain.replace('s', ''))
			shaker = db.session.query(Shaker).filter(and_(Shaker.id==offchain, Shaker.shaker_id==user.id)).first()
			if shaker is not None:
				handshake = Handshake.find_handshake_by_id(shaker.handshake_id)
				outcome = Outcome.find_outcome_by_id(handshake.outcome_id)
				if outcome.result != shaker.side:
					raise Exception(MESSAGE.HANDSHAKE_NO_PERMISSION)

				# update status to STATUS_BLOCKCHAIN_PENDING
				handshakes = db.session.query(Handshake).filter(and_(Handshake.user_id==user.id, Handshake.outcome_id==outcome.id, Handshake.side==outcome.result)).all()
				shakers = db.session.query(Shaker).filter(and_(Shaker.shaker_id==user.id, Shaker.side==outcome.result, Shaker.handshake_id.in_(db.session.query(Handshake.id).filter(Handshake.outcome_id==outcome.id)))).all()

				for handshake in handshakes:
					handshake.status = HandshakeStatus['STATUS_BLOCKCHAIN_PENDING']
					handshake.bk_status = HandshakeStatus['STATUS_BLOCKCHAIN_PENDING']
					db.session.flush()

					update_feed.delay(handshake.id, handshake.user_id)

				for shaker in shakers:
					shaker.status = HandshakeStatus['STATUS_BLOCKCHAIN_PENDING']
					shaker.bk_status = HandshakeStatus['STATUS_BLOCKCHAIN_PENDING']
					db.session.flush()

					update_feed.delay(handshake.id, shaker.shaker_id, shaker.id)

			else:
				raise Exception(MESSAGE.SHAKER_NOT_FOUND)

		else:
			offchain = int(offchain.replace('m', ''))
			handshake = db.session.query(Handshake).filter(and_(Handshake.id==offchain, Handshake.user_id==user.id)).first()
			if handshake is not None:
				outcome = Outcome.find_outcome_by_id(handshake.outcome_id)
				if outcome.result != handshake.side:
					raise Exception(MESSAGE.HANDSHAKE_NO_PERMISSION)


				# update status to STATUS_BLOCKCHAIN_PENDING
				handshakes = db.session.query(Handshake).filter(and_(Handshake.user_id==user.id, Handshake.outcome_id==outcome.id, Handshake.side==outcome.result)).all()
				shakers = db.session.query(Shaker).filter(and_(Shaker.shaker_id==user.id, Shaker.side==outcome.result, Shaker.handshake_id.in_(db.session.query(Handshake.id).filter(Handshake.outcome_id==outcome.id)))).all()

				for handshake in handshakes:
					handshake.status = HandshakeStatus['STATUS_BLOCKCHAIN_PENDING']
					handshake.bk_status = HandshakeStatus['STATUS_BLOCKCHAIN_PENDING']
					db.session.flush()

					update_feed.delay(handshake.id, handshake.user_id)

				for shaker in shakers:
					shaker.status = HandshakeStatus['STATUS_BLOCKCHAIN_PENDING']
					shaker.bk_status = HandshakeStatus['STATUS_BLOCKCHAIN_PENDING']
					db.session.flush()

					update_feed.delay(handshake.id, shaker.shaker_id, shaker.id)

			else:
				raise Exception(MESSAGE.HANDSHAKE_NOT_FOUND)

		db.session.commit()

		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)

@handshake_routes.route('/rollback', methods=['POST'])
@login_required
def rollback():
	try:
		uid = int(request.headers['Uid'])
		chain_id = int(request.headers.get('ChainId', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
		user = User.find_user_with_id(uid)

		data = request.json
		if data is None:
			raise Exception(MESSAGE.INVALID_DATA)

		offchain = data.get('outcome_id')
		if offchain is None or len(offchain) == 0:
			raise Exception(MESSAGE.INVALID_DATA)

		
		offchain = offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')
		if 'm' in offchain:
			offchain = offchain.replace('m', '')
			handshake = db.session.query(Handshake).filter(and_(Handshake.id==offchain, Handshake.user_id==uid)).first()
			if handshake is not None:
				if handshake.status == CONST.Handshake['STATUS_BLOCKCHAIN_PENDING']:
					handshake.status = handshake.bk_status
					db.session.commit()

					update_feed.delay(handshake.id, user.id)
					return response_ok(handshake.to_json())

			else:
				raise Exception(MESSAGE.HANDSHAKE_EMPTY)
		else:
			offchain = offchain.replace('s', '')
			shaker = db.session.query(Shaker).filter(and_(Shaker.id==offchain, Shaker.shaker_id==uid)).first()
			if shaker is not None:
				if shaker.status == CONST.Handshake['STATUS_BLOCKCHAIN_PENDING']:
					shaker.status = shaker.bk_status
					db.session.commit()

					update_feed.delay(shaker.handshake_id, user.id, shaker.id)
					return response_ok(shaker.to_json())
			else:
				raise Exception(MESSAGE.SHAKER_NOT_FOUND)

		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)

# TODO
@handshake_routes.route('/refund', methods=['POST'])
@login_required
def refund():
	try:
		uid = int(request.headers['Uid'])
		chain_id = int(request.headers.get('ChainId', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
		user = User.find_user_with_id(uid)

		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
