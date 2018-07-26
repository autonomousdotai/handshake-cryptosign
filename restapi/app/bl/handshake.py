#!/usr/bin/python
# -*- coding: utf-8 -*-
import hashlib
import os
import sys
import time
import requests
import json
import app.constants as CONST
import app.bl.match as match_bl

from decimal import *
from flask import g
from app import db, fcm, sg, firebase
from sqlalchemy import and_, or_, func, text
from app.constants import Handshake as HandshakeStatus, CRYPTOSIGN_OFFCHAIN_PREFIX
from app.models import Handshake, User, Shaker, Outcome
from app.helpers.bc_exception import BcException
from app.tasks import update_feed, add_shuriken, send_mail
from app.helpers.message import MESSAGE
from app.helpers.utils import utc_to_local
from datetime import datetime

getcontext().prec = 18


def save_status_all_bet_which_user_win(user_id, outcome):
	handshakes = []
	shakers = []
	if outcome.result == CONST.RESULT_TYPE['DRAW'] or outcome.result == CONST.RESULT_TYPE['PENDING']:
		print 'outcome result is {}'.format(outcome.result)
		return None, None

	handshakes = db.session.query(Handshake).filter(or_(and_(Handshake.status==HandshakeStatus['STATUS_COLLECT_FAILED'], Handshake.user_id==user_id, Handshake.outcome_id==outcome.id, Handshake.side==outcome.result), and_(Handshake.status==HandshakeStatus['STATUS_INITED'], Handshake.user_id==user_id, Handshake.outcome_id==outcome.id, Handshake.side==outcome.result), and_(Handshake.status==HandshakeStatus['STATUS_COLLECT_PENDING'], Handshake.user_id==user_id, Handshake.outcome_id==outcome.id, Handshake.side==outcome.result))).all()
	print 'handshakes {}'.format(handshakes)
	shakers = db.session.query(Shaker).filter(or_(and_(Shaker.status==HandshakeStatus['STATUS_COLLECT_FAILED'], Shaker.shaker_id==user_id, Shaker.side==outcome.result, Shaker.handshake_id.in_(db.session.query(Handshake.id).filter(Handshake.outcome_id==outcome.id))), and_(Shaker.status==HandshakeStatus['STATUS_COLLECT_PENDING'], Shaker.shaker_id==user_id, Shaker.side==outcome.result, Shaker.handshake_id.in_(db.session.query(Handshake.id).filter(Handshake.outcome_id==outcome.id))), and_(Shaker.status==HandshakeStatus['STATUS_SHAKER_SHAKED'], Shaker.shaker_id==user_id, Shaker.side==outcome.result, Shaker.handshake_id.in_(db.session.query(Handshake.id).filter(Handshake.outcome_id==outcome.id))))).all()
	print 'shakers {}'.format(shakers)

	for handshake in handshakes:
		handshake.bk_status = handshake.status
		handshake.status = HandshakeStatus['STATUS_DONE']
		db.session.merge(handshake)

	for shaker in shakers:
		shaker.bk_status = shaker.status
		shaker.status = HandshakeStatus['STATUS_DONE']
		db.session.merge(shaker)
		
	db.session.flush()
	return handshakes, shakers

def save_collect_state_for_maker(handshake):
	if handshake is not None:
		outcome = Outcome.find_outcome_by_id(handshake.outcome_id)
		if outcome is not None:
			if handshake.side == outcome.result:
				shaker = Shaker.find_shaker_by_handshake_id(handshake.id)
				shaker.bk_status = shaker.status
				shaker.status = HandshakeStatus['STATUS_DONE']

				db.session.merge(shaker)
				db.session.flush()
				handshakes, shakers = save_status_all_bet_which_user_win(handshake.user_id, outcome)
				
				if shakers is None:
					shakers = []	
				shakers.append(shaker)
				return handshakes, shakers

