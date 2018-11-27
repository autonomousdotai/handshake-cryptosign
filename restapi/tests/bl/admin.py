#!/usr/bin/env python
#
# Copyright (C) 2017 Autonomous Inc. All rights reserved.
#

from flask_testing import TestCase
from tests.routes.base import BaseTestCase
from app import db, app
from app.models import Outcome, Match, Contract

import app.bl.admin as admin_bl

class TestAdminBaseTestCase(BaseTestCase):

	def clear_data_before_test(self):
		pass


	def test_can_admin_report_this_outcome(self):
		arr_outcomes = []
		match = Match.find_match_by_id(1)
		contract = Contract.find_contract_by_id(1)

		outcome = Outcome(
		)
		db.session.add(outcome)
		db.session.commit()
		arr_outcomes.append(outcome)

		actual = admin_bl.can_admin_report_this_outcome(outcome)
		expected = False
		self.assertEqual(actual, expected)

		# ------------		
		match.grant_permission = 0
		db.session.commit()

		outcome = Outcome(
			match_id=1,
			hid=0,
			created_user_id=88
		)
		db.session.add(outcome)
		db.session.commit()
		arr_outcomes.append(outcome)

		actual = admin_bl.can_admin_report_this_outcome(outcome)
		expected = False
		self.assertEqual(actual, expected)


		# ------------
		match.grant_permission = 1
		match.creator_wallet_address = None
		db.session.commit()

		outcome = Outcome(
			match_id=1,
			hid=0,
			result=-1,
			created_user_id=88
		)
		db.session.add(outcome)
		db.session.commit()
		arr_outcomes.append(outcome)

		actual = admin_bl.can_admin_report_this_outcome(outcome)
		expected = False
		self.assertEqual(actual, expected)


		# ------------
		match.grant_permission = 1
		match.creator_wallet_address = '0x123'

		contract.json_name = 'PredictionHandshake_v1_4'
		db.session.commit()

		outcome = Outcome(
			match_id=1,
			hid=0,
			result=-1,
			created_user_id=88,
			contract_id=contract.id
		)
		db.session.add(outcome)
		db.session.commit()
		arr_outcomes.append(outcome)

		actual = admin_bl.can_admin_report_this_outcome(outcome)
		expected = True
		self.assertEqual(actual, expected)

		for outcome in arr_outcomes:
			db.session.delete(outcome)
			db.session.commit()


	def test_is_contract_support_report_for_creator_method(self):
		name = 'PredictionHandshake_v1_4'

		actual = admin_bl.is_contract_support_report_for_creator_method(name)
		expected = True
		self.assertEqual(actual, expected)

		# ----------------
		name = 'PredictionHandshake_v1_3'

		actual = admin_bl.is_contract_support_report_for_creator_method(name)
		expected = False
		self.assertEqual(actual, expected)


		# ----------------
		name = ''

		actual = admin_bl.is_contract_support_report_for_creator_method(name)
		expected = False
		self.assertEqual(actual, expected)


if __name__ == '__main__':
	unittest.main()