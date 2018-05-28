# -*- coding: utf-8 -*-
import base64
import time
import os
import requests
import hashlib
import sys

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


@handshake_routes.route('/terms')
@jwt_required
def get_terms():
	return response_ok(CONST.Handshake['TERM_OPTIONS'])


@handshake_routes.route('/statuses')
@jwt_required
def get_states():
	return response_ok(CONST.Handshake['STATUS_OPTIONS'])


@handshake_routes.route('/industries')
@jwt_required
def get_industries():
	data = request.args
	public = data.get('public', -1, type=int)

	if public == -1:
		res = Industries.query.all()
	else:
		res = Industries.find_all_industries_with_public_type(public)

	industries = []
	for industry in res:
		industries.append(industry.to_json())
	return response_ok(industries)


@handshake_routes.route('/message/<int:industries_type>')
@jwt_required
def get_sharing_message(industries_type):
	user_id = get_jwt_identity()
	user = User.query.get(user_id)
	response = {}

	industries = Industries.find_industries_with_id(industries_type)
	if industries is not None:
		return response_ok(industries.to_json())
	
	return response_error('Invalid industries type')

@handshake_routes.route('/')
@jwt_required
def get_list():
	user_id = get_jwt_identity()
	user = User.query.get(user_id)

	try:
		data = request.args
		page = data.get('page', 1, type=int)
		page_size = data.get('page_size', 10, type=int)
		chain_id = data.get('chain_id', 4, type=int)
		public = data.get('public', 0, type=int)

		result = {
			'page': page,
			'page_size': page_size,
			'total': 0,
      		'chain_id': chain_id
		}

		skip = (page - 1) * page_size

		query = text('''
			SELECT handshake.*, T.user_id as user_id_shaked
				FROM handshake LEFT OUTER JOIN (select * from tx where user_id = {}) as T ON T.scope_id = handshake.id
				WHERE handshake.chain_id = {} AND handshake.public = {}
				ORDER BY handshake.id desc
				LIMIT {}, {}
		'''.format(user.id, chain_id, public, skip, page_size))

		query_count = text('''
			SELECT count(*) as count FROM (
				SELECT handshake.*, T.user_id as user_id_shaked
				FROM handshake LEFT OUTER JOIN (select * from tx where user_id = {}) as T ON T.scope_id = handshake.id
				WHERE handshake.chain_id = {} AND handshake.public = {}
				ORDER BY handshake.id desc
				LIMIT {}, {}
			) as T
		'''.format(user.id, chain_id, public, skip, page_size))

		if public is not 1:
			query = text('''
				SELECT handshake.*, T.user_id as user_id_shaked
				FROM handshake LEFT OUTER JOIN (select * from tx where user_id = {}) as T ON T.scope_id = handshake.id
				WHERE handshake.chain_id = {} AND (handshake.from_email = '{}' OR handshake.to_email LIKE '%{}%') AND handshake.public = {}
				ORDER BY handshake.id desc
				LIMIT {}, {}
			'''.format(user.id, chain_id, user.email, user.email, public, skip, page_size))

			query_count = text('''
				SELECT count(*) as count FROM (
					SELECT handshake.*, T.user_id as user_id_shaked
					FROM handshake LEFT OUTER JOIN (select * from tx where user_id = {}) as T ON T.scope_id = handshake.id
					WHERE handshake.chain_id = {} AND (handshake.from_email = '{}' OR handshake.to_email LIKE '%{}%') AND handshake.public = {}
				) as T
			'''.format(user.id, chain_id, user.email, user.email, public))

		result_db = db.engine.execute(query)

		total = db.engine.execute(query_count).first()[0]

		json_handshakes = []

		for row in result_db:
			handshake = {
				'id': row['id'],
				'hid': row['hid'],
				'term': row['term'],
				'escrow_date': row['escrow_date'],
				'delivery_date': row['delivery_date'],
				'from_address': row['from_address'],
				'to_address': row['to_address'],
				'description': row['description'],
				'status': row['status'],
				'contract_file': row['contract_file'],
				'contract_file_name': row['contract_file_name'],
				'signed_contract_file': row['signed_contract_file'],
				'industries_type': row['industries_type'],
				'from_email': row['from_email'],
				'to_email': row['to_email'],
				'source': row['source'],
				'public': row['public'],
				'user_id_shaked': row['user_id_shaked'],
			}
			json_handshakes.append(handshake)

		result['total'] = total
		result['data'] = json_handshakes

		return response_ok(result)
	except Exception, ex:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)
		print ex
		return response_error(ex.message)