def save_collect_state_for_shaker(shaker):
	if shaker is not None:
		handshake = Handshake.find_handshake_by_id(shaker.handshake_id)
		outcome = Outcome.find_outcome_by_id(handshake.outcome_id)

		if outcome is not None:
			if shaker.side == outcome.result:
				handshake.bk_status = handshake.status
				handshake.status = HandshakeStatus['STATUS_DONE']

				db.session.merge(handshake)
				db.session.flush()
				handshakes, shakers = save_status_all_bet_which_user_win(shaker.shaker_id, outcome)
				
				if handshakes is None:
					handshakes = []
				handshakes.append(handshake)
				return handshakes, shakers

	return None, None


def save_refund_state_for_shaker(shaker):
	if shaker is not None:
		handshake = Handshake.find_handshake_by_id(shaker.handshake_id)
		outcome = Outcome.find_outcome_by_id(handshake.outcome_id)

		if outcome is not None:
			handshakes = db.session.query(Handshake).filter(and_(Handshake.user_id==shaker.shaker_id, Handshake.outcome_id==handshake.outcome_id)).all()
			shakers = db.session.query(Shaker).filter(and_(Shaker.shaker_id==shaker.shaker_id, Shaker.handshake_id.in_(db.session.query(Handshake.id).filter(Handshake.outcome_id==handshake.outcome_id)))).all()

			for hs in handshakes:
				hs.bk_status = hs.status
				hs.status = HandshakeStatus['STATUS_REFUNDED']
				db.session.merge(hs)

			for sk in shakers:
				sk.bk_status = sk.status
				sk.status = HandshakeStatus['STATUS_REFUNDED']
				db.session.merge(sk)
				
			db.session.flush()
			return handshakes, shakers

	return None, None

def save_dispute_state_all(outcome_id, state):
	handshakes = []
	shakers = []
	handshakes = db.session.query(Handshake).filter(Handshake.outcome_id == outcome_id).all()
	for hs in handshakes:
		hs.bk_status = hs.status
		hs.status = state
		db.session.merge(hs)

		shakers = db.session.query(Shaker).filter(Shaker.handshake_id == hs.id).all()
		for shaker in shakers:
			shaker.bk_status = shaker.status
			shaker.status = state
			db.session.merge(shaker)
	db.session.flush()
	return handshakes, shakers

def save_refund_state_for_maker(handshake):
	if handshake is not None:
		outcome = Outcome.find_outcome_by_id(handshake.outcome_id)

		if outcome is not None:
			handshakes = db.session.query(Handshake).filter(and_(Handshake.user_id==handshake.user_id, Handshake.outcome_id==handshake.outcome_id)).all()
			shakers = db.session.query(Shaker).filter(and_(Shaker.shaker_id==handshake.user_id, Shaker.handshake_id.in_(db.session.query(Handshake.id).filter(Handshake.outcome_id==outcome.id)))).all()

			for hs in handshakes:
				hs.bk_status = hs.status
				hs.status = HandshakeStatus['STATUS_REFUNDED']
				db.session.merge(hs)

			for sk in shakers:
				sk.bk_status = sk.status
				shaker.sk = HandshakeStatus['STATUS_REFUNDED']
				db.session.merge(sk)
				
			db.session.flush()
			return handshakes, shakers

	return None, None


def has_valid_shaker(handshake):
	if handshake is not None:
		shakers = handshake.shakers.all()
		if shakers is not None:
			for sk in shakers:
				if sk.status == HandshakeStatus['STATUS_SHAKER_SHAKED']:
					return True
	return False


def data_need_set_result_for_outcome(outcome):
    	print 'data_need_set_result_for_outcome --> {}, {}'.format(outcome.id, outcome.result)

	if outcome.result == -1:
		return None, None

	handshakes = db.session.query(Handshake).filter(Handshake.outcome_id==outcome.id).all()
	shakers = db.session.query(Shaker).filter(Shaker.handshake_id.in_(db.session.query(Handshake.id).filter(Handshake.outcome_id==outcome.id))).all()
	
	for hs in handshakes:
		if not has_valid_shaker(hs) and hs.status == HandshakeStatus['STATUS_INITED']:
			hs.bk_status = hs.status
			hs.status = HandshakeStatus['STATUS_MAKER_SHOULD_UNINIT']
			db.session.merge(hs)
			db.session.flush()

	return handshakes, shakers

