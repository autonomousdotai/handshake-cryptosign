#!/usr/bin/env python
#
# Copyright (C) 2017 Autonomous Inc. All rights reserved.
#

from flask_testing import TestCase
from tests.routes.base import BaseTestCase
from app import db, app
from app.models import Redeem, Referral, User

import app.bl.referral as referral_bl
import mock

class TestReferralBl(BaseTestCase):

	def clear_data_before_test(self):
		r = Referral.find_referral_by_uid(88)
		if r is not None:
			db.session.delete(r)
			db.session.commit()
    	

	def test_issue_referral_code_for_user(self):
		self.clear_data_before_test()

		u = User.find_user_with_id(88)
		code1 = referral_bl.issue_referral_code_for_user(u)
		self.assertTrue(code1 is not None)
		db.session.commit()

		# issue again
		code2 = referral_bl.issue_referral_code_for_user(u)
		self.assertTrue(code1 == code2)
		db.session.commit()


if __name__ == '__main__':
	unittest.main()