#!/usr/bin/env python
#
# Copyright (C) 2017 Autonomous Inc. All rights reserved.
#

from flask_testing import TestCase
from datetime import datetime, timedelta
from mock import patch
from tests.routes.base import BaseTestCase
from app import db, app
from app.models import User, Handshake, Outcome, Contract, Shaker
from app.helpers.message import MESSAGE

import mock
import json
import time
import app.bl.user as user_bl

class TestUser(BaseTestCase):

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

		# create user
		user = User.find_user_with_id(88)
		if user is None:
			user = User(
				id=88
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
			Handshake.user_id == 88).all()

		shakers = db.session.query(Shaker).filter(
			Shaker.shaker_id == 88).all()

		for handshake in handshakes:
			db.session.delete(handshake)
			db.session.commit()

		for shaker in shakers:
			db.session.delete(shaker)
			db.session.commit()
	
	def test_check_user_is_able_to_create_new_free_bet(self):
		self.clear_data_before_test()
		arr_hs = []

		can_free_bet, is_win, total_count_free_bet = user_bl.check_user_is_able_to_create_new_free_bet(88)
		self.assertEqual(can_free_bet, True)
		self.assertEqual(is_win, None)
		self.assertEqual(total_count_free_bet, 0)
		
		# -----
		handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=99,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=1,
				remaining_amount=1,
				from_address='0x123',
				status=0,
				free_bet=1,
		        date_created=datetime.now() + timedelta(seconds=1)
		)
		db.session.add(handshake)
		db.session.commit()
		arr_hs.append(handshake)

		# -----
		shaker = Shaker(
					shaker_id=88,
					amount=0.2,
					currency='ETH',
					odds=6,
					side=2,
					handshake_id=handshake.id,
					from_address='0x123',
					chain_id=4,
					status=2,
					free_bet=1,
		            date_created=datetime.now() + timedelta(seconds=10)
				)

		# -----
		handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=88,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=1,
				remaining_amount=1,
				from_address='0x123',
				status=0,
				free_bet=1,
		        date_created=datetime.now() + timedelta(seconds=20)
		)
		db.session.add(handshake)
		db.session.commit()
		arr_hs.append(handshake)

		db.session.add(shaker)
		db.session.commit()
		arr_hs.append(shaker)

		can_free_bet, is_win, total_count_free_bet = user_bl.check_user_is_able_to_create_new_free_bet(88)
		self.assertEqual(can_free_bet, False)
		self.assertEqual(is_win, False)
		self.assertEqual(total_count_free_bet, 2)

		o = Outcome.find_outcome_by_id(88)
		o.result = 1
		db.session.commit()

		can_free_bet, is_win, total_count_free_bet = user_bl.check_user_is_able_to_create_new_free_bet(88)
		self.assertEqual(can_free_bet, True)
		self.assertEqual(is_win, True)
		self.assertEqual(total_count_free_bet, 2)

		# -----
		handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=88,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=1,
				from_address='0x123',
				status=0,
				free_bet=1,
		        date_created=datetime.now() + timedelta(seconds=100)
		)
		db.session.add(handshake)
		db.session.commit()
		arr_hs.append(handshake)

		can_free_bet, is_win, total_count_free_bet = user_bl.check_user_is_able_to_create_new_free_bet(88)
		self.assertEqual(can_free_bet, False)
		self.assertEqual(is_win, False)
		self.assertEqual(total_count_free_bet, 3)

	def test_count_user_free_bet(self):
		pass

if __name__ == '__main__':
	unittest.main()