@handshake_routes.route('/<int:id>')
@jwt_required
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
		user = User.find_user_with_uid(uid)		

		data = request.form
		hs_type = data.get('type', -1, type=int)
		extra_data = data.get('extra_data', '')
		description = data.get('description', '')
		chain_id = data.get('chain_id', CONST.BLOCKCHAIN_NETWORK['RINKEBY'], type=int)
		from_address = data.get('from_address', '')
		to_address = data.get('to_address', '')

		if hs_type != CONST.Handshake['INDUSTRIES_BETTING']:
			return response_error('Handshake type is not betting')

		handshake = Handshake(
			hs_type = hs_type,
			extra_data = extra_data,
			description = description,
			chain_id = chain_id,
			from_address = from_address,
			to_address = to_address,
			user_id = user.id
		)
		
		db.session.commit()

		hs_json = handshake.to_json()
		hs_json["offchain"] = CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + str(handshake.id)

		return response_ok(hs_json)

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@handshake_routes.route('/view_file/<int:hand_shake_id>', methods=['POST'])
@jwt_required
def view_file(hand_shake_id):
	try:
		user_id = get_jwt_identity()
		user = User.query.get(user_id)

		data = request.form
		original = data.get('original', 0, type=int)

		handshake = Handshake.find_handshake_by_id(hand_shake_id)
		if handshake is None:
			raise Exception(MESSAGE.HANDSHAKE_EMPTY)

		if handshake_bl.has_permission_to_open_handshake(user.wallet.address, handshake) == False:
			raise Exception(MESSAGE.HANDSHAKE_NO_PERMISSION)

		if handshake.contract_file is None:
			raise Exception(MESSAGE.HANDSHAKE_NO_CONTRACT_FILE)

		hash = handshake.contract_file
		secret_key = handshake.secret_key

		if original == 0:
			if handshake.status == HandshakeStatus['STATUS_DONE'] and handshake.signed_contract_file and len(handshake.signed_contract_file) > 0:
				hash = handshake.signed_contract_file
				secret_key = handshake.signed_secret_key

		# download file
		filename = '{}.pdf'.format(hash)
		file_path = os.path.abspath(os.path.join(__file__, '../..')) + '/files/pdf/' + filename
		with open(file_path, 'wb') as f:
			for chunk in ipfs.get_file_streaming(hash):
				if chunk:
					f.write(chunk)

		# decrypt file
		filename = '{}_decrypt.pdf'.format(hash)
		outfile_path = os.path.abspath(os.path.join(__file__, '../..')) + '/files/pdf/' + filename
		file_crypto = FileCrypto()
		file_crypto.decrypt_file(file_path, secret_key, outfile_path, g.PASSPHASE)

		contents = None
		with open(outfile_path) as ex:
			contents = ex.read()

		response = Response(contents, mimetype='application/pdf')
		response.headers['Content-Disposition'] = 'inline; filename="{filename}"'.format(filename=handshake.contract_file_name)

		return response
	except Exception as ex:
		return response_error(str(ex))

@handshake_routes.route('/view-file/<int:hand_shake_id>/<token>')
def view_file_with_token(hand_shake_id, token):
	try:
		if token is None:
			raise Exception('Invalid token')

		decoded = decode_token(token)
		user_id = decoded.get('identity', -1)
		if user_id == -1:
			raise Exception('Invalid token')

		user = User.query.get(user_id)
		handshake = Handshake.find_handshake_by_id(hand_shake_id)
		if handshake is None:
			raise Exception(MESSAGE.HANDSHAKE_EMPTY)

		if handshake_bl.has_permission_to_open_handshake(user.wallet.address, handshake) == False:
			raise Exception(MESSAGE.HANDSHAKE_NO_PERMISSION)

		if handshake.contract_file is None and handshake.signed_contract_file is None:
			print '--> no contract'
			raise Exception(MESSAGE.HANDSHAKE_NO_CONTRACT_FILE)

		hash = handshake.contract_file
		secret_key = handshake.secret_key
		if handshake.status == HandshakeStatus['STATUS_DONE'] and handshake.signed_contract_file and len(handshake.signed_contract_file) > 0:
			hash = handshake.signed_contract_file
			secret_key = handshake.signed_secret_key

		# download file
		filename = '{}.pdf'.format(hash)
		file_path = os.path.abspath(os.path.join(__file__, '../..')) + '/files/pdf/' + filename
		with open(file_path, 'wb') as f:
			for chunk in ipfs.get_file_streaming(hash):
				if chunk:
					f.write(chunk)

		# decrypt file
		filename = '{}_decrypt.pdf'.format(hash)
		outfile_path = os.path.abspath(os.path.join(__file__, '../..')) + '/files/pdf/' + filename
		file_crypto = FileCrypto()
		file_crypto.decrypt_file(file_path, secret_key, outfile_path, g.PASSPHASE)

		contents = None
		with open(outfile_path) as ex:
			contents = ex.read()

		response = Response(contents, mimetype='application/pdf')
		response.headers['Content-Disposition'] = 'inline; filename="{filename}"'.format(filename=handshake.contract_file_name)

		return response

	except Exception as ex:
		return str(ex)

