#!/usr/bin/env python
#
# Copyright (C) 2017 Autonomous Inc. All rights reserved.
#

from flask_testing import TestCase
from tests.routes.base import BaseTestCase
from mock import patch
from datetime import datetime
from app import db, app
from app.models import Handshake, User, Outcome, Match, Shaker, Contract
from app.tasks import send_email_result_notifcation
from app.helpers.message import MESSAGE
from app.constants import Handshake as HandshakeStatus
from app.helpers.utils import local_to_utc

import app.bl.handshake as handshake_bl
import app.constants as CONST
import mock
import json
import time


class TestHandshakeBl(BaseTestCase):

	def setUp(self):
    	# create contract
		contract = Contract.find_contract_by_id(1)
		if contract is None:
			contract = Contract(
				id=1,
				contract_name="contract1",
				contract_address="0x123",
				json_name="name1"
			)
			db.session.add(contract)
			db.session.commit()
		# create match
		match = Match.find_match_by_id(1)
		if match is None:
			match = Match(
				id=1
			)
			db.session.add(match)
			db.session.commit()

		# create user
		user = User.find_user_with_id(88)
		if user is None:
			user = User(
				id=88
			)
			db.session.add(user)
			db.session.commit()

		user = User.find_user_with_id(99)
		if user is None:
			user = User(
				id=99
			)
			db.session.add(user)
			db.session.commit()

		user = User.find_user_with_id(66)
		if user is None:
			user = User(
				id=66
			)
			db.session.add(user)
			db.session.commit()

		# create outcome
		outcome = Outcome.find_outcome_by_id(88)
		if outcome is None:
			outcome = Outcome(
				id=88,
				match_id=1,
				hid=88,
				contract_id=contract.id
			)
			db.session.add(outcome)
			db.session.commit()
		else:
			outcome.result = -1
			outcome.contract_id=contract.id
			db.session.commit()

	def clear_data_before_test(self):
		handshakes = db.session.query(Handshake).filter(
			Handshake.outcome_id == 88).all()
		for handshake in handshakes:
			db.session.delete(handshake)
			db.session.commit()

	def test_find_all_matched_handshakes_with_side_against(self):
		self.clear_data_before_test()
		# -----
		handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=88,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=1,
				remaining_amount=1,
				from_address='0x123',
				status=0
		)
		db.session.add(handshake)
		db.session.commit()

		# -----
		handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=88,
				outcome_id=88,
				odds=1.1,
				amount=1,
				currency='ETH',
				side=1,
				remaining_amount=1,
				from_address='0x1234',
				status=0
		)
		db.session.add(handshake)
		db.session.commit()

		handshakes = handshake_bl.find_all_matched_handshakes(
			side=2, odds=5.0, outcome_id=88, amount=0.25, maker=88)

		# cannot shake to myself
		self.assertEqual(len(handshakes), 0)

		# shake with another user
		handshakes = handshake_bl.find_all_matched_handshakes(
			side=2, odds=5.0, outcome_id=88, amount=0.25, maker=99)
		self.assertEqual(len(handshakes), 2)
		self.assertEqual(float(handshakes[0].odds), 1.1)
		self.assertEqual(float(handshakes[1].odds), 1.2)

	def test_find_all_matched_handshakes_with_side_support(self):
		self.clear_data_before_test()
		# -----
		handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=88,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=1,
				from_address='0x123',
				status=0
		)
		db.session.add(handshake)
		db.session.commit()

		# -----
		handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=88,
				outcome_id=88,
				odds=1.4,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=1,
				from_address='0x1234',
				status=0
		)
		db.session.add(handshake)
		db.session.commit()

		handshakes = handshake_bl.find_all_matched_handshakes(
			side=1, odds=5.0, outcome_id=88, amount=0.25, maker=88)

		# cannot shake to myself
		self.assertEqual(len(handshakes), 0)

		# shake again
		# -----
		handshakes = handshake_bl.find_all_matched_handshakes(
			side=1, odds=5.0, outcome_id=88, amount=0.25, maker=99)
		self.assertEqual(float(handshakes[0].odds), 1.2)

	def test_find_all_joined_handshakes_with_side_support(self):
		self.clear_data_before_test()
		# -----
		handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=88,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=1,
				remaining_amount=1,
				from_address='0x123',
				status=0
		)
		db.session.add(handshake)
		db.session.commit()

		# -----
		handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=88,
				outcome_id=88,
				odds=1.1,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=1,
				from_address='0x1234',
				status=0
		)
		db.session.add(handshake)
		db.session.commit()

		handshakes = handshake_bl.find_all_joined_handshakes(
			side=1, outcome_id=88)
		self.assertEqual(len(handshakes), 1)
		self.assertEqual(float(handshakes[0].odds), 1.1)

		# -----
		handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=88,
				outcome_id=88,
				odds=1.0,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=1,
				from_address='0x1234',
				status=0
		)
		db.session.add(handshake)
		db.session.commit()

		handshakes = handshake_bl.find_all_joined_handshakes(
			side=1, outcome_id=88)
		self.assertEqual(len(handshakes), 2)
		self.assertEqual(float(handshakes[0].odds), 1.1)
		self.assertEqual(float(handshakes[1].odds), 1.0)

	def test_data_need_set_result_for_outcome(self):
		self.clear_data_before_test()
		arr_hs = []
		
		outcome = Outcome.find_outcome_by_id(88)
		outcome.result = 1

		# -----
		handshake = Handshake(
						hs_type=3,
						chain_id=4,
						user_id=88,
						outcome_id=88,
						odds=1.5,
						amount=1,
						currency='ETH',
						side=2,
						remaining_amount=0,
						from_address='0x123',
						status=0
					)
		db.session.add(handshake)
		db.session.commit()
		arr_hs.append(handshake)
		
		shaker = Shaker(
					shaker_id=66,
					amount=0.2,
					currency='ETH',
					odds=6,
					side=1,
					handshake_id=handshake.id,
					from_address='0x123',
					chain_id=4,
					status=-1
				)
		db.session.add(shaker)
		db.session.commit()
		arr_hs.append(shaker)

		handshake_bl.data_need_set_result_for_outcome(outcome)

		hs = Handshake.find_handshake_by_id(handshake.id)
		self.assertEqual(hs.status, HandshakeStatus['STATUS_MAKER_SHOULD_UNINIT'])

		for item in arr_hs:
			db.session.delete(item)
			db.session.commit()

	def test_data_need_set_result_for_outcome_failed(self):
		self.clear_data_before_test()
		arr_hs = []
		
		outcome = Outcome.find_outcome_by_id(88)
		outcome.result = 1

		# -----
		handshake = Handshake(
						hs_type=3,
						chain_id=4,
						user_id=88,
						outcome_id=88,
						odds=1.5,
						amount=1,
						currency='ETH',
						side=2,
						remaining_amount=0,
						from_address='0x123',
						status=-1
					)
		db.session.add(handshake)
		db.session.commit()
		arr_hs.append(handshake)

		handshake_bl.data_need_set_result_for_outcome(outcome)
		hs = Handshake.find_handshake_by_id(handshake.id)
		self.assertEqual(hs.status, -1)

		hs.status = 0
		db.session.merge(hs)
		db.session.commit()

		handshake_bl.data_need_set_result_for_outcome(outcome)
		hs = Handshake.find_handshake_by_id(handshake.id)
		self.assertEqual(hs.status, HandshakeStatus['STATUS_MAKER_SHOULD_UNINIT'])

		for item in arr_hs:
			db.session.delete(item)
			db.session.commit()
	

	def test_find_all_joined_handshakes_with_side_against(self):
		self.clear_data_before_test()
		# -----
		handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=88,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=1,
				remaining_amount=1,
				from_address='0x123',
				status=0
		)
		db.session.add(handshake)
		db.session.commit()

		# -----
		handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=88,
				outcome_id=88,
				odds=1.1,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=1,
				from_address='0x1234',
				status=0
		)
		db.session.add(handshake)
		db.session.commit()

		handshakes = handshake_bl.find_all_joined_handshakes(
			side=2, outcome_id=88)
		self.assertEqual(len(handshakes), 1)
		self.assertEqual(float(handshakes[0].odds), 1.2)

		# -----
		handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=88,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=1,
				remaining_amount=1,
				from_address='0x123',
				status=0
		)
		db.session.add(handshake)
		db.session.commit()

		handshakes = handshake_bl.find_all_joined_handshakes(
			side=2, outcome_id=88)
		self.assertEqual(len(handshakes), 2)
		self.assertEqual(float(handshakes[0].odds), 1.2)
		self.assertEqual(float(handshakes[1].odds), 1.2)

	def test_find_available_support_handshakes(self):
		self.clear_data_before_test()
		# -----
		handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=88,
				outcome_id=88,
				odds=1.25,
				amount=1,
				currency='ETH',
				side=1,
				remaining_amount=0.25,
				from_address='0x123',
				status=0
		)
		db.session.add(handshake)
		db.session.commit()

		# -----
		handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=99,
				outcome_id=88,
				odds=1.25,
				amount=0.25,
				currency='ETH',
				side=1,
				remaining_amount=0.0625,
				from_address='0x123',
				status=0
		)
		db.session.add(handshake)
		db.session.commit()

		# -----
		handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=88,
				outcome_id=88,
				odds=1.10,
				amount=1,
				currency='ETH',
				side=1,
				remaining_amount=0.10,
				from_address='0x1234',
				status=0
		)
		db.session.add(handshake)
		db.session.commit()

		# -----
		handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=88,
				outcome_id=88,
				odds=1.10,
				amount=0.1,
				currency='ETH',
				side=1,
				remaining_amount=0.01,
				from_address='0x1234',
				status=0
		)
		db.session.add(handshake)
		db.session.commit()

		# -----
		handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=99,
				outcome_id=88,
				odds=1.10,
				amount=1,
				currency='ETH',
				side=1,
				remaining_amount=0.1,
				from_address='0x12345',
				status=0
		)
		db.session.add(handshake)
		db.session.commit()

		handshakes = handshake_bl.find_available_support_handshakes(
			outcome_id=88)
		self.assertEqual(len(handshakes), 2)
		self.assertEqual(float(handshakes[0].amount), 0.3125)
		self.assertEqual(float(handshakes[1].amount), 0.21)

	def test_find_available_against_handshakes(self):
		self.clear_data_before_test()
		# -----
		handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=88,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=0.25,
				from_address='0x123',
				status=0
		)
		db.session.add(handshake)
		db.session.commit()

		# -----
		handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=99,
				outcome_id=88,
				odds=1.2,
				amount=0.25,
				currency='ETH',
				side=2,
				remaining_amount=0.0625,
				from_address='0x123',
				status=0
		)
		db.session.add(handshake)
		db.session.commit()

		# -----
		handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=88,
				outcome_id=88,
				odds=1.1,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=0.10,
				from_address='0x1234',
				status=0
		)
		db.session.add(handshake)
		db.session.commit()

		# -----
		handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=88,
				outcome_id=88,
				odds=1.1,
				amount=0.1,
				currency='ETH',
				side=2,
				remaining_amount=0.01,
				from_address='0x1234',
				status=0
		)
		db.session.add(handshake)
		db.session.commit()

		# -----
		handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=99,
				outcome_id=88,
				odds=1.1,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=0.1,
				from_address='0x12345',
				status=0
		)
		db.session.add(handshake)
		db.session.commit()

		handshakes = handshake_bl.find_available_against_handshakes(
			outcome_id=88)
		self.assertEqual(len(handshakes), 2)
		self.assertEqual(float(handshakes[0].amount), 0.3125)
		self.assertEqual(float(handshakes[1].amount), 0.21)

	def test_save_collect_state_for_shaker(self):
		self.clear_data_before_test()
		# -----
		handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=88,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=0,
				from_address='0x123',
				status=0
		)
		db.session.add(handshake)
		db.session.commit()

		# -----
		shaker = Shaker(
					shaker_id=66,
					amount=0.2,
					currency='ETH',
					odds=6,
					side=1,
					handshake_id=handshake.id,
					from_address='0x123',
					chain_id=4,
					status=2
				)
		db.session.add(shaker)
		db.session.commit()

		outcome = Outcome.find_outcome_by_id(88)
		outcome.result = 1
		db.session.flush()

		handshake_bl.save_collect_state_for_shaker(shaker)
		db.session.commit()

		h = Handshake.find_handshake_by_id(handshake.id)
		s = Shaker.find_shaker_by_id(shaker.id)

		self.assertEqual(h.status, 6)
		self.assertEqual(s.status, 6)

	def test_is_init_pending_status(self):
		handshake = Handshake(
			hs_type=3,
			chain_id=4,
			user_id=99,
			outcome_id=88,
			odds=1.2,
			amount=1,
			currency='ETH',
			side=2,
			remaining_amount=0,
			from_address='0x123',
			status=0,
		)
		actual = handshake_bl.is_init_pending_status(handshake)
		expected = False
		self.assertEqual(actual, expected)

		handshake = Handshake(
			hs_type=3,
			chain_id=4,
			user_id=99,
			outcome_id=88,
			odds=1.2,
			amount=1,
			currency='ETH',
			side=2,
			remaining_amount=0,
			from_address='0x123',
			status=-1
		)

		actual = handshake_bl.is_init_pending_status(handshake)
		expected = False
		self.assertEqual(actual, expected)

		handshake = Handshake(
			hs_type=3,
			chain_id=4,
			user_id=99,
			outcome_id=88,
			odds=1.2,
			amount=1,
			currency='ETH',
			side=2,
			remaining_amount=0,
			from_address='0x123',
			status=-1,
			bk_status=-1
		)

		actual = handshake_bl.is_init_pending_status(handshake)
		expected = True
		self.assertEqual(actual, expected)

	def test_can_uninit(self):
		self.clear_data_before_test()
		# -----
		handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=88,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=0,
				from_address='0x123',
				status=0
		)
		db.session.add(handshake)
		db.session.commit()

		# not free-bet
		actual = handshake_bl.can_uninit(handshake)
		expected = True
		self.assertEqual(actual, expected)

		handshake.free_bet = 1
		db.session.merge(handshake)
		db.session.commit()

		# free-bet
		actual = handshake_bl.can_uninit(handshake)
		expected = False
		self.assertEqual(actual, expected)

		# -----
		shaker = Shaker(
					shaker_id=88,
					amount=0.2,
					currency='ETH',
					odds=6,
					side=1,
					handshake_id=handshake.id,
					from_address='0x123',
					chain_id=4,
					status=-1
				)
		db.session.add(shaker)
		db.session.commit()

		# free-bet with shaker status = -1
		actual = handshake_bl.can_uninit(handshake)
		expected = False
		self.assertEqual(actual, expected)

		# decrease date create of shaker
		shaker.date_created = datetime(2018, 6, 12)
		db.session.merge(shaker)
		db.session.flush()

		actual = handshake_bl.can_uninit(handshake)
		expected = True
		self.assertEqual(actual, expected)

		# set shaker status = 2
		shaker.status = 2
		db.session.merge(shaker)
		db.session.flush()

		actual = handshake_bl.can_uninit(handshake)
		expected = False
		self.assertEqual(actual, expected)

		handshake.free_bet = 0
		db.session.flush()

		actual = handshake_bl.can_uninit(handshake)
		expected = False
		self.assertEqual(actual, expected)

	def test_rollback_shake_state(self):
		self.clear_data_before_test()

		# -----
		handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=88,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=0,
				from_address='0x123',
				status=0
		)
		db.session.add(handshake)
		db.session.commit()

		# -----
		shaker = Shaker(
					shaker_id=88,
					amount=0.2,
					currency='ETH',
					odds=6,
					side=1,
					handshake_id=handshake.id,
					from_address='0x123',
					chain_id=4
				)
		db.session.add(shaker)
		db.session.commit()

		handshake_bl.rollback_shake_state(shaker)

		h = Handshake.find_handshake_by_id(handshake.id)
		s = Shaker.find_shaker_by_id(shaker.id)

		self.assertEqual(h.remaining_amount, 1)
		self.assertEqual(s.status, HandshakeStatus['STATUS_SHAKER_ROLLBACK'])

	def test_can_withdraw(self):
		self.clear_data_before_test()

		outcome = Outcome.find_outcome_by_id(88)
		outcome.result = 1

		match = Match.find_match_by_id(1)
		match.disputeTime = time.time() + 1000
		match.reportTime = time.time() + 1000
		db.session.commit()

		actual = handshake_bl.can_withdraw(None, shaker=None)
		self.assertNotEqual(len(actual), 0)

		# -----
		handshake = Handshake(
			hs_type=3,
			chain_id=4,
			user_id=88,
			outcome_id=1000,
			odds=1.2,
			amount=1,
			currency='ETH',
			side=2,
			remaining_amount=0,
			from_address='0x123',
			status=0
		)

		actual = handshake_bl.can_withdraw(handshake, shaker=None)
		self.assertEqual(actual, MESSAGE.OUTCOME_INVALID)

		# -----
		handshake = Handshake(
			hs_type=3,
			chain_id=4,
			user_id=88,
			outcome_id=88,
			odds=1.2,
			amount=1,
			currency='ETH',
			side=2,
			remaining_amount=0,
			from_address='0x123',
			status=0
		)

		actual = handshake_bl.can_withdraw(handshake, shaker=None)
		self.assertEqual(actual, MESSAGE.HANDSHAKE_NOT_THE_SAME_RESULT)

		# -----
		handshake = Handshake(
			hs_type=3,
			chain_id=4,
			user_id=88,
			outcome_id=88,
			odds=1.2,
			amount=1,
			currency='ETH',
			side=1,
			remaining_amount=0,
			from_address='0x123',
			status=0
		)

		actual = handshake_bl.can_withdraw(handshake, shaker=None)
		self.assertEqual(actual, MESSAGE.HANDSHAKE_WITHDRAW_AFTER_DISPUTE)

		match = Match.find_match_by_id(1)
		match.disputeTime = time.time() - 1000
		match.reportTime = time.time() - 1000
		db.session.commit()

		# -----
		handshake = Handshake(
			hs_type=3,
			chain_id=4,
			user_id=88,
			outcome_id=88,
			odds=1.2,
			amount=1,
			currency='ETH',
			side=1,
			remaining_amount=0,
			from_address='0x123',
			status=0
		)

		actual = handshake_bl.can_withdraw(handshake, shaker=None)
		self.assertEqual(actual, '')

	def test_has_valid_shaker(self):
		self.clear_data_before_test()
		arr_hs = []

		outcome = Outcome.find_outcome_by_id(88)
		outcome.result = 1

		# -----
		handshake = Handshake(
						hs_type=3,
						chain_id=4,
						user_id=88,
						outcome_id=88,
						odds=1.5,
						amount=1,
						currency='ETH',
						side=2,
						remaining_amount=0,
						from_address='0x123',
						status=0
					)
		db.session.add(handshake)
		db.session.commit()
		arr_hs.append(handshake)
		actual = handshake_bl.has_valid_shaker(handshake)
		expected = False
		self.assertEqual(actual, expected)

		shaker = Shaker(
					shaker_id=66,
					amount=0.2,
					currency='ETH',
					odds=6,
					side=1,
					handshake_id=handshake.id,
					from_address='0x123',
					chain_id=4,
					status=2
				)
		db.session.add(shaker)
		db.session.commit()
		arr_hs.append(shaker)

		actual = handshake_bl.has_valid_shaker(handshake)
		expected = True
		self.assertEqual(actual, expected)

		for item in arr_hs:
			db.session.delete(item)
			db.session.commit()

	def test_test_save_refund_state_for_all(self):
		self.clear_data_before_test()
		arr_hs = []
		arr_sk = []

		# -----
		handshake1 = Handshake(
						hs_type=3,
						chain_id=4,
						user_id=88,
						outcome_id=88,
						odds=1.5,
						amount=1,
						currency='ETH',
						side=2,
						remaining_amount=0,
						from_address='0x123',
						status=HandshakeStatus['STATUS_REFUND_PENDING']
					)
		db.session.add(handshake1)
		db.session.commit()
		arr_hs.append(handshake1)

		handshake2 = Handshake(
						hs_type=3,
						chain_id=4,
						user_id=88,
						outcome_id=88,
						odds=1.5,
						amount=1,
						currency='ETH',
						side=2,
						remaining_amount=0,
						from_address='0x123',
						status=HandshakeStatus['STATUS_MAKER_UNINITED']
					)
		db.session.add(handshake2)
		db.session.commit()
		arr_hs.append(handshake2)

		handshake3 = Handshake(
						hs_type=3,
						chain_id=4,
						user_id=99,
						outcome_id=88,
						odds=1.5,
						amount=1,
						currency='ETH',
						side=2,
						remaining_amount=0,
						from_address='0x123',
						status=HandshakeStatus['STATUS_INITED']
					)
		db.session.add(handshake3)
		db.session.commit()
		arr_hs.append(handshake3)

		# -----
		shaker1 = Shaker(
					shaker_id=88,
					amount=0.2,
					currency='ETH',
					odds=6,
					side=1,
					handshake_id=handshake1.id,
					from_address='0x123',
					chain_id=4,
					status=HandshakeStatus['STATUS_REFUND_PENDING']
				)
		db.session.add(shaker1)
		db.session.commit()
		arr_sk.append(shaker1)

		# -----
		shaker2 = Shaker(
					shaker_id=88,
					amount=0.2,
					currency='ETH',
					odds=6,
					side=1,
					handshake_id=handshake3.id,
					from_address='0x123',
					chain_id=4,
					status=HandshakeStatus['STATUS_REFUND_PENDING']
				)
		db.session.add(shaker2)
		db.session.commit()
		arr_sk.append(shaker2)

		handshakes, shakers = handshake_bl.save_refund_state_for_all(88, 88)
		actual = None

		hs1 = Handshake.find_handshake_by_id(handshake1.id)
		self.assertEqual(hs1.status, HandshakeStatus['STATUS_REFUNDED'])
		hs2 = Handshake.find_handshake_by_id(handshake2.id)
		self.assertEqual(hs2.status, HandshakeStatus['STATUS_MAKER_UNINITED'])
		hs3 = Handshake.find_handshake_by_id(handshake3.id)
		self.assertEqual(hs3.status, HandshakeStatus['STATUS_INITED'])

		sk1 = Shaker.find_shaker_by_id(shaker1.id)
		self.assertEqual(sk1.status, HandshakeStatus['STATUS_REFUNDED'])
		sk2 = Shaker.find_shaker_by_id(shaker2.id)
		self.assertEqual(sk2.status, HandshakeStatus['STATUS_REFUNDED'])

		for item in arr_hs:
			db.session.delete(item)
			db.session.commit()
		for item in arr_sk:
			db.session.delete(item)
			db.session.commit()

	def test_can_refund_for_maker(self):
		self.clear_data_before_test()

		t = datetime.now().timetuple()
		seconds = local_to_utc(t)

		match = Match.find_match_by_id(1)
		match.disputeTime = seconds + 1100
		match.reportTime = seconds + 1000
		db.session.merge(match)
		db.session.commit()

		arr_hs = []

		# -----
		handshake = Handshake(
						hs_type=3,
						chain_id=4,
						user_id=88,
						outcome_id=88,
						odds=1.5,
						amount=1,
						currency='ETH',
						side=2,
						remaining_amount=0,
						from_address='0x123',
						status=0
					)
		db.session.add(handshake)
		db.session.commit()
		arr_hs.append(handshake)

		actual = handshake_bl.can_refund(handshake)
		expected = False
		self.assertEqual(actual, expected)

		# test cannot refund
		outcome = Outcome.find_outcome_by_id(88)
		outcome.result = 1
		db.session.merge(outcome)
		db.session.flush()

		actual = handshake_bl.can_refund(handshake)
		expected = False
		self.assertEqual(actual, expected)

		# test refund if time exceed report time
		outcome.result = -1
		db.session.merge(outcome)
		db.session.flush()

		match.reportTime = seconds - 2000
		db.session.merge(match)
		db.session.commit()

		actual = handshake_bl.can_refund(handshake)
		expected = True
		self.assertEqual(actual, expected)

		for item in arr_hs:
			db.session.delete(item)
			db.session.commit()

	def test_can_refund_for_shaker(self):
		self.clear_data_before_test()

		match = Match.find_match_by_id(1)
		match.disputeTime = time.time() + 1000
		match.reportTime = time.time() + 1000
		db.session.merge(match)
		db.session.commit()

		arr_hs = []

		# -----
		handshake = Handshake(
						hs_type=3,
						chain_id=4,
						user_id=88,
						outcome_id=88,
						odds=1.5,
						amount=1,
						currency='ETH',
						side=2,
						remaining_amount=0,
						from_address='0x123',
						status=0
					)
		db.session.add(handshake)
		db.session.commit()
		arr_hs.append(handshake)

		# -----
		shaker = Shaker(
					shaker_id=66,
					amount=0.2,
					currency='ETH',
					odds=6,
					side=1,
					handshake_id=handshake.id,
					from_address='0x123',
					chain_id=4,
					status=2
				)
		db.session.add(shaker)
		db.session.commit()
		arr_hs.append(shaker)


		actual = handshake_bl.can_refund(None, shaker=shaker)
		expected = False
		self.assertEqual(actual, expected)

		outcome = Outcome.find_outcome_by_id(88)
		outcome.result = 3
		db.session.merge(outcome)
		db.session.flush()

		actual = handshake_bl.can_refund(None, shaker=shaker)
		expected = True
		self.assertEqual(actual, expected)


		for item in arr_hs:
			db.session.delete(item)
			db.session.commit()

	def test_verify_taker_odds(self):
		taker_odds = 1.6
		maker_odds = 2.7

		actual = handshake_bl.verify_taker_odds(taker_odds, maker_odds)
		expected = False
		self.assertEqual(actual, expected)

		taker_odds = 1.6
		maker_odds = 2.5
		
		actual = handshake_bl.verify_taker_odds(taker_odds, maker_odds)
		expected = True
		self.assertEqual(actual, expected)

		taker_odds = 1.1
		maker_odds = 11.1
		
		actual = handshake_bl.verify_taker_odds(taker_odds, maker_odds)
		expected = False
		self.assertEqual(actual, expected)


		taker_odds = 11.1
		maker_odds = 1.1
		
		actual = handshake_bl.verify_taker_odds(taker_odds, maker_odds)
		expected = False
		self.assertEqual(actual, expected)
		
	def test_send_email_result_notifcation(self):
		user = User(
			email="abc012@abc3456.com",
			payload="LDwp7UQoRNW5tUwzrA6q2trkwJLS3q6IHdOB0vt4T3dWV-a720yuWC1A9g==",
			is_subscribe=1
		)
		db.session.add(user)
		db.session.commit()

		match = Match(
			name="match test email"
		)
		db.session.add(match)
		db.session.commit()

		outcome = Outcome(
			match_id=match.id,
			name="Outcome Name",
			result=1,
			contract_id=1
		)
		db.session.add(outcome)
		db.session.commit()

		outcome_draw = Outcome(
			match_id=match.id,
			name="Outcome Draw",
			result=3,
			contract_id=1
		)
		db.session.add(outcome_draw)
		db.session.commit()

		handshake_win = Handshake(
						hs_type=3,
						chain_id=4,
						user_id=user.id,
						outcome_id=outcome.id,
						odds=1.5,
						amount=1,
						currency='ETH',
						side=outcome.result,
						remaining_amount=0,
						from_address='0x123',
						status=0
					)
		db.session.add(handshake_win)
		db.session.commit()

		handshake_draw = Handshake(
						hs_type=3,
						chain_id=4,
						user_id=user.id,
						outcome_id=outcome.id,
						odds=1.5,
						amount=1,
						currency='ETH',
						side=2,
						remaining_amount=0,
						from_address='0x123',
						status=0
					)
		db.session.add(handshake_draw)
		db.session.commit()

		handshake_draw = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=user.id,
				outcome_id=outcome_draw.id,
				odds=1.5,
				amount=1,
				currency='ETH',
				side=1,
				remaining_amount=0,
				from_address='0x123',
				status=0
			)
		db.session.add(handshake_draw)
		db.session.commit()

		# -----
		shaker_lose = Shaker(
			shaker_id=user.id,
			amount=0.2,
			currency='ETH',
			odds=6,
			side=2,
			handshake_id=handshake_win.id,
			from_address='0x123',
			chain_id=4,
			status=2
		)
		db.session.add(shaker_lose)
		db.session.commit()

		send_email_result_notifcation.delay(outcome_draw.id, outcome_draw.result, True)
		send_email_result_notifcation.delay(outcome.id, outcome.result, True)
		self.assertEqual(True, True)

if __name__ == '__main__':
	unittest.main()