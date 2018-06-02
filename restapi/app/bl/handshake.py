#!/usr/bin/python
# -*- coding: utf-8 -*-
import hashlib
import os
import sys
import time
import requests
import app.constants as CONST

from flask import g
from app import db, fcm, sg
from sqlalchemy import and_, or_
from app.constants import Handshake as HandshakeStatus, CRYPTOSIGN_OFFCHAIN_PREFIX
from app.models import Handshake, User, Shaker, Outcome
from app.helpers.utils import parse_date_to_int, is_valid_email, parse_shakers_array
from app.tasks import add_transaction
from app.helpers.bc_exception import BcException
from datetime import datetime
from app.helpers.message import MESSAGE
from datetime import datetime
from sqlalchemy import literal


def init_handshake_for_user(user):
	handshakes = Handshake.query.filter_by(to_address=user.email).all()
	if len(handshakes) > 0:
		for handshake in handshakes:
			if handshake.from_address is not None:
				handshake.to_address = user.wallet.address
				bc_json = init_handshake(handshake)
				add_transaction.delay(bc_json, handshake.id, handshake.user_id)

def init_handshake(handshake):
	send_noti_for_handshake(handshake)
	return bc_init_handshake(handshake)

def bc_init_handshake(handshake):
	try:
		to_address = '' if is_valid_email(handshake.to_address) else handshake.to_address
		if "," in handshake.to_email:
			to_address = ", ".join([hashlib.md5(email.strip()).hexdigest() for email in str(handshake.to_email).split(",")])

		wallet = Wallet.find_wallet_by_address(handshake.from_address)
		if wallet is not None:
			bc_data = {
				'address': wallet.address,
				'privateKey': wallet.private_key,
				'value': handshake.value,
				'term': handshake.term,
				'escrow_date': parse_date_to_int(handshake.escrow_date) if handshake.escrow_date else 0,
				'delivery_date': parse_date_to_int(handshake.delivery_date) if handshake.delivery_date else 0,
				'to_address': to_address,
				'offchain': CRYPTOSIGN_OFFCHAIN_PREFIX + str(handshake.id)
			}

			bc_res = requests.post(g.BLOCKCHAIN_SERVER_ENDPOINT + '/cryptosign/init', data=bc_data, params={'chain_id': handshake.chain_id})

			bc_json = bc_res.json()

			print "bc_res=>", bc_json

			if bc_json['status'] != 1:
				raise BcException(bc_json['message'])

			return bc_json
	except Exception, ex:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)

def save_handshake_for_init_state(hid, offchain):
	print "hid = {}, offchain = {}".format(hid, offchain)
	handshake = Handshake.find_handshake_by_id(offchain)
	if handshake is not None:
		handshake.status = HandshakeStatus['STATUS_INITED']
		handshake.bk_status = HandshakeStatus['STATUS_INITED']
		handshake.hid = hid
		send_noti_for_handshake(handshake, CONST.HANDSHAKE_STATE['INTIATED'])
	return handshake

def save_handshake_for_shake_state(offchain, isPayable=False):
	print "handshakeId = {}".format(offchain)
	handshake = Handshake.find_handshake_by_id(offchain)
	if handshake is not None:
		if isPayable:
			handshake.status = HandshakeStatus['STATUS_SHAKED']
			handshake.bk_status = HandshakeStatus['STATUS_SHAKED']
			send_noti_for_handshake(handshake, CONST.HANDSHAKE_STATE['SHAKED'])
		else:
			handshake.status = HandshakeStatus['STATUS_DONE']
			handshake.bk_status = HandshakeStatus['STATUS_DONE']
			send_noti_for_handshake(handshake, CONST.HANDSHAKE_STATE['DONE'])

	return handshake


def save_group_handshake_for_shake_state(offchain, state, isPayable=False):
	handshake = Handshake.find_handshake_by_id(offchain)
	if handshake is not None:

		if int(str(state)) == int(str(HandshakeStatus['STATUS_GROUP_SHAKED'])):
			handshake.status = HandshakeStatus['STATUS_SHAKED']
			handshake.bk_status = HandshakeStatus['STATUS_SHAKED']
			send_noti_for_handshake(handshake, CONST.HANDSHAKE_STATE['SHAKED'])

		elif state == HandshakeStatus['STATUS_GROUP_DONE']:

			handshake.status = HandshakeStatus['STATUS_DONE']
			handshake.bk_status = HandshakeStatus['STATUS_DONE']
			send_noti_for_handshake(handshake, CONST.HANDSHAKE_STATE['DONE'])

	return handshake


