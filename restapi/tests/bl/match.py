#!/usr/bin/env python
#
# Copyright (C) 2017 Autonomous Inc. All rights reserved.
#

from flask_testing import TestCase
from tests.routes.base import BaseTestCase
from mock import patch
from datetime import datetime
from app import db, app
from app.models import Handshake, User, Outcome, Match, Contract
from app.helpers.utils import local_to_utc

import app.bl.match as match_bl
import app.constants as CONST
import mock
import json


class TestMatchBl(BaseTestCase):

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
            outcome.contract_id=contract.id



    def clear_data_before_test(self):
        handshakes = db.session.query(Handshake).filter(Handshake.outcome_id==88).all()
        for handshake in handshakes:
            db.session.delete(handshake)
            db.session.commit()

    def test_find_best_odds_which_match_support_side(self):
        self.clear_data_before_test()

        arr_hs = []
        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=88,
				outcome_id=88,
				odds=1.25,
				amount=1,
				currency='ETH',
				side=2,
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
				outcome_id=88,
				odds=1.10,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=1,
				from_address='0x1234',
                status=0
        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()


        expected_odds = 11
        expected_amount = handshake.amount * (handshake.odds - 1)
        actual_odds, actual_amount = match_bl.find_best_odds_which_match_support_side(88)
        self.assertEqual(expected_odds, actual_odds)
        
    def test_is_validate_match_time(self):

        t = datetime.now().timetuple()
    	seconds = local_to_utc(t)

        data = {
            "date": seconds,
            "reportTime": seconds + 1000,
            "disputeTime": seconds + 2000 
        }

        expected = False
        actual = match_bl.is_validate_match_time(data)
        self.assertEqual(actual, expected)

        # -------
        data = {
            "date": seconds + 1000,
            "reportTime": seconds + 1000,
            "disputeTime": seconds + 2000 
        }

        expected = False
        actual = match_bl.is_validate_match_time(data)
        self.assertEqual(actual, expected)

        # -------
        data = {
            "date": seconds + 1000,
            "reportTime": seconds + 2000,
            "disputeTime": seconds + 3000 
        }

        expected = True
        actual = match_bl.is_validate_match_time(data)
        self.assertEqual(actual, expected)


    def test_clean_source_with_valid_format(self):
        data = 'https://ninja.org'
        actual = match_bl.clean_source_with_valid_format(data)
        expected = 'ninja.org'
        self.assertEqual(actual, expected)

        data = 'http://ninja.org'
        actual = match_bl.clean_source_with_valid_format(data)
        expected = 'ninja.org'
        self.assertEqual(actual, expected)

        data = 'www.ninja.org'
        actual = match_bl.clean_source_with_valid_format(data)
        expected = 'www.ninja.org'
        self.assertEqual(actual, expected)

        data = 'https://www.ninja.org'
        actual = match_bl.clean_source_with_valid_format(data)
        expected = 'ninja.org'
        self.assertEqual(actual, expected)

        data = 'http://www.ninja.org'
        actual = match_bl.clean_source_with_valid_format(data)
        expected = 'ninja.org'
        self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()