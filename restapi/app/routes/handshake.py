# -*- coding: utf-8 -*-
import base64
import time
import os
import requests
import hashlib
import sys
import json

import app.constants as CONST
import app.bl.handshake as handshake_bl

from flask import Blueprint, request, g, Response
from sqlalchemy import or_, text

from app.helpers.response import response_ok, response_error
from app.helpers.utils import is_valid_email, isnumber, formalize_description
from app.helpers.message import MESSAGE
from app.helpers.bc_exception import BcException
from app.helpers.decorators import login_required
from app import db, s3, ipfs
from app.models import User, Handshake, Tx, Shaker, Outcome
from app.constants import Handshake as HandshakeStatus
from datetime import datetime


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

		supports = handshake_bl.find_available_support_handshakes(outcome_id)
		against = handshake_bl.find_available_against_handshakes(outcome_id)

		arr_supports = []
		for support in supports:
			arr_supports.append(support.to_json())

		arr_against = []
		for against in arr_against:
			arr_against.append(against.to_json())

		respose = {
			"support": arr_supports,
			"against": arr_against
		}

		return response_ok(respose)

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
		odds = float(data.get('odds'))
		amount = float(data.get('amount'))
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

		# filter all handshakes which able be to match first
		handshakes = handshake_bl.find_all_matched_handshakes(side, odds, outcome_id)
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
				remaining_amount=odds*amount,
				from_address=from_address
			)
			db.session.add(handshake)
			db.session.flush()

			handshake_bl.add_handshake_to_solrservice(handshake, user)
			db.session.commit()

			# response data
			hs_json = handshake.to_json()
			hs_json['offchain'] = CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + 'm' + str(handshake.id)

			return response_ok(hs_json)
		else:
			arr_hs = []
			shaker_amount = amount
			for handshake in handshakes:

				amount_for_handshake = 0
				if shaker_amount > handshake.remaining_amount:
					shaker_amount -= handshake.remaining_amount
					amount_for_handshake = handshake.remaining_amount
					handshake.remaining_amount = 0

				else:
					amount_for_handshake = amount
					shaker_amount -= amount
					handshake.remaining_amount -= amount
				
				# create shaker
				shaker = Shaker(
					shaker_id=user.id,
					amount=amount_for_handshake,
					currency=currency,
					odds=odds,
					win_value=odds*amount,
					side=side,
					handshake_id=handshake.id
				)
				shaker_amount -= amount

				db.session.add(shaker)
				db.session.flush()

				handshake_bl.add_handshake_to_solrservice(handshake, user, shaker=shaker)
				shaker_json = handshake.to_json()
				shaker_json['offchain'] = CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + 's' + str(shaker.id)
				arr_hs.append(shaker_json)
				
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
					remaining_amount=odds*shaker_amount,
					from_address=from_address
				)
				db.session.add(handshake)
				db.session.flush()

				handshake_bl.add_handshake_to_solrservice(handshake, user)

			db.session.commit()
			return response_ok(arr_hs)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@handshake_routes.route('/update', methods=['POST'])
@login_required
def update():
	try:
		uid = int(request.headers['Uid'])
		chain_id = int(request.headers.get('ChainId', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
		user = User.find_user_with_id(uid)

		return response_ok()
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

		amount = float(data.get('amount'))
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

		handshakes = handshake_bl.find_all_joined_handshakes(side, outcome_id)
		if len(handshakes) > 0:
			arr_hs = []
			shaker_amount = amount
			for handshake in handshakes:
				amount_for_handshake = 0
				if shaker_amount > handshake.remaining_amount:
					shaker_amount -= handshake.remaining_amount
					amount_for_handshake = handshake.remaining_amount
					handshake.remaining_amount = 0

				else:
					amount_for_handshake = amount
					shaker_amount -= amount
					handshake.remaining_amount -= amount

				# create shaker
				shaker = Shaker(
					shaker_id=user.id,
					amount=amount_for_handshake,
					currency=currency,
					odds=1/handshake.odds,
					win_value=1/handshake.odds*amount,
					side=side,
					handshake_id=handshake.id
				)
				shaker_amount -= amount

				db.session.add(shaker)
				db.session.flush()

				handshake_bl.add_handshake_to_solrservice(handshake, user, shaker=shaker)
				shaker_json = handshake.to_json()
				shaker_json['offchain'] = CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + 's' + str(shaker.id)
				arr_hs.append(shaker_json)
				
				if shaker_amount <= 0:
					break

			db.session.commit()	
			message = ''
			if shaker_amount > 0:
				message = 'Your remaining money: {} after shaked!'.format(shaker_amount)
			
			return response_ok(arr_hs, message=message)
		else:
			return response_error(MESSAGE.BET_NOT_FOUND)

		return response_ok()

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)

@handshake_routes.route('/rollback', methods=['POST'])
@login_required
def rollback():
	# TODO: rollback
	try:
		uid = int(request.headers['Uid'])
		chain_id = int(request.headers.get('ChainId', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
		user = User.find_user_with_id(uid)

		return response_ok()
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)