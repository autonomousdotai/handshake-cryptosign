import sys
from flask import Flask
from werkzeug.datastructures import FileStorage

from app.factory import make_celery
from app.core import db, s3, configure_app, wm, ipfs
from app.extensions.file_crypto import FileCrypto
from app.models import Tx, Handshake

import time
import app.constants as CONST
import json
import os, hashlib
import requests

app = Flask(__name__)
# config app
configure_app(app)

# db
db.init_app(app)
# s3
s3.init_app(app)
# init ipfs
ipfs.init_app(app)

#
celery = make_celery(app)



@celery.task()
def add_transaction(bc_json, handshake_id, user_id, chain_id):
	try:
		print 'debug add transaction', bc_json, handshake_id, user_id
		bc_data = bc_json.get('data', {})
		rs_hash = bc_data.get('hash', '')
		rs_payload = bc_data.get('payload', '')
		rs_from_address = bc_data.get('fromAddress', '')
		rs_to_address = bc_data.get('toAddress', '')
		rs_amount = bc_data.get('amount', '')
		rs_arguments = bc_data.get('arguments', {})
		rs_contract_name = bc_data.get('contractName', '')
		rs_contract_address = bc_data.get('contractAddress', '')
		rs_contract_method = bc_data.get('contractMethod', '')
		tx = Tx(
			hash=rs_hash,
			scope='handshake',
			scope_id=handshake_id,
			contract_name=rs_contract_name,
			contract_address=rs_contract_address,
			contract_method=rs_contract_method,
			arguments=json.dumps(rs_arguments),
			amount=rs_amount,
			from_address=rs_from_address,
			to_address=rs_to_address,
			payload=rs_payload,
			user_id=user_id,
			chain_id=chain_id
		)
		db.session.add(tx)
		db.session.commit()
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print("add_transaction=>",exc_type, fname, exc_tb.tb_lineno)


@celery.task()
def add_request_eth_transaction(bc_json, user_id, chain_id):
	print 'debug add request eth transaction', bc_json, user_id
	bc_data = bc_json.get('data', {})
	rs_hash = bc_data.get('hash', '')
	rs_from_address = bc_data.get('fromAddress', '')
	rs_to_address = bc_data.get('toAddress', '')
	rs_amount = bc_data.get('amount', '')
	rs_contract_method = bc_data.get('contractMethod', '')
	tx = Tx(
		hash=rs_hash,
		contract_method=rs_contract_method,
		amount=rs_amount,
		from_address=rs_from_address,
		to_address=rs_to_address,
		user_id=user_id,
		chain_id=chain_id
	)
	db.session.add(tx)
	db.session.commit()


@celery.task()
def upload_handshake_file(handshake_id, destination, filename, extension):
	print 'debug upload', handshake_id, destination, filename, extension
	handshake = Handshake.query.get(handshake_id)
	print handshake
	if handshake:
		path = os.path.join(app.config['UPLOAD_DIR'], destination)
		if extension.endswith('pdf'):
			print 'pdf file'
		else:
			print 'todo convert to pdf file'

		hash = ipfs.upload_file(path)
		handshake.contract_file = hash
		handshake.contract_file_name = filename
		db.session.commit()

	return None

@celery.task()
def create_handshake_file(handshake_id):
	print '----------------------------'
	print 'create handshake file --> ', handshake_id
	handshake = Handshake.query.get(handshake_id)
	print handshake
	if handshake:
		print 'create new contract'
		millis = int(round(time.time()))
		filename = '{}_{}.pdf'.format(millis, hashlib.md5(os.urandom(32)).hexdigest())
		file_path = os.path.abspath(os.path.join(__file__, '../..')) + '/files/pdf/' + filename
		f = open(file_path, "w+")
		f.close()

		path = wm.add_description(handshake.description, handshake.industries_type, file_path)

		# encrypt file
		print 'begin encrypt file'
		filename = '{}_{}_crypto.pdf'.format(millis, hashlib.md5(os.urandom(32)).hexdigest())
		output_filepath = os.path.abspath(os.path.join(__file__, '../..')) + '/files/pdf/' + filename
		file_crypto = FileCrypto()
		secret_key = file_crypto.encrypt_file(path, output_filepath, app.config['PASSPHASE'])
		print 'secret_key = {}'.format(secret_key)

		hash = ipfs.upload_file(output_filepath)
		handshake.contract_file = hash
		handshake.contract_file_name = filename
		handshake.secret_key = secret_key
		db.session.commit()

	print '----------------------------'
	return None


