#!/usr/bin/env python
#
# Copyright (C) 2017 Autonomous Inc. All rights reserved.
#

from sqlalchemy import func
from flask_testing import TestCase
from datetime import datetime, timedelta
from mock import patch
from tests.routes.base import BaseTestCase
from app import db, app
from app.models import User, Handshake, Outcome, Contract, Shaker, Redeem
from app.helpers.message import MESSAGE

import mock
import string
import random
import json
import time
import app.bl.user as user_bl

class TestUser(BaseTestCase):
		
	def clear_data_before_test(self):
		handshakes = db.session.query(Handshake).filter(
			Handshake.user_id == 88).all()

		shakers = db.session.query(Shaker).filter(
			Shaker.shaker_id == 88).all()

		redeems = db.session.query(Redeem).filter(
			Redeem.reserved_id == 88).all()

		for handshake in handshakes:
			db.session.delete(handshake)
			db.session.commit()

		for shaker in shakers:
			db.session.delete(shaker)
			db.session.commit()

		for r in redeems:
			r.reserved_id = 0
			r.used_user = 0
			db.session.commit()


	def test_is_able_to_claim_redeem_code(self):
		self.clear_data_before_test()

		user = User.find_user_with_id(88)
		actual = user_bl.is_able_to_claim_redeem_code(user)
		expected = True
		self.assertEqual(actual, expected)

		# claim redeem code for user 88
		redeems = db.session.query(Redeem).filter(Redeem.reserved_id==0).limit(2).all()
		for r in redeems:
			r.reserved_id = 88
			db.session.flush()
			db.session.commit()
		

		# recheck again
		actual = user_bl.is_able_to_claim_redeem_code(user)
		expected = False
		self.assertEqual(actual, expected)


	def test_is_able_to_use_redeem_code(self):
		self.clear_data_before_test()

		# claim redeem code for user 88
		redeems = db.session.query(Redeem).filter(Redeem.reserved_id==0).limit(2).all()
		for r in redeems:
			r.reserved_id = 88
			db.session.flush()
			db.session.commit()

		user = User.find_user_with_id(88)
		actual = user_bl.is_able_to_use_redeem_code(user)
		expected = True

		# user 88 use redeem code
		for r in redeems:
			r.used_user = 88
			db.session.flush()
			db.session.commit()

		actual = user_bl.is_able_to_use_redeem_code(user)
		expected = True

		# use producthunt code
		r = db.session.query(Redeem).filter(Redeem.reserved_id==88, Redeem.code==func.binary('DOJO')).first()
		if r is not None:
			r.used_user = 88
			db.session.flush()
			db.session.commit()

		actual = user_bl.is_able_to_use_redeem_code(user)
		expected = False

		self.assertEqual(actual, expected)


	def test_claim_redeem_code_for_user(self):
		self.clear_data_before_test()

		user = User.find_user_with_id(88)
		actual, _, _ = user_bl.claim_redeem_code_for_user(user)
		expected = True

		self.assertEqual(actual, expected)

		actual, _, _ = user_bl.claim_redeem_code_for_user(user)
		expected = False
		self.assertEqual(actual, expected)

if __name__ == '__main__':
	unittest.main()