# when time exceed report time and there is no result or outcome result is draw
def can_refund(handshake, shaker=None):
    	if handshake is None and shaker is None:
		return False

	outcome = None
	if handshake is not None:
		if handshake.status == HandshakeStatus['STATUS_REFUNDED']:
			return False

		outcome = Outcome.find_outcome_by_id(handshake.outcome_id)

	else:
		if shaker.status == HandshakeStatus['STATUS_REFUNDED']:
			return False
		
		handshake = Handshake.find_handshake_by_id(shaker.handshake_id)
		outcome = Outcome.find_outcome_by_id(handshake.outcome_id)


	if outcome is not None and \
		outcome.hid is not None:

		if outcome.result == CONST.RESULT_TYPE['DRAW'] or (match_bl.is_exceed_report_time(outcome.match_id) and outcome.result == -1):
			return True

	return False

def parse_inputs(inputs):
	offchain = ''
	hid = ''
	state = -1

	if 'offchain' in inputs:
		offchain = inputs['offchain']

	if 'hid' in inputs:
		hid = inputs['hid']

	if 'state' in inputs:
		state = inputs['state']

	return offchain, hid, state


def save_handshake_method_for_event(method, inputs):
	offchain, hid, state = parse_inputs(inputs)
	if method == 'init' or method == 'initTestDrive':
		offchain = offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')
		offchain = int(offchain.replace('m', ''))
		handshake = Handshake.find_handshake_by_id(offchain)
		if handshake is not None:
			handshake.bk_status = handshake.status
			handshake.status = HandshakeStatus['STATUS_INIT_FAILED']
			db.session.flush()

			if 'maker' in inputs: # free-bet
				user = User.find_user_with_id(handshake.user_id)
				if user is not None and user.free_bet == 1:
					user.free_bet = 0
					db.session.flush()

			arr = []
			arr.append(handshake)
			return arr, None

	elif method == 'shake' or method == 'shakeTestDrive':
		offchain = offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')
		offchain = int(offchain.replace('s', ''))
		shaker = Shaker.find_shaker_by_id(offchain)
		if shaker is not None:
			if shaker.status == HandshakeStatus['STATUS_PENDING']:
				shaker = rollback_shake_state(shaker)

			shaker.bk_status = shaker.status
			shaker.status = HandshakeStatus['STATUS_SHAKE_FAILED']
			db.session.flush()

			if 'taker' in inputs: # free-bet
				user = User.find_user_with_id(shaker.shaker_id)
				if user is not None and user.free_bet == 1:
					user.free_bet = 0
					db.session.flush()

			arr = []
			arr.append(shaker)
			return None, arr

	elif method == 'uninit' or method == 'uninitTestDrive':
		offchain = offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')
		offchain = int(offchain.replace('m', ''))
		handshake = Handshake.find_handshake_by_id(offchain)
		if handshake is not None:
			handshake.bk_status = handshake.status
			handshake.status = HandshakeStatus['STATUS_MAKER_UNINIT_FAILED']
			db.session.flush()

			if method == 'uninitTestDrive':
				user = User.find_user_with_id(handshake.user_id)
				if user is not None:
					user.free_bet = 0
					db.session.flush()

			arr = []
			arr.append(handshake)
			return arr, None

	elif method == 'collect' or method == 'collectTestDrive':
		offchain = offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')

		if 'm' in offchain:
			offchain = int(offchain.replace('m', ''))
			handshake = Handshake.find_handshake_by_id(offchain)
			if handshake is not None:
				handshake.bk_status = handshake.status
				handshake.status = HandshakeStatus['STATUS_COLLECT_FAILED']
				db.session.flush()

				arr = []
				arr.append(handshake)
				return arr, None

		elif 's' in offchain:
			offchain = int(offchain.replace('s', ''))
			shaker = Shaker.find_shaker_by_id(offchain)
			if shaker is not None:
				shaker.bk_status = shaker.status
				shaker.status = HandshakeStatus['STATUS_COLLECT_FAILED']
				db.session.flush()

				arr = []
				arr.append(shaker)
				return None, arr

	elif method == 'refund':
		offchain = offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')

		if 'm' in offchain:
			offchain = int(offchain.replace('m', ''))
			handshake = Handshake.find_handshake_by_id(offchain)
			if handshake is not None:
				handshake.bk_status = handshake.status
				handshake.status = HandshakeStatus['STATUS_REFUND_FAILED']
				db.session.flush()

				arr = []
				arr.append(handshake)
				return arr, None

		elif 's' in offchain:
			offchain = int(offchain.replace('s', ''))
			shaker = Shaker.find_shaker_by_id(offchain)
			if shaker is not None:
				shaker.bk_status = shaker.status
				shaker.status = HandshakeStatus['STATUS_REFUND_FAILED']
				db.session.flush()

				arr = []
				arr.append(shaker)
				return None, arr

	elif method == 'report':
		hid = int(hid)
		outcome = Outcome.find_outcome_by_hid(hid)
		if outcome is not None and outcome.result == CONST.RESULT_TYPE['PROCESSING']:
			outcome.result = CONST.RESULT_TYPE['PENDING']
			db.session.flush()

	return None, None