@celery.task()
def create_signed_handshake_file(handshake_id):
	print '----------------------------'
	print 'start create signed handshake file'
	handshake = Handshake.query.get(handshake_id)
	if not handshake:
		print 'not handshake'
		return

	if not handshake.contract_file:
		print 'no contract file'
		return

	if handshake.status != CONST.Handshake['STATUS_DONE']:
		print 'handshake is not done yet'
		return

	if handshake.signed_contract_file is not None:
		print 'handshake created signed contract file'
		return

	# get all transaction
	txs = Tx.query \
		.filter(Tx.scope == 'handshake', Tx.scope_id == handshake_id, Tx.status == CONST.Tx['STATUS_SUCCESS']) \
		.order_by(Tx.date_created.asc())\
		.all()
	if len(txs) < 2:
		print 'transaction is less than 2'
		return

	if handshake.contract_file:
		print 'start download contract file'

		hash = handshake.contract_file
		# download contract file
		millis = int(round(time.time()))
		filename = '{}_{}.pdf'.format(millis, hash)
		file_path = os.path.abspath(os.path.join(__file__, '../..')) + '/files/pdf/' + filename
		with open(file_path, 'wb') as f:
			for chunk in ipfs.get_file_streaming(hash):
				if chunk:
					f.write(chunk)
		f.close()

		print 'start decrypt contract file'
		filename = '{}_{}_decrypt.pdf'.format(millis, hash)
		outfile_path = os.path.abspath(os.path.join(__file__, '../..')) + '/files/pdf/' + filename
		file_crypto = FileCrypto()
		file_crypto.decrypt_file(file_path, handshake.secret_key, outfile_path, app.config['PASSPHASE'])

		print 'start add watermark', file_path
		# add watermark
		signed_file = os.path.abspath(wm.add_payer_signature(outfile_path, handshake.industries_type, txs[1]))
		# push to ipfs
		print 'start push signed to ipfs'
		if len(signed_file) > 0:
			# encrypt file
			print 'begin encrypt file'
			filename = '{}_{}_crypto.pdf'.format(millis, hashlib.md5(os.urandom(32)).hexdigest())
			output_encrypt_filepath = os.path.abspath(os.path.join(__file__, '../..')) + '/files/pdf/' + filename

			secret_key = file_crypto.encrypt_file(signed_file, output_encrypt_filepath, app.config['PASSPHASE'])
			print 'secret_key = {}'.format(secret_key)

			hash = ipfs.upload_file(output_encrypt_filepath)
			handshake.signed_contract_file = hash
			handshake.signed_secret_key = secret_key
			db.session.commit()
			print 'add signed contract file success', hash
	print '----------------------------'
	return None

@celery.task()
def add_payee_signature(handshake_id):
	print '----------------------------'
	print 'debug add payee signature ', handshake_id
	handshake = Handshake.query.get(handshake_id)
	print handshake
	if handshake:
		# get transaction
		tx = Tx.query \
			.filter(Tx.scope == 'handshake', Tx.scope_id == handshake_id, Tx.status == CONST.Tx['STATUS_SUCCESS']) \
			.order_by(Tx.date_created.asc())\
			.first()

		if tx is not None:
			hash = handshake.contract_file
			# download contract file
			millis = int(round(time.time()))

			filename = '{}_{}.pdf'.format(millis, hash)
			file_path = os.path.abspath(os.path.join(__file__, '../..')) + '/files/pdf/' + filename
			with open(file_path, 'wb') as f:
				for chunk in ipfs.get_file_streaming(hash):
					if chunk:
						f.write(chunk)
			f.close()

			print 'start decrypt contract file'
			filename = '{}_{}_decrypt.pdf'.format(millis, hash)
			outfile_path = os.path.abspath(os.path.join(__file__, '../..')) + '/files/pdf/' + filename
			file_crypto = FileCrypto()
			file_crypto.decrypt_file(file_path, handshake.secret_key, outfile_path, app.config['PASSPHASE'])

			print 'start add watermark', file_path
			# add watermark
			signed_file = os.path.abspath(wm.add_payee_signature(outfile_path, handshake.industries_type, tx))
			# push to ipfs
			print 'start push signed to ipfs'
			if len(signed_file) > 0:
				# encrypt file
				print 'begin encrypt file'
				filename = '{}_{}_crypto.pdf'.format(millis, hashlib.md5(os.urandom(32)).hexdigest())
				output_encrypt_filepath = os.path.abspath(os.path.join(__file__, '../..')) + '/files/pdf/' + filename

				secret_key = file_crypto.encrypt_file(signed_file, output_encrypt_filepath, app.config['PASSPHASE'])
				print 'secret_key = {}'.format(secret_key)

				hash = ipfs.upload_file(output_encrypt_filepath)
				handshake.contract_file = hash
				handshake.secret_key = secret_key
				db.session.commit()
				print 'add signature contract file success', hash
	print '----------------------------'
	return None

@celery.task()
def upload_handshake_file(handshake_id, destination, filename, extension):
	print 'debug upload', handshake_id, destination, filename, extension
	handshake = Handshake.query.get(handshake_id)
	print handshake
	if handshake:
		path = os.path.join(app.config['UPLOAD_DIR'], destination)
		if extension.endswith('pdf'):
			print 'pdf file'
		else:
			print 'todo convert to pdf file'

		# encrypt file
		print 'begin encrypt file'
		final_file_path = wm.add_empty_page(path)
		output_filepath = os.path.abspath(os.path.join(__file__, '../..')) + '/files/pdf/' + filename
		file_crypto = FileCrypto()
		secret_key = file_crypto.encrypt_file(final_file_path, output_filepath, app.config['PASSPHASE'])

		hash = ipfs.upload_file(output_filepath)
		handshake.contract_file = hash
		handshake.contract_file_name = filename
		handshake.secret_key = secret_key
		db.session.commit()
		print hash


	return None