def save_handshake_for_event(event_name, offchain):
	if 's' in offchain: # shaker
		offchain = offchain.replace('s', '')
		shaker = Shaker.find_shaker_by_id(int(offchain))
		print 'shaker = {}'.format(shaker)
		if shaker is not None:
			if '__shake' in event_name:
				print '__shake'
				shaker.status = HandshakeStatus['STATUS_SHAKER_SHAKED']
				shaker.bk_status = HandshakeStatus['STATUS_SHAKER_SHAKED']

				# update solr
				handshake = Handshake.find_handshake_by_id(shaker.handshake_id)
				user = User.find_user_with_id(handshake.user_id)
				add_handshake_to_solrservice(handshake, user, shaker)

	else: # maker
		offchain = offchain.replace('m', '')
		handshake = Handshake.find_handshake_by_id(int(offchain))
		print 'handshake = {}'.format(handshake)
		if handshake is not None:
			if '__init' in event_name:
				print '__init'
				handshake.status = HandshakeStatus['STATUS_INITED']
				handshake.bk_status = HandshakeStatus['STATUS_INITED']

				# update solr
				user = User.find_user_with_id(handshake.user_id)
				add_handshake_to_solrservice(handshake, user)


def rollback_handshake_state(handshake_id):
	handshake = Handshake.find_handshake_by_id(handshake_id)
	if handshake is not None:
		handshake.status = handshake.bk_status
	return handshake


def update_to_address_for_user(user):
	# handshakes = Handshake.query.filter(Handshake.to_address==user.email).all()
	handshakes = Handshake.query.filter(Handshake.to_address.contains(user.email)).all()
	print "handshakes of this user: ", handshakes
	for handshake in handshakes:
		to_address = str(handshake.to_address).split(",")
		flag = False
		for idx, item in enumerate(to_address):
			if item.strip() == str(user.email).strip():
				print "found email in handshake ", user.wallet.address
				flag = True
				to_address[idx] = user.wallet.address
		if flag:
			handshake.to_address = ", ".join([address for address in to_address])
			print "update new to_address->", handshake.to_address


def is_need_fire_notification_for_handshake(handshake):
	now = datetime.now()
	delta = (now - handshake.date_created).seconds / 60
	if delta < 5:
		return False
	return True

def is_group_handshake(handshake):
	if handshake.to_address is not None:
		addresses = str(handshake.to_address).split(",")
		if len(addresses) > 1:
			return True
	return False

def has_permission_to_open_handshake(wallet_address, handshake):
	print 'public --> {}'.format(handshake.public)
	if int(handshake.public) is 1:
		return True

	if handshake.from_address != wallet_address and wallet_address not in handshake.to_address:
		return False
	return True

# refer document: https://docs.google.com/document/d/1iKS7bgSm8DUcvpFE3GqWb1pWcdJWXxYeuxULNgsOIec/edit
def send_noti_for_handshake(handshake, handshake_state=CONST.HANDSHAKE_STATE['INIT'], source='web'):
	print "send push notification ..."
	fcm_send_notification(handshake, handshake_state)

	print "send email ..."
	send_email(handshake, handshake_state, source)


def send_email(handshake, handshake_state, source):
	(subject_payee, content_payee), (subject_payer, content_payer) = build_email_for_handshake(handshake, handshake_state)
	list_email_to = [ {"email": email} for email in str(handshake.to_email).split(",")]
	print "send list mail:", list_email_to
	if handshake_state == CONST.HANDSHAKE_STATE['INTIATED']:
		sg.sendMany(handshake.from_email, list_email_to, subject_payer, content_payer)
		sg.send("handshake@autonomous.nyc", handshake.from_email, subject_payee, content_payee)

	elif handshake_state == CONST.HANDSHAKE_STATE['DONE']:
		sg.sendMany("handshake@autonomous.nyc", list_email_to, subject_payer, content_payer)
		sg.send("handshake@autonomous.nyc", handshake.from_email, subject_payee, content_payee)

