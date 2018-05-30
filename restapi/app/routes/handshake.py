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
import app.bl.user as user_bl

from uuid import uuid4
from flask import Blueprint, request, g, current_app, Response
from sqlalchemy import or_, text
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity, decode_token

from app.helpers.response import response_ok, response_error
from app.helpers.utils import is_valid_email, isnumber, formalize_description
from app.helpers.message import MESSAGE
from app.helpers.bc_exception import BcException
from app.helpers.decorators import login_required
from app import db, s3, ipfs
from app.models import User, Handshake, Tx, Wallet, Industries
from app.constants import Handshake as HandshakeStatus
from app.tasks import add_transaction, upload_handshake_file, create_handshake_file
from app.extensions.file_crypto import FileCrypto
from datetime import datetime


handshake_routes = Blueprint('handshake', __name__)


@handshake_routes.route('/<int:id>')
@login_required
def detail(id):
	user_id = get_jwt_identity()
	user = User.query.get(user_id)

	try:
		handshake = Handshake.find_handshake_by_id(id)
		if not handshake:
			raise Exception('Handshake {} is not found.'.format(id))
		if user.wallet.address not in [handshake.from_address, handshake.to_address]:
			raise Exception('You don\'t have permission to retrieve this handshake')

		handshake_json = handshake.to_json()
		handshake_json['txs'] = []
		txs = Tx.find_tx_with_hand_shake_id(handshake.id)
		for tx in txs:
			handshake_json['txs'].append(tx.to_json())

		return response_ok(handshake_json)

	except Exception, ex:
		return response_error(ex.message)


@handshake_routes.route('/init', methods=['POST'])
@login_required
def init():
	try:
		uid = int(request.headers['Uid'])
		chain_id = int(request.headers.get('ChainId', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
		user = User.find_user_with_uid(uid)		

		data = request.json
		if data is None:
			raise Exception(MESSAGE.INVALID_DATA)

		hs_type = data.get('type', -1)
		extra_data = data.get('extra_data', '')
		description = data.get('description', '')
		from_address = data.get('from_address', '')
		to_address = data.get('to_address', '')
		is_private = data.get('is_private', 0)
		shake_user_ids = data.get('shake_user_ids', '')

		if hs_type != CONST.Handshake['INDUSTRIES_BETTING']:
			raise Exception(MESSAGE.HANDSHAKE_INVALID_BETTING_TYPE)

		handshake = Handshake(
			hs_type=hs_type,
			extra_data=extra_data,
			description=description,
			chain_id=chain_id,
			from_address=from_address,
			to_address=to_address,
			user_id=user.id,
			shake_user_ids=shake_user_ids,
			is_private=is_private
		)
		db.session.add(handshake)
		db.session.flush()

		handshake_bl.add_handshake_to_solrservice(handshake, user)
		db.session.commit()

		# response data
		hs_json = handshake.to_json()
		hs_json['id'] = CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + str(handshake.id)

		return response_ok(hs_json)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)

@handshake_routes.route('/update', methods=['POST'])
@login_required
def update():
	try:
		uid = int(request.headers['Uid'])
		chain_id = int(request.headers.get('ChainId', CONST.BLOCKCHAIN_NETWORK['RINKEBY']))
		user = User.find_user_with_uid(uid)

		data = request.json
		if data is None:
			raise Exception(MESSAGE.INVALID_DATA)

		offchain = data.get('id', -1)
		if offchain == -1 or CONST.CRYPTOSIGN_OFFCHAIN_PREFIX not in offchain:
			raise Exception(MESSAGE.HANDSHAKE_NOT_FOUND)

		offchain = int(offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, ''))
		handshake = Handshake.query.filter(Handshake.user_id == user.id, Handshake.id == offchain).first()
		if handshake is None:
			raise Exception(MESSAGE.HANDSHAKE_NO_PERMISSION)

		hs_type = data.get('type', -1)
		extra_data = data.get('extra_data', '')
		description = data.get('description', '')
		from_address = data.get('from_address', '')
		to_address = data.get('to_address', '')
		state = data.get('state', -1)
		shake_user_ids = data.get('shake_user_ids', '')

		if hs_type != -1:
			if hs_type != CONST.Handshake['INDUSTRIES_BETTING']:
				raise Exception(MESSAGE.HANDSHAKE_INVALID_BETTING_TYPE)
			handshake.hs_type = hs_type

		if len(extra_data) != 0:
			handshake.extra_data = extra_data

		if len(description) != 0:
			handshake.description = description

		if chain_id != -1:
			handshake.chain_id = chain_id

		if len(from_address) != 0:
			handshake.from_address = from_address

		if len(to_address) != 0:
			handshake.to_address = to_address

		if state != -1:
			handshake.state = state

		if len(shake_user_ids) != 0:
			handshake.shake_user_ids = shake_user_ids

		db.session.flush()

		handshake_bl.add_handshake_to_solrservice(handshake, user)
		db.session.commit()

		# response data
		hs_json = handshake.to_json()
		hs_json["id"] = CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + str(handshake.id)

		return response_ok(hs_json)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
