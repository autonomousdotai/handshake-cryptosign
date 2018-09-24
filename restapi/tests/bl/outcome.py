#!/usr/bin/env python
#
# Copyright (C) 2017 Autonomous Inc. All rights reserved.
#

from flask_testing import TestCase
from tests.routes.base import BaseTestCase
from mock import patch
from datetime import datetime
from app import db, app
from app.models import Handshake, User, Outcome, Match, Contract, Shaker
from app.helpers.utils import local_to_utc

import app.bl.outcome as outcome_bl
import app.constants as CONST
import mock
import json


class TestOutcomeBl(BaseTestCase):

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
		user = User.find_user_with_id(109)
		if user is None:
			user = User(
				id=109
			)
			db.session.add(user)
			db.session.commit()

		# create match
		match = Match.find_match_by_id(1)
		if match is None:
			match = Match(
				id=1
			)
			db.session.add(match)
			db.session.commit()

		# create outcome
		outcome = Outcome.find_outcome_by_id(109)
		if outcome is None:
			outcome = Outcome(
				id=109,
				match_id=match.id,
				hid=109,
				contract_id=contract.id
			)
			db.session.add(outcome)
			db.session.commit()
		else:
			outcome.result = -1
			outcome.contract_id=contract.id
			db.session.commit()

	def clear_data_before_test(self):
		handshakes = db.session.query(Handshake).filter(Handshake.outcome_id==109).all()
		for handshake in handshakes:
			db.session.delete(handshake)
			db.session.commit()

	def test_count_users_play_on_outcome(self):
		self.clear_data_before_test()

		arr_hs = []
		# -----
		handshake = Handshake(
			hs_type=3,
			chain_id=4,
			user_id=109,
			outcome_id=109,
			odds=1.2,
			amount=1,
			currency='ETH',
			side=1,
			remaining_amount=1,
			from_address='0x123',
			status=0
		)
		arr_hs.append(handshake)
		db.session.add(handshake)
		db.session.commit()


		# -----
		handshake = Handshake(
			hs_type=3,
			chain_id=4,
			user_id=88,
			outcome_id=109,
			odds=1.2,
			amount=1,
			currency='ETH',
			side=1,
			remaining_amount=1,
			from_address='0x123',
			status=-1
		)
		arr_hs.append(handshake)
		db.session.add(handshake)
		db.session.commit()


		# -----
		shaker = Shaker(
			shaker_id=88,
			handshake_id=handshake.id,
			status=2,
			side=2
		)
		arr_hs.append(shaker)
		db.session.add(shaker)
		db.session.commit()


		# -----
		shaker = Shaker(
			shaker_id=109,
			handshake_id=handshake.id,
			status=2,
			side=2
		)
		arr_hs.append(shaker)
		db.session.add(shaker)
		db.session.commit()


		actual = outcome_bl.count_users_play_on_outcome(109)
		expected = 2
		self.assertEqual(actual, expected)

		for handshake in arr_hs:
			db.session.delete(handshake)
			db.session.commit()


	def test_count_support_users_play_on_outcome(self):
		self.clear_data_before_test()

		arr_hs = []
		# -----
		handshake = Handshake(
			hs_type=3,
			chain_id=4,
			user_id=109,
			outcome_id=109,
			odds=1.2,
			amount=1,
			currency='ETH',
			side=1,
			remaining_amount=1,
			from_address='0x123',
			status=0
		)
		arr_hs.append(handshake)
		db.session.add(handshake)
		db.session.commit()


		# -----
		handshake = Handshake(
			hs_type=3,
			chain_id=4,
			user_id=88,
			outcome_id=109,
			odds=1.2,
			amount=1,
			currency='ETH',
			side=1,
			remaining_amount=1,
			from_address='0x123',
			status=-1
		)
		arr_hs.append(handshake)
		db.session.add(handshake)
		db.session.commit()


		# -----
		shaker = Shaker(
			shaker_id=88,
			handshake_id=handshake.id,
			status=2,
			side=2
		)
		arr_hs.append(shaker)
		db.session.add(shaker)
		db.session.commit()


		# -----
		shaker = Shaker(
			shaker_id=109,
			handshake_id=handshake.id,
			status=2,
			side=2
		)
		arr_hs.append(shaker)
		db.session.add(shaker)
		db.session.commit()


		actual = outcome_bl.count_support_users_play_on_outcome(109)
		expected = 1
		self.assertEqual(actual, expected)

		for handshake in arr_hs:
			db.session.delete(handshake)
			db.session.commit()


	def test_count_against_users_play_on_outcome(self):
		self.clear_data_before_test()

		arr_hs = []
		# -----
		handshake = Handshake(
			hs_type=3,
			chain_id=4,
			user_id=109,
			outcome_id=109,
			odds=1.2,
			amount=1,
			currency='ETH',
			side=1,
			remaining_amount=1,
			from_address='0x123',
			status=0
		)
		arr_hs.append(handshake)
		db.session.add(handshake)
		db.session.commit()


		# -----
		handshake = Handshake(
			hs_type=3,
			chain_id=4,
			user_id=88,
			outcome_id=109,
			odds=1.2,
			amount=1,
			currency='ETH',
			side=1,
			remaining_amount=1,
			from_address='0x123',
			status=-1
		)
		arr_hs.append(handshake)
		db.session.add(handshake)
		db.session.commit()


		# -----
		shaker = Shaker(
			shaker_id=88,
			handshake_id=handshake.id,
			status=2,
			side=2
		)
		arr_hs.append(shaker)
		db.session.add(shaker)
		db.session.commit()


		# -----
		shaker = Shaker(
			shaker_id=109,
			handshake_id=handshake.id,
			status=2,
			side=2
		)
		arr_hs.append(shaker)
		db.session.add(shaker)
		db.session.commit()

		actual = outcome_bl.count_against_users_play_on_outcome(109)
		expected = 2
		self.assertEqual(actual, expected)

		for handshake in arr_hs:
			db.session.delete(handshake)
			db.session.commit()

	def test_has_result_outcome(self):
		self.clear_data_before_test()

		o = Outcome()
		db.session.add(o)
		db.session.commit()

		actual = outcome_bl.has_result(o)
		expected = False
		self.assertEqual(actual, expected)

		o.result = 4
		db.session.merge(o)
		db.session.commit()

		actual = outcome_bl.has_result(o)
		expected = False
		self.assertEqual(actual, expected)


		o.result = 1
		db.session.merge(o)
		db.session.commit()
		
		actual = outcome_bl.has_result(o)
		expected = True
		self.assertEqual(actual, expected)


if __name__ == '__main__':
	unittest.main()