def build_email_for_handshake(handshake, handshake_state):
	subject_payer = ''
	subject_payee = ''
	content_payee = ''
	content_payer = ''

	if handshake_state == CONST.HANDSHAKE_STATE['INIT']:
		subject_payer = "{} wants to Handshake with you!".format(handshake.from_email)
		content_payer = "<html><head><title>Handshake</title></head><body>{} needs your cryptographic signature on an agreement!. <br><br>Visit <a href='https://www.autonomous.ai/handshake'>www.autonomous.ai/handshake</a> to add your blockchain-protected mark <br><br> Or download Handshake for mobile on <a href='https://itunes.apple.com/us/app/crypto-handshake/id1360132818?ls=1&mt=8'>iOS</a> or <a href='https://play.google.com/store/apps/details?id=com.mobile_handshake'>Google play</a> </body></html>".format(handshake.from_email)

		subject_payee = "You are initiating a Handshake!"
		content_payee = "<html><head><title>Handshake</title></head><body>Your Handshake is being processed on the blockchain! We will send you a status update once it has been successfully initiated. <br><br> Handshake Team </body></html>"

	elif handshake_state == CONST.HANDSHAKE_STATE['INTIATED']:
		subject_payer = "Someone wants to shake your hand!"
		content_payer = "<html><head><title>Handshake</title></head><body>{} has extended a Handshake. <br> To view and respond, download and open Handshake for mobile on <a href='https://itunes.apple.com/us/app/crypto-handshake/id1360132818?ls=1&mt=8'>iOS</a> or <a href='https://play.google.com/store/apps/details?id=com.mobile_handshake'>Google play</a> <br><br> Handshake Team </body></html>".format(handshake.from_email)

		subject_payee = "You have initiated a Handshake!"
		content_payee = "<html><head><title>Handshake</title></head><body>Handshake with {} initiated! We have sent the other party a notification as well. You are now able to view its status on your mobile app. Just tap 'My Handshakes' to keep track of your agreements. </body></html>".format(handshake.to_email)

	elif handshake_state == CONST.HANDSHAKE_STATE['SHAKED']:
		subject_payer = "Handshake: Contract in progress."
		content_payer = "<html><head><title>Handshake</title></head><body>{} is working on their side of the agreement. We will send you a status update when it has been delivered! <br></br> In the meantime, sign in to the app on <a href='https://www.autonomous.ai/handshake'>www.autonomous.ai/hanshake</a>, or on mobile to view your Handshake details. </body></html>".format(handshake.from_email)

		subject_payee = "Your Handshake has been signed. Time to get to work!"
		content_payee = "<html><head><title>Handshake</title></head><body>{} signed your agreement! You now have deliverables pending. Sign in to the app on <a href='https://www.autonomous.ai/handshake>www.autonomous.ai/hanshake</a> or on mobile to view your Handshake and mark the task done.</body></html>".format(handshake.to_email)

	elif handshake_state == CONST.HANDSHAKE_STATE['DELIVER']:
		subject_payer = "Handshake: {} has delivered. 7 days to reject.".format(handshake.from_email)
		content_payer = "<html><head><title>Handshake</title></head><body> {} has completed their side of the agreement. You have 7 days to reject if you wish, after which they will automatically be able to withdraw their payment.</body></html>".format(handshake.from_email)

		subject_payee = "Handshake: Payment from {} available in 7 days.".format(handshake.to_email)
		content_payee = "<html><head><title>Handshake</title></head><body>Congrats! {} has been notified that you have completed your side of the agreement. They have a 7 day window to reject, after which you will be able to withdraw payment instantly.</body></html>".format(handshake.to_email)

	elif handshake_state == CONST.HANDSHAKE_STATE['REJECT']:
		subject_payer = "Handshake: You have 14 days to accept new work"
		content_payer = "<html><head><title>Handshake</title></head><body> We have sent a rejection notification to {}. They have 14 days to send a new offer or work for you to accept, after which the contract will terminate automatically. </body></html>".format(handshake.from_email)

		subject_payee = "Handshake: Your offer has been rejected."
		content_payee = "<html><head><title>Handshake</title></head><body>Sorry, {} has rejected your side of the agreement. The contract will be valid for 14 more days for you both to work it out or try again, after which it will terminate</body></html>".format(handshake.to_email)

	elif handshake_state == CONST.HANDSHAKE_STATE['DONE']:
		subject_payer = "Handshake: Complete!"
		content_payer = "<html><head><title>Handshake</title></head><body> Congrats! Your Handshake with {} is complete. You can now view your Handshake in the app, share it on your networks, or simply keep it as evidence of a promise! <br><br> Thanks for using Handshake! <br><br> Shake hands, make friends. <br> <a href='https://www.facebook.com/share.php?u=https://www.autonomous.ai/handshake-digital-signature'> Share on facebook</a> <a href='https://twitter.com/intent/tweet?url=https://www.autonomous.ai/handshake-digital-signature'> Share on twitter</a> <br><br> We’d love to hear your thoughts. Send us an email at <a href=\"mailto:handshake@autonomous.nyc\">handshake@autonomous.nyc</a> - help us make Handshake better! </body></html>".format(handshake.from_email)

		subject_payee = "Handshake: Complete!"
		content_payee = "<html><head><title>Handshake</title></head><body> Congrats! Your Handshake with {} is complete. You can now view your Handshake in the app, share it on your networks, or simply keep it as evidence of a promise! <br><br> Thanks for using Handshake! <br><br> Shake hands, make friends. <br> <a href='https://www.facebook.com/share.php?u=https://www.autonomous.ai/handshake-digital-signature'> Share on facebook</a> <a href='https://twitter.com/intent/tweet?url=https://www.autonomous.ai/handshake-digital-signature'> Share on twitter</a> <br><br> We’d love to hear your thoughts. Send us an email at <a href=\"mailto:handshake@autonomous.nyc\">handshake@autonomous.nyc</a> - help us make Handshake better! </body></html>".format(handshake.to_email)


	return ((subject_payee, content_payee), (subject_payer, content_payer))


