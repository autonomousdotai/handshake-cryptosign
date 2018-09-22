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


if __name__ == '__main__':
	unittest.main()