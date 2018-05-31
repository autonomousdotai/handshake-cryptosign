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

from flask import Blueprint, request, g, current_app, Response
from sqlalchemy import or_, text
from werkzeug.utils import secure_filename

from app.helpers.response import response_ok, response_error
from app.helpers.utils import is_valid_email, isnumber, formalize_description
from app.helpers.message import MESSAGE
from app.helpers.bc_exception import BcException
from app.helpers.decorators import login_required
from app import db, s3, ipfs
from app.models import User, Handshake, Tx, Wallet, Industries
from app.constants import Handshake as HandshakeStatus
from datetime import datetime


handshake_routes = Blueprint('handshake', __name__)


@handshake_routes.route('/<int:id>')
@login_required
def detail(id):
	uid = int(request.headers['Uid'])
	chain_id = int(request.headers.get('ChainId', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
	user = User.find_user_with_id(uid)

	try:
		handshake = Handshake.find_handshake_by_id(id)
		if not handshake:
			raise Exception('Handshake {} is not found.'.format(id))
		if user.wallet.address not in [handshake.from_address, handshake.to_address]:
			raise Exception(MESSAGE.HANDSHAKE_NO_PERMISSION)

		handshake_json = handshake.to_json()

		return response_ok(handshake_json)

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
		is_private = data.get('is_private', 0)
		outcome_id = data.get('outcome_id')
		odds = float(data.get('odds'))
		amount = float(data.get('amount'))
		currency = data.get('currency', 'ETH')
		side = data.get('side', CONST.SIDE_TYPE['SUPPORT'])

		if hs_type != CONST.Handshake['INDUSTRIES_BETTING']:
			raise Exception(MESSAGE.HANDSHAKE_INVALID_BETTING_TYPE)

		# filter all handshakes which able be to match first
		handshakes = handshake_bl.find_all_matched_handshakes(side, odds)
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
				remaining_amount=odds*amount
			)
			db.session.add(handshake)
			db.session.flush()

			handshake_bl.add_handshake_to_solrservice(handshake, user)
			db.session.commit()

			# response data
			hs_json = handshake.to_json()
			hs_json['id'] = CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + str(handshake.id)

			return response_ok(hs_json)
		else:
			pass

		return response_ok()

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@handshake_routes.route('/shake', methods=['GET'])
@login_required
def handshakes():
	uid = int(request.headers['Uid'])
	chain_id = int(request.headers.get('ChainId', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
	user = User.find_user_with_id(uid)

	return response_ok()