def fcm_send_notification(handshake, handshake_state=CONST.HANDSHAKE_STATE['INIT']):
	try:
		body_payer, body_payee = build_fcm_body_for_handshake(handshake, handshake_state)
		if len(body_payer) != 0 or len(body_payee) != 0:
			devices = []
			if handshake_state == CONST.HANDSHAKE_STATE['INTIATED']:
				print 'send push notification for INTIATED state'
				if is_need_fire_notification_for_handshake(handshake):
					print 'send to payee'
					devices = db.session.query(Device.device_token).filter(Device.user_id.in_(db.session.query(Wallet.user_id).filter(Wallet.address==handshake.from_address))).all()
					print "device payee=>", devices
					send_push(devices, "Handshake", body_payee, data_message={'data': handshake.to_json()})

				print 'send to payer'
				query = db.session.query(Device.device_token).filter(Device.user_id.in_(db.session.query(Wallet.user_id).filter(literal(handshake.to_address).contains(Wallet.address))))

				print query

				devices = query.all()
				print "device payer=>", devices
				send_push(devices, "Handshake", body_payer, data_message={'data': handshake.to_json()})

			elif handshake_state == CONST.HANDSHAKE_STATE['DONE']:
				print 'send push notification for DONE state'
				devices = db.session.query(Device.device_token).filter(Device.user_id.in_(db.session.query(Wallet.user_id).filter(Wallet.address==handshake.from_address))).all()
				send_push(devices, "Handshake", body_payee, data_message={'data': handshake.to_json()})

				devices = db.session.query(Device.device_token).filter(Device.user_id.in_(db.session.query(Wallet.user_id).filter(literal(handshake.to_address).contains(Wallet.address)))).all()
				send_push(devices, "Handshake", body_payer, data_message={'data': handshake.to_json()})
	except Exception as ex:
		print "error on fcm_send_notification->", ex.message


def build_fcm_body_for_handshake(handshake, handshake_state):
	body_payer = ''
	body_payee = ''

	if handshake_state == CONST.HANDSHAKE_STATE['INIT']:
		body_payee = 'You are initiating a Handshake.'

	elif handshake_state == CONST.HANDSHAKE_STATE['INTIATED']:
		body_payer = 'Someone wants to shake your hand.'
		body_payee = 'You have initiated a Handshake!'

	elif handshake_state == CONST.HANDSHAKE_STATE['SHAKED']:
		body_payer = 'Contract in progress.'
		body_payee = 'Deliverables pending.'

	elif handshake_state == CONST.HANDSHAKE_STATE['DELIVER']:
		body_payer = 'You have 7 days to reject.'
		body_payee = 'Payment available in 7 days.'

	elif handshake_state == CONST.HANDSHAKE_STATE['REJECT']:
		body_payer = 'You have 14 days to accept a new offer.'
		body_payee = 'Your offer has been rejected.'

	elif handshake_state == CONST.HANDSHAKE_STATE['DONE']:
		body_payer = 'Handshake: Complete!'
		body_payee = 'Handshake: Complete!'

	return (body_payer, body_payee)