@handshake_routes.route('/shake', methods=['POST'])
@jwt_required
def shake():
	try:
		user_id = get_jwt_identity()
		user = User.query.get(user_id)

		chain_id = request.args.get('chain_id', 4, type=int)

		data = request.form
		handshake_id = data.get('handshake_id')
		print 'handshake id {}'.format(handshake_id)
		handshake = Handshake.find_handshake_by_id(handshake_id)

		print 'handshake->', handshake

		if not handshake or (handshake and not handshake.hid):
			raise Exception(MESSAGE.HANDSHAKE_NOT_FOUND)

		if handshake.to_address is not None and len(handshake.to_address) > 0:
			if user.wallet.address not in handshake.to_address:
				raise Exception(MESSAGE.HANDSHAKE_NO_PERMISSION)

		acceptorid = hashlib.md5(user.email).hexdigest()
		print "acceptorid==>", acceptorid

		# TODO: term means `kỳ hạn` not `type`
		bc_data = {
			'acceptorid': acceptorid,
			'address': user.wallet.address,
			'privateKey': user.wallet.private_key,
			'offchain': CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + str(handshake.id),
			'hid': handshake.hid,
			'term': handshake.term,
			'amount': handshake.value if handshake.term != CONST.Handshake['TERM_NONE'] else '0',
			'to_address': user.wallet.address,
		}

		bc_res = requests.post(g.BLOCKCHAIN_SERVER_ENDPOINT + '/cryptosign/shake', data=bc_data, params={'chain_id': chain_id})
		bc_json = bc_res.json()

		if bc_json['status'] != 1:
			raise BcException(bc_json['message'])

		handshake.status = HandshakeStatus['STATUS_BLOCKCHAIN_PENDING']

		db.session.commit()

		add_transaction.delay(bc_json, handshake.id, user.id, chain_id)

		return response_ok(handshake.to_json())
	except Exception, ex:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("shake=>", exc_type, fname, exc_tb.tb_lineno)
		db.session.rollback()
		return response_error(ex.message)


