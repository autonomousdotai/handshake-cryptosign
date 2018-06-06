#!/usr/bin/python
# -*- coding: utf-8 -*-
import hashlib
import os
import sys
import time
import requests
import app.constants as CONST
import math

from decimal import Decimal
from flask import g
from app import db, fcm, sg, firebase
from sqlalchemy import and_, or_, func, text
from app.constants import Handshake as HandshakeStatus, CRYPTOSIGN_OFFCHAIN_PREFIX
from app.models import Handshake, User, Shaker, Outcome
from app.helpers.utils import parse_date_to_int, is_valid_email, parse_shakers_array
from app.helpers.bc_exception import BcException
from app.tasks import update_feed
from datetime import datetime
from app.helpers.message import MESSAGE
from datetime import datetime
from sqlalchemy import literal


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

def save_status_all_bet_which_user_win(user_id, outcome):
	handshakes = []
	shakers = []
	if outcome.result == CONST.RESULT_TYPE['DRAW'] or outcome.result == CONST.RESULT_TYPE['PENDING']:
		print 'outcome result is {}'.format(outcome.result)
		return

	handshakes = db.session.query(Handshake).filter(and_(Handshake.user_id==user_id, Handshake.outcome_id==outcome.id, Handshake.side==outcome.result)).all()
	print 'handshakes {}'.format(handshakes)
	shakers = db.session.query(Shaker).filter(and_(Shaker.shaker_id==user_id, Shaker.side==outcome.result, Shaker.handshake_id.in_(db.session.query(Handshake.id).filter(Handshake.outcome_id==outcome.id)))).all()
	print 'shakers {}'.format(shakers)

	for handshake in handshakes:
		handshake.status = HandshakeStatus['STATUS_DONE']
		handshake.bk_status = HandshakeStatus['STATUS_DONE']
		db.session.flush()

		update_feed.delay(handshake.id, handshake.user_id)

	for shaker in shakers:
		shaker.status = HandshakeStatus['STATUS_DONE']
		shaker.bk_status = HandshakeStatus['STATUS_DONE']
		db.session.flush()

		update_feed.delay(handshake.id, shaker.shaker_id, shaker.id)

def save_collect_state_for_maker(handshake):
	if handshake is not None:
		outcome = Outcome.find_outcome_by_id(handshake.outcome_id)
		if outcome is not None:
			if handshake.side == outcome.result:
				handshake.status = HandshakeStatus['STATUS_DONE']
				handshake.bk_status = HandshakeStatus['STATUS_DONE']
				db.session.flush()

				save_status_all_bet_which_user_win(handshake.user_id, outcome)
				

def save_collect_state_for_shaker(shaker):
	if shaker is not None:
		handshake = Handshake.find_handshake_by_id(shaker.handshake_id)
		outcome = Outcome.find_outcome_by_id(handshake.outcome_id)

		if outcome is not None:
			if shaker.side == outcome.result:
				shaker.status = HandshakeStatus['STATUS_DONE']
				shaker.bk_status = HandshakeStatus['STATUS_DONE']

				handshake = Handshake.find_handshake_by_id(shaker.handshake_id)
				handshake.status = HandshakeStatus['STATUS_DONE']
				handshake.bk_status = HandshakeStatus['STATUS_DONE']

				save_status_all_bet_which_user_win(shaker.shaker_id, outcome)

def update_feed_result_for_outcome(outcome):
	print 'update_feed_result_for_outcome --> {}, {}'.format(outcome.id, outcome.result)

	handshakes = db.session.query(Handshake).filter(Handshake.outcome_id==outcome.id).all()
	shakers = db.session.query(Shaker).filter(Shaker.handshake_id.in_(db.session.query(Handshake.id).filter(Handshake.outcome_id==outcome.id))).all()

	for handshake in handshakes:
		print '--> {}'.format(handshake)
		update_feed.delay(handshake.id, handshake.user_id)

	for shaker in shakers:
		print '--> {}'.format(shaker)
		update_feed.delay(handshake.id, shaker.shaker_id, shaker.id)