def save_failed_handshake_method_for_event(method, tx):
	if method == 'init' or method == 'initTestDrive':
		offchain = tx.offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')
		offchain = int(offchain.replace('m', ''))
		handshake = Handshake.find_handshake_by_id(offchain)
		if handshake is not None:
			handshake.status = HandshakeStatus['STATUS_INIT_FAILED']
			db.session.flush()
	
			if method == 'initTestDrive': # free-bet
				user = User.find_user_with_id(handshake.user_id)
				if user is not None and user.free_bet == 1:
					user.free_bet = 0
					db.session.flush()

			arr = []
			arr.append(handshake)
			return arr, None

	elif method == 'shake' or method == 'shakeTestDrive':
		offchain = tx.offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')
		offchain = int(offchain.replace('s', ''))
		shaker = Shaker.find_shaker_by_id(offchain)
		if shaker is not None:
			if shaker.status == HandshakeStatus['STATUS_PENDING']:
				shaker = rollback_shake_state(shaker)

			shaker.status = HandshakeStatus['STATUS_SHAKE_FAILED']
			db.session.flush()

			if method == 'shakeTestDrive': # free-bet
				user = User.find_user_with_id(shaker.shaker_id)
				if user is not None and user.free_bet == 1:
					user.free_bet = 0
					db.session.flush()

			arr = []
			arr.append(shaker)
			return None, arr

	elif method == 'report':
		payload = tx.payload
		data = json.loads(payload)

		if '_options' in data:
			options = data['_options']
			if 'onchainData' in options:
				onchain = options['onchainData']
				if 'hid' in onchain:
					hid = int(onchain['hid'])
					outcome =Outcome.find_outcome_by_hid(hid)
					if outcome is not None and outcome.result == CONST.RESULT_TYPE['PROCESSING']:
						outcome.result = CONST.RESULT_TYPE['PENDING']
						db.session.flush()

		return None, None

	return None, None


def save_handshake_for_event(event_name, inputs):
	offchain, hid, state = parse_inputs(inputs)
	offchain = offchain.replace(CONST.CRYPTOSIGN_OFFCHAIN_PREFIX, '')

	if event_name == '__createMarket':
		offchain = int(offchain.replace('createMarket', ''))
		outcome = Outcome.find_outcome_by_id(offchain)
		if outcome is not None:
			outcome.hid = hid
			db.session.flush()

		return None, None

	elif event_name == '__report':
		print '__report'
		# report1: mean that support win
		# report2: mean that against win
		# report0: mean that no one win
		result = offchain.replace('report', '')
		print 'result {}'.format(result)
		outcome = Outcome.find_outcome_by_hid(hid)
		if len(result) > -1:
			result = int(result)
			outcome.result = result

			db.session.flush()
			return data_need_set_result_for_outcome(outcome)

		return None, None

	elif event_name == '__shake':
		print '__shake'
		offchain = offchain.replace('s', '')
		shaker = Shaker.find_shaker_by_id(int(offchain))
		if shaker is not None:
			print 'shaker = {}'.format(shaker)
			shaker.status = HandshakeStatus['STATUS_SHAKER_SHAKED']
			shaker.bk_status = HandshakeStatus['STATUS_SHAKER_SHAKED']

			db.session.flush()
			# Add shuriken
			if shaker.free_bet == 1:
				add_shuriken.delay(shaker.shaker_id, CONST.SHURIKEN_TYPE['FREE'])
			else:
				add_shuriken.delay(shaker.shaker_id, CONST.SHURIKEN_TYPE['REAL'])

			arr = []
			arr.append(shaker)
			return None, arr

		return None, None

	elif event_name == '__collect':
		print '__collect'

		if 's' in offchain:
			offchain = offchain.replace('s', '')
			shaker = Shaker.find_shaker_by_id(int(offchain))
			if shaker is not None:
				# update status of shaker and handshake to done
				# find all bets belongs to this outcome which user join
				# update all statuses (shaker and handshake) of them to done
				return save_collect_state_for_shaker(shaker)

		elif 'm' in offchain:
			offchain = offchain.replace('m', '')
			handshake = Handshake.find_handshake_by_id(int(offchain))
			if handshake is not None:
				# update status of shaker and handshake to done
				# find all bets belongs to this outcome which user join
				# update all statuses (shaker and handshake) of them to done
				return save_collect_state_for_maker(handshake)

		return None, None

	elif event_name == '__init':
		print '__init'
		offchain = offchain.replace('m', '')
		handshake = Handshake.find_handshake_by_id(int(offchain))
		if handshake is not None:
			handshake.status = HandshakeStatus['STATUS_INITED']
			handshake.bk_status = HandshakeStatus['STATUS_INITED']

			db.session.flush()

			arr = []
			arr.append(handshake)

			# Add shuriken
			if handshake.free_bet == 1:
				add_shuriken.delay(handshake.user_id, CONST.SHURIKEN_TYPE['FREE'])
			else:
				add_shuriken.delay(handshake.user_id, CONST.SHURIKEN_TYPE['REAL'])

			return arr, None

		return None, None

	elif event_name == '__uninit':
		print '__uninit'
		offchain = offchain.replace('m', '')
		handshake = Handshake.find_handshake_by_id(int(offchain))
		if handshake is not None:
			handshake.status = HandshakeStatus['STATUS_MAKER_UNINITED']
			handshake.bk_status = HandshakeStatus['STATUS_MAKER_UNINITED']

			db.session.flush()

			arr = []
			arr.append(handshake)
			return arr, None

	elif event_name == '__refund':
		print '__refund'
		if 's' in offchain:
			offchain = offchain.replace('s', '')
			shaker = Shaker.find_shaker_by_id(int(offchain))
			return save_refund_state_for_shaker(shaker)

		elif 'm' in offchain:
			offchain = offchain.replace('m', '')
			handshake = Handshake.find_handshake_by_id(int(offchain))
			return save_refund_state_for_maker(handshake)

		return None, None

	elif event_name == '__dispute':
		print '__dispute'
		shaker_dispute = []
		handshake_dispute = []
		if state < 2:
			return None, None
    	
		if 's' in offchain:
			offchain = offchain.replace('s', '')
			shaker = Shaker.find_shaker_by_id(int(offchain))
			if shaker is not None:
				shaker.bk_status = shaker.status
				shaker.status = HandshakeStatus['STATUS_USER_DISPUTED']
				db.session.flush()
				shaker_dispute.append(shaker)
				
		elif 'm' in offchain:
			offchain = offchain.replace('m', '')
			handshake = Handshake.find_handshake_by_id(int(offchain))
			if handshake is not None:
				handshake.bk_status = handshake.status
				handshake.status = HandshakeStatus['STATUS_USER_DISPUTED']
				db.session.flush()
				handshake_dispute.append(handshake)

		outcome_id = -1
		if len(handshake_dispute) != 0:
			outcome_id = handshake_dispute[0].outcome_id
		else:
			handshake = Handshake.find_handshake_by_id(shaker_dispute[0].handshake_id)
			if handshake is None:
				return None, None
			outcome_id = handshake.outcome_id

		outcome = Outcome.find_outcome_by_id(outcome_id)
		if outcome is None:
			return None, None

		if state == 3 and outcome.result != CONST.RESULT_TYPE['DISPUTED']:
			total_dispute_amount = db.engine.execute('SELECT SUM(amount) AS total FROM (SELECT * FROM handshake WHERE outcome_id = {} AND status = {}) as tmp'.format(outcome.id, HandshakeStatus['STATUS_USER_DISPUTED'])).scalar()
			if total_dispute_amount is not None:
				outcome.total_dispute_amount = total_dispute_amount
			outcome.result = CONST.RESULT_TYPE['DISPUTED']
			db.session.flush()

			handshake_dispute, shaker_dispute = save_dispute_state_all(outcome.id, HandshakeStatus['STATUS_DISPUTED'])

			# Send mail to admin
			send_mail.delay(outcome.id, outcome.name)
		return handshake_dispute, shaker_dispute

	elif event_name == '__resolve':
		result = offchain.replace('resolve', '')
		outcome = Outcome.find_outcome_by_hid(hid)
		if outcome is None:
			return None, None

		if len(result) == 0 or int(result) not in [1, 2, 3]:
			return None, None

		outcome.total_dispute_amount = 0
		outcome.result = int(result)
		db.session.flush()
		handshakes, shakers = save_dispute_state_all(outcome.id, HandshakeStatus['STATUS_RESOLVED'])
		return handshakes, shakers
		

def find_all_matched_handshakes(side, odds, outcome_id, amount):
	outcome = db.session.query(Outcome).filter(and_(Outcome.result==CONST.RESULT_TYPE['PENDING'], Outcome.id==outcome_id)).first()
	if outcome is not None:
		win_value = amount*odds
		if win_value - amount > 0:
			# calculate matched odds
			v = odds/(odds-1)
			v = float(Decimal(str(v)).quantize(Decimal('.1'), rounding=ROUND_HALF_DOWN))

			print 'matched odds --> {}'.format(v)
			query = text('''SELECT * FROM handshake where outcome_id = {} and odds <= {} and remaining_amount > 0 and status = {} and side != {} ORDER BY odds ASC;'''.format(outcome_id, v, CONST.Handshake['STATUS_INITED'], side))
			print query
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
		handshakes = db.session.query(Handshake).filter(and_(Handshake.side!=side, Handshake.outcome_id==outcome_id, Handshake.remaining_amount>0, Handshake.status==CONST.Handshake['STATUS_INITED'])).order_by(Handshake.odds.desc()).all()
		return handshakes
	return []

def find_available_support_handshakes(outcome_id):
	outcome = db.session.query(Outcome).filter(and_(Outcome.result==CONST.RESULT_TYPE['PENDING'], Outcome.id==outcome_id)).first()
	if outcome is not None:
		handshakes = db.session.query(Handshake.odds, func.sum(Handshake.remaining_amount).label('amount')).filter(and_(Handshake.side==CONST.SIDE_TYPE['SUPPORT'], Handshake.outcome_id==outcome_id, Handshake.remaining_amount>0, Handshake.status==CONST.Handshake['STATUS_INITED'])).group_by(Handshake.odds).order_by(Handshake.odds.desc()).all()
		return handshakes
	return []


def find_available_against_handshakes(outcome_id):
	outcome = db.session.query(Outcome).filter(and_(Outcome.result==CONST.RESULT_TYPE['PENDING'], Outcome.id==outcome_id)).first()
	if outcome is not None:
		handshakes = db.session.query(Handshake.odds, func.sum(Handshake.remaining_amount).label('amount')).filter(and_(Handshake.side==CONST.SIDE_TYPE['AGAINST'], Handshake.outcome_id==outcome_id, Handshake.remaining_amount>0, Handshake.status==CONST.Handshake['STATUS_INITED'])).group_by(Handshake.odds).order_by(Handshake.odds.desc()).all()
		return handshakes
	return []


def rollback_shake_state(shaker):
	if shaker is None:
		raise Exception(MESSAGE.SHAKER_NOT_FOUND)

	shaker.status = HandshakeStatus['STATUS_SHAKER_ROLLBACK']
	handshake = db.session.query(Handshake).filter(and_(Handshake.id==shaker.handshake_id, Handshake.status==HandshakeStatus['STATUS_INITED'])).first()
	if handshake is None:
		raise Exception(MESSAGE.HANDSHAKE_NOT_FOUND)

	handshake.remaining_amount += ((shaker.odds * shaker.amount) - shaker.amount)
	db.session.flush()

	return shaker


def is_init_pending_status(handshake):
	if handshake.status == HandshakeStatus['STATUS_PENDING'] and handshake.bk_status == HandshakeStatus['STATUS_PENDING']:
		return True	
	return False


def update_handshakes_feed(handshakes, shakers):
	# update feed
	if handshakes is not None:
		for handshake in handshakes:
			update_feed.delay(handshake.id)

	if shakers is not None:
		for shaker in shakers:
			update_feed.delay(shaker.handshake_id)


def can_withdraw(handshake, shaker=None):
	outcome = None
	result = None

	if shaker is None:
		if handshake is not None:
			if handshake.status == HandshakeStatus['STATUS_INITED']:
				outcome = Outcome.find_outcome_by_id(handshake.outcome_id)
				result = handshake.side
			else:
				return MESSAGE.CANNOT_WITHDRAW
		else:
			return MESSAGE.CANNOT_WITHDRAW
	else:
		if shaker.status == HandshakeStatus['STATUS_SHAKER_SHAKED']:
			handshake = Handshake.find_handshake_by_id(shaker.handshake_id)
			outcome = Outcome.find_outcome_by_id(handshake.outcome_id)	
			result = shaker.side
		else:
			return MESSAGE.CANNOT_WITHDRAW

	if outcome is not None:
		if outcome.result != result:
			return MESSAGE.HANDSHAKE_NOT_THE_SAME_RESULT

		if match_bl.is_exceed_dispute_time(outcome.match_id) == False:
			return MESSAGE.HANDSHAKE_WITHDRAW_AFTER_DISPUTE
	else:
		return MESSAGE.OUTCOME_INVALID

	return ''

def can_uninit(handshake):
	if handshake is None:
		return False
	
	n = time.mktime(datetime.now().timetuple())
	if len(handshake.shakers.all()) == 0:
		# avoid maker uninit too fast
		if handshake.free_bet == 1:
			ds = time.mktime(utc_to_local(handshake.date_created.timetuple()))
			if n - ds < 300.0: #5 minutes
				return False

	else:
		for sk in handshake.shakers.all():
			if sk.status == HandshakeStatus['STATUS_SHAKER_SHAKED']:
				return False
			else:
				ds = time.mktime(utc_to_local(sk.date_created.timetuple()))
				if n - ds < 300.0:
					return False

	return True