@handshake_routes.route('/deliver', methods=['POST'])
@jwt_required
def deliver():
	try:
		user_id = get_jwt_identity()
		user = User.query.get(user_id)

		chain_id = request.args.get('chain_id', 4, type=int)
		data = request.form
		handshake_id = data.get('handshake_id')
		handshake = Handshake.find_handshake_by_id(handshake_id)

		if not handshake or (handshake and not handshake.hid):
			raise Exception(MESSAGE.HANDSHAKE_NOT_FOUND)

		bc_data = {
			'address': user.wallet.address,
			'privateKey': user.wallet.private_key,
			'offchain': CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + str(handshake.id),
			'hid': handshake.hid,
			'term': handshake.term,
		}

		bc_res = requests.post(g.BLOCKCHAIN_SERVER_ENDPOINT + '/cryptosign/deliver', data=bc_data, params={'chain_id': chain_id})
		bc_json = bc_res.json()
		if bc_json['status'] != 1:
			raise BcException(bc_json['message'])

		handshake.status = HandshakeStatus['STATUS_BLOCKCHAIN_PENDING']

		add_transaction.delay(bc_json, handshake.id, user.id, chain_id)

		db.session.commit()
		handshake_bl.send_noti_for_handshake(handshake, CONST.HANDSHAKE_STATE['DELIVER'])

		return response_ok(handshake.to_json())
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@handshake_routes.route('/withdraw', methods=['POST'])
@jwt_required
def withdraw():
	try:
		user_id = get_jwt_identity()
		user = User.query.get(user_id)

		chain_id = request.args.get('chain_id', 4, type=int)

		data = request.form
		handshake_id = data.get('handshake_id')
		handshake = Handshake.find_handshake_by_id(handshake_id)

		if not handshake or (handshake and not handshake.hid):
			raise Exception(MESSAGE.HANDSHAKE_NOT_FOUND)

		bc_data = {
			'address': user.wallet.address,
			'privateKey': user.wallet.private_key,
			'offchain': CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + str(handshake.id),
			'hid': handshake.hid,
			'term': handshake.term,
		}

		bc_res = requests.post(g.BLOCKCHAIN_SERVER_ENDPOINT + '/cryptosign/withdraw', data=bc_data, params={'chain_id': chain_id})
		bc_json = bc_res.json()
		if bc_json['status'] != 1:
			raise BcException(bc_json['message'])

		handshake.status = HandshakeStatus['STATUS_BLOCKCHAIN_PENDING']

		add_transaction.delay(bc_json, handshake.id, user.id, chain_id)

		db.session.commit()

		return response_ok(handshake.to_json())
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@handshake_routes.route('/accept', methods=['POST'])
@jwt_required
def accept():
	try:
		user_id = get_jwt_identity()
		user = User.query.get(user_id)

		chain_id = request.args.get('chain_id', 4, type=int)

		data = request.form
		handshake_id = data.get('handshake_id')
		handshake = Handshake.find_handshake_by_id(handshake_id)

		if not handshake or (handshake and not handshake.hid):
			raise Exception(MESSAGE.HANDSHAKE_NOT_FOUND)

		bc_data = {
			'address': user.wallet.address,
			'privateKey': user.wallet.private_key,
			'offchain': CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + str(handshake.id),
			'hid': handshake.hid,
			'term': handshake.term,
		}

		bc_res = requests.post(g.BLOCKCHAIN_SERVER_ENDPOINT + '/cryptosign/accept', data=bc_data, params={'chain_id': chain_id})
		bc_json = bc_res.json()
		if bc_json['status'] != 1:
			raise BcException(bc_json['message'])

		handshake.status = HandshakeStatus['STATUS_BLOCKCHAIN_PENDING']

		add_transaction.delay(bc_json, handshake.id, user.id, chain_id)

		db.session.commit()

		return response_ok(handshake.to_json())

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@handshake_routes.route('/reject', methods=['POST'])
@jwt_required
def reject():
	try:
		user_id = get_jwt_identity()
		user = User.query.get(user_id)

		chain_id = request.args.get('chain_id', 4, type=int)

		data = request.form
		handshake_id = data.get('handshake_id')
		handshake = Handshake.find_handshake_by_id(handshake_id)

		if not handshake or (handshake and not handshake.hid):
			raise Exception(MESSAGE.HANDSHAKE_NOT_FOUND)

		bc_data = {
			'address': user.wallet.address,
			'privateKey': user.wallet.private_key,
			'offchain': CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + str(handshake.id),
			'hid': handshake.hid,
			'term': handshake.term,
		}

		bc_res = requests.post(g.BLOCKCHAIN_SERVER_ENDPOINT + '/cryptosign/reject', data=bc_data, params={'chain_id': chain_id})
		bc_json = bc_res.json()
		if bc_json['status'] != 1:
			raise BcException(bc_json['message'])

		handshake.status = HandshakeStatus['STATUS_BLOCKCHAIN_PENDING']

		add_transaction.delay(bc_json, handshake.id, user.id, chain_id)

		db.session.commit()
		handshake_bl.send_noti_for_handshake(handshake, CONST.HANDSHAKE_STATE['REJECT'])
		return response_ok(handshake.to_json())

	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)


@handshake_routes.route('/cancel', methods=['POST'])
@jwt_required
def cancel():
	try:
		user_id = get_jwt_identity()
		user = User.query.get(user_id)

		chain_id = request.args.get('chain_id', 4, type=int)

		data = request.form
		handshake_id = data.get('handshake_id')
		handshake = Handshake.find_handshake_by_id(handshake_id)

		if not handshake or (handshake and not handshake.hid):
			raise Exception(MESSAGE.HANDSHAKE_NOT_FOUND)

		bc_data = {
			'address': user.wallet.address,
			'privateKey': user.wallet.private_key,
			'offchain': CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + str(handshake.id),
			'hid': handshake.hid,
			'term': handshake.term,
		}

		bc_res = requests.post(g.BLOCKCHAIN_SERVER_ENDPOINT + '/cryptosign/cancel', data=bc_data, params={'chain_id': chain_id})
		bc_json = bc_res.json()
		if bc_json['status'] != 1:
			raise BcException(bc_json['message'])

		handshake.status = HandshakeStatus['STATUS_BLOCKCHAIN_PENDING']

		add_transaction.delay(bc_json, handshake.id, user.id, chain_id)

		db.session.commit()

		return response_ok(handshake.to_json())
	except Exception, ex:
		db.session.rollback()
		return response_error(ex.message)