def save_handshake_for_event(event_name, offchain, outcome=None):
	if 'report' in offchain:
		if outcome is None:
			print 'outcome is None'
			return

		# report1: mean that support win
		# report2: mean that against win
		# report0: mean that noone win
		result = offchain.replace('report', '')
		print 'result {}'.format(result)
		if len(result) > -1:
			result = int(result)
			outcome.result = result
			db.session.flush()

			update_feed_result_for_outcome(outcome)

	elif 's' in offchain: # shaker
		offchain = offchain.replace('s', '')
		shaker = Shaker.find_shaker_by_id(int(offchain))
		print 'shaker = {}'.format(shaker)
		if shaker is not None:
			if '__shake' in event_name:
				print '__shake'
				shaker.status = HandshakeStatus['STATUS_SHAKER_SHAKED']
				shaker.bk_status = HandshakeStatus['STATUS_SHAKER_SHAKED']
				db.session.flush()

				handshake = Handshake.find_handshake_by_id(shaker.handshake_id)
				update_feed.delay(handshake.id, shaker.shaker_id, shaker.id)

			elif '__collect' in event_name:
				print '__collect'
				# update status of shaker and handshake to done
				# find all bets belongs to this outcome which user join
				# update all statuses (shaker and handshake) of them to done
				save_collect_state_for_shaker(shaker)

	else: # maker
		offchain = offchain.replace('m', '')
		handshake = Handshake.find_handshake_by_id(int(offchain))
		print 'handshake = {}, offchain = {}'.format(handshake, offchain)
		if handshake is not None:
			if '__init' in event_name:
				print '__init'
				handshake.status = HandshakeStatus['STATUS_INITED']
				handshake.bk_status = HandshakeStatus['STATUS_INITED']
				db.session.flush()

				update_feed.delay(handshake.id, handshake.user_id)

			elif '__uninit' in event_name:
				print '__uninit'
				handshake.status = HandshakeStatus['STATUS_MAKER_UNINITED']
				handshake.bk_status = HandshakeStatus['STATUS_MAKER_UNINITED']
				db.session.flush()

				update_feed.delay(handshake.id, handshake.user_id)

			elif '__collect' in event_name:
				print '__collect'
				# update status of shaker and handshake to done
				# find all bets belongs to this outcome which user join
				# update all statuses (shaker and handshake) of them to done
				save_collect_state_for_maker(handshake)


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

def find_all_matched_handshakes(side, odds, outcome_id, amount):
	outcome = db.session.query(Outcome).filter(and_(Outcome.result==CONST.RESULT_TYPE['PENDING'], Outcome.id==outcome_id)).first()
	if outcome is not None:
		win_value = amount*odds
		if win_value - amount > 0:
			d = Decimal(win_value/(win_value-amount))
			v = round(d, 2)
			query = text('''
						SELECT * FROM handshake where outcome_id = {} and odds <= {} and remaining_amount > 0 and status = {} and side != {} ORDER BY odds ASC, remaining_amount DESC;
						'''.format(outcome_id, v, CONST.Handshake['STATUS_INITED'], side))

			handshakes = []
			result_db = db.engine.execute(query)
			for row in result_db:
				handshake = Handshake(
					id=row['id'],
					hs_type=row['hs_type'],
					extra_data=row['extra_data'],
					description=row['description'],
					chain_id=row['chain_id'],
					is_private=row['is_private'],
					user_id=row['user_id'],
					outcome_id=row['outcome_id'],
					odds=row['odds'],
					amount=row['amount'],
					currency=row['currency'],
					side=row['side'],
					win_value=row['win_value'],
					remaining_amount=row['remaining_amount'],
					from_address=row['from_address'],
					shake_count=row['shake_count'],
					view_count=row['view_count'],
					date_created=row['date_created'],
					date_modified=row['date_modified']
				)
				handshakes.append(handshake)
			return handshakes
	return []

def find_all_joined_handshakes(side, outcome_id):
	outcome = db.session.query(Outcome).filter(and_(Outcome.result==CONST.RESULT_TYPE['PENDING'], Outcome.id==outcome_id)).first()
	if outcome is not None:
		handshakes = db.session.query(Handshake).filter(and_(Handshake.side!=side, Handshake.outcome_id==outcome_id, Handshake.remaining_amount>0, Handshake.status==CONST.Handshake['STATUS_INITED'])).order_by(Handshake.odds.asc()).all()
		return handshakes
	return []

def find_available_support_handshakes(outcome_id):
	outcome = db.session.query(Outcome).filter(and_(Outcome.result==CONST.RESULT_TYPE['PENDING'], Outcome.id==outcome_id)).first()
	if outcome is not None:
		handshakes = db.session.query(Handshake.odds, func.sum(Handshake.amount).label('amount')).filter(and_(Handshake.side==CONST.SIDE_TYPE['SUPPORT'], Handshake.outcome_id==outcome_id, Handshake.remaining_amount>0, Handshake.status==CONST.Handshake['STATUS_INITED'])).group_by(Handshake.odds).order_by(Handshake.odds.asc()).all()
		return handshakes
	return []

def find_available_against_handshakes(outcome_id):
	outcome = db.session.query(Outcome).filter(and_(Outcome.result==CONST.RESULT_TYPE['PENDING'], Outcome.id==outcome_id)).first()
	if outcome is not None:
		handshakes = db.session.query(Handshake.odds, func.sum(Handshake.amount).label('amount')).filter(and_(Handshake.side==CONST.SIDE_TYPE['AGAINST'], Handshake.outcome_id==outcome_id, Handshake.remaining_amount>0, Handshake.status==CONST.Handshake['STATUS_INITED'])).group_by(Handshake.odds).order_by(Handshake.odds.asc()).all()
		return handshakes
	return []
