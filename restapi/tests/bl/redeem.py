#!/usr/bin/env python
#
# Copyright (C) 2017 Autonomous Inc. All rights reserved.
#

from flask_testing import TestCase
from tests.routes.base import BaseTestCase
from app import db, app
from app.models import Redeem, Referral, User

import app.bl.redeem as redeem_bl
import mock

class TestRedeemBl(BaseTestCase):

	def clear_data_before_test(self):
		pass
    	

	def test_issue_new_redeem_code_for_user(self):
		self.clear_data_before_test()

		r = Redeem.find_redeem_by_user(88)
		before = len(r)

		redeem_bl.issue_new_redeem_code_for_user(88, is_need_send_mail=False)

		r = Redeem.find_redeem_by_user(88)
		after = len(r)

		self.assertNotEqual(before, after)


if __name__ == '__main__':
	unittest.main()