def send_push(devices, title, body, data_message):
	if len(devices) > 0:
		dvs = []
		for device in devices:
			dvs.append(device[0])
		print "devices --> {}".format(dvs)
		fcm.push_multi_devices(devices=dvs, title=title, body=body, data_message=data_message)


def add_handshake_to_solrservice(handshake, user, shaker=None):
	outcome = Outcome.find_outcome_by_id(handshake.outcome_id)
	_id = CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + 'm' + str(handshake.id)
	amount = handshake.amount
	status = handshake.status

	if shaker is not None:
		_id = CONST.CRYPTOSIGN_OFFCHAIN_PREFIX + 's' + str(shaker.shaker_id)
		amount = shaker.amount
		status = shaker.status

	hs = {
		"id": _id,
		"hid_s": -1,
		"type_i": handshake.hs_type,
		"state_i": handshake.state,
		"status_i": status,
		"init_user_id_i": user.id,
		"chain_id_i": handshake.chain_id,
		"shake_user_ids_is": [],
		"text_search_ss": [handshake.description],
		"shake_count_i": handshake.shake_count,
		"view_count_i": handshake.view_count,
		"comment_count_i": 0,
		"init_at_i": int(time.mktime(handshake.date_created.timetuple())),
		"last_update_at_i": int(time.mktime(handshake.date_modified.timetuple())),
		"is_private_i": handshake.is_private,
		"extra_data_s": handshake.extra_data,
		"remaining_amount_f": handshake.remaining_amount,
		"amount_f": amount,
		"outcome_id_i": handshake.outcome_id,
		"odds_f": handshake.odds,
		"currency_s": handshake.currency,
		"side_i": handshake.side,
		"win_value_f": handshake.win_value,
		"from_address_s": handshake.from_address,
		"result_i": outcome.result
	}

	print "add to solr -> {}".format(hs)

	arr_handshakes = []
	arr_handshakes.append(hs)
	endpoint = "{}/handshake/update".format(g.SOLR_SERVICE)
	data = {
		"add": arr_handshakes
	}
	
	res = requests.post(endpoint, json=data)
	if res.status_code > 400:
		raise Exception('SOLR service is failed.')
	
	json = res.json()
	return json

def find_all_matched_handshakes(side, odds, outcome_id):
	handshakes = db.session.query(Handshake).filter(and_(Handshake.side!=side, Handshake.outcome_id==outcome_id, Handshake.odds==float(1/odds), Handshake.remaining_amount>0, Handshake.status==CONST.Handshake['STATUS_INITED'])).all()
	return handshakes

def find_all_joined_handshakes(side, outcome_id):
	if side == CONST.SIDE_TYPE['SUPPORT']:
		handshakes = db.session.query(Handshake).filter(and_(Handshake.side!=side, Handshake.outcome_id==outcome_id, Handshake.remaining_amount>0, Handshake.status==CONST.Handshake['STATUS_INITED'])).order_by(Handshake.odds.asc()).all()
		return handshakes
	else:
		handshakes = db.session.query(Handshake).filter(and_(Handshake.side!=side, Handshake.outcome_id==outcome_id, Handshake.remaining_amount>0, Handshake.status==CONST.Handshake['STATUS_INITED'])).order_by(Handshake.odds.asc()).all()
		return handshakes

def find_available_support_handshakes(outcome_id):
	handshakes = db.session.query(Handshake).filter(and_(Handshake.side==CONST.SIDE_TYPE['SUPPORT'], Handshake.outcome_id==outcome_id, Handshake.remaining_amount>0, Handshake.status==CONST.Handshake['STATUS_INITED'])).order_by(Handshake.odds.desc()).all()
	return handshakes

def find_available_against_handshakes(outcome_id):
	handshakes = db.session.query(Handshake).filter(and_(Handshake.side==CONST.SIDE_TYPE['AGAINST'], Handshake.outcome_id==outcome_id, Handshake.remaining_amount>0, Handshake.status==CONST.Handshake['STATUS_INITED'])).order_by(Handshake.odds.asc()).all()
	return handshakes
