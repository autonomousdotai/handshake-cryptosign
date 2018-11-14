#!/usr/bin/env python
#
# Copyright (C) 2017 Autonomous Inc. All rights reserved.
#

from flask_testing import TestCase
from tests.routes.base import BaseTestCase
from app import db, app
from app.models import Outcome, Match

import app.bl.admin as admin_bl

class TestAdminBaseTestCase(BaseTestCase):

	def setUp(self):
		match = Match.find_match_by_id(1)
		if match is None:
			match = Match(
				id=1,
				name='test1-2-3'
			)
			db.session.add(match)
			db.session.commit()


	def clear_data_before_test(self):
		pass


	def test_can_admin_report_this_outcome(self):
		arr_outcomes = []
		match = Match.find_match_by_id(1)

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
		expected = True
		self.assertEqual(actual, expected)

		for outcome in arr_outcomes:
			db.session.delete(outcome)
			db.session.commit()


if __name__ == '__main__':
	unittest.main()