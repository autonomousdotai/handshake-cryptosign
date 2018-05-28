from flask import Blueprint, request
from app.helpers.response import response_ok, response_error
from app import db
from app.constants import Handshake as HandshakeStatus, CRYPTOSIGN_OFFCHAIN_PREFIX
from app.models import Tx, Handshake
from app.helpers.message import MESSAGE
import app.bl.handshake as handshake_bl
from app.tasks import create_signed_handshake_file, add_payee_signature

event_routes = Blueprint('event', __name__)


@event_routes.route('/', methods=['POST'])
def event():
	tx_id = request.json['txId']
	tx_status = request.json['txStatus']
	block_number = request.json['blockNumber']
	block_time_stamp = request.json['blockTimeStamp']
	events = request.json['events']
	print '-------------------------------'
	print "tx_id = {}, tx_status = {}, block_number = {}, events = {}".format(tx_id, tx_status, block_number, events)

	tx = Tx.find_tx_with_id(tx_id)

	if tx is not None:
		handshake = None
		tx.status = tx_status
		tx.block_number = block_number
		tx.block_time_stamp = block_time_stamp
		tx.transaction_status = tx_status
		if tx_status != 1:
			if tx.scope_id is not None:
				handshake_bl.rollback_handshake_state(tx.scope_id)
		else:
			if 'BasicHandshake.__init' in events:
				data = events['BasicHandshake.__init']
				(hid, offchain, _) = parse_data(data)
				handshake = handshake_bl.save_handshake_for_init_state(hid, offchain.replace(CRYPTOSIGN_OFFCHAIN_PREFIX, ''))
			elif'GroupHandshake.__init' in events:
				data = events['GroupHandshake.__init']
				print ('GroupHandshake>data->', data)
				(hid, offchain, _) = parse_data(data)
				handshake = handshake_bl.save_handshake_for_init_state(hid,offchain.replace(CRYPTOSIGN_OFFCHAIN_PREFIX, ''))
			elif 'PayableHandshake.__init' in events:
				data = events['PayableHandshake.__init']
				(hid, offchain, _) = parse_data(data)
				handshake = handshake_bl.save_handshake_for_init_state(hid, offchain.replace(CRYPTOSIGN_OFFCHAIN_PREFIX, ''))
			elif 'BasicHandshake.__shake' in events:
				data = events['BasicHandshake.__shake']
				(_, offchain, _) = parse_data(data)
				handshake = handshake_bl.save_handshake_for_shake_state(offchain.replace(CRYPTOSIGN_OFFCHAIN_PREFIX, ''))
			elif 'GroupHandshake.__shake' in events:
				data = events['GroupHandshake.__shake']
				(_, offchain, state) = parse_data(data)
				print '---'
				print _
				print '----'
				print state
				print '-'
				print offchain
				handshake = handshake_bl.save_group_handshake_for_shake_state(offchain.replace(CRYPTOSIGN_OFFCHAIN_PREFIX, ''), state)
			elif 'PayableHandshake.__shake' in events:
				data = events['PayableHandshake.__shake']
				(_, offchain, _) = parse_data(data)
				handshake = handshake_bl.save_handshake_for_shake_state(offchain.replace(CRYPTOSIGN_OFFCHAIN_PREFIX, ''), isPayable=True)
			elif 'PayableHandshake.__deliver' in events:
				data = events['PayableHandshake.__deliver']
				(_, offchain, _) = parse_data(data)
				handshake = handshake_bl.save_handshake_for_state(HandshakeStatus['STATUS_ACCEPTED'], offchain.replace(CRYPTOSIGN_OFFCHAIN_PREFIX, ''))
			elif 'PayableHandshake.__withdraw' in events:
				data = events['PayableHandshake.__withdraw']
				(_, offchain, _) = parse_data(data)
				handshake = handshake_bl.save_handshake_for_state(HandshakeStatus['STATUS_DONE'], offchain.replace(CRYPTOSIGN_OFFCHAIN_PREFIX, ''))
			elif 'PayableHandshake.__reject' in events:
				data = events['PayableHandshake.__reject']
				(_, offchain, _) = parse_data(data)
				handshake = handshake_bl.save_handshake_for_state(HandshakeStatus['STATUS_REJECTED'], offchain.replace(CRYPTOSIGN_OFFCHAIN_PREFIX, ''))
			elif 'PayableHandshake.__accept' in events:
				data = events['PayableHandshake.__accept']
				(_, offchain, _) = parse_data(data)
				handshake = handshake_bl.save_handshake_for_state(HandshakeStatus['STATUS_ACCEPTED'], offchain.replace(CRYPTOSIGN_OFFCHAIN_PREFIX, ''))
			elif 'PayableHandshake.__cancel' in events:
				data = events['PayableHandshake.__cancel']
				(_, offchain, _) = parse_data(data)
				handshake = handshake_bl.save_handshake_for_state(HandshakeStatus['STATUS_CANCELLED'], offchain.replace(CRYPTOSIGN_OFFCHAIN_PREFIX, ''))

		print '-----handshake.status', handshake.status

		db.session.commit()

		print '-----handshake.status after', handshake.status

		if handshake:
			print '-----handshake.status done 0', handshake.status

			if handshake_bl.is_group_handshake(handshake):
				if handshake.status == HandshakeStatus['STATUS_GROUP_DONE']:
					if handshake.contract_file and len(handshake.contract_file) > 0:
						print 'add payer signature'
						create_signed_handshake_file.delay(handshake.id)
			else:
				if handshake.status == HandshakeStatus['STATUS_DONE']:
					if handshake.contract_file and len(handshake.contract_file) > 0:
						print 'add payer signature'
						create_signed_handshake_file.delay(handshake.id)

			print '-----handshake.status before 0', handshake.status

			if handshake.status == HandshakeStatus['STATUS_INITED']:
				if handshake.contract_file and len(handshake.contract_file) > 0:
					print 'add payee signature'
					add_payee_signature.delay(handshake.id)
		print '-------------------------------'
		return response_ok()
	else:
		return response_error(message='Please double check your transaction id!')


def parse_data(data):
	offchain = None
	hid = None
	state = -1
	if 'hid' in data:
		hid = data['hid']

	if 'offchain' in data:
		offchain = data['offchain']

	if 'state' in data:
		state = int(data['state'])

	return (hid, offchain, state)
