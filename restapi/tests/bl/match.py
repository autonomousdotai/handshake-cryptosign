#!/usr/bin/env python
#
# Copyright (C) 2017 Autonomous Inc. All rights reserved.
#

from flask_testing import TestCase
from tests.routes.base import BaseTestCase
from mock import patch
from datetime import datetime
from app import db, app
from app.models import Handshake, User, Outcome, Match, Contract, Source
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
        expected = 'ninja'
        self.assertEqual(actual, expected)

        data = 'http://ninja.org'
        actual = match_bl.clean_source_with_valid_format(data)
        expected = 'ninja'
        self.assertEqual(actual, expected)

        data = 'www.ninja.org'
        actual = match_bl.clean_source_with_valid_format(data)
        expected = 'ninja'
        self.assertEqual(actual, expected)

        data = 'https://www.ninja.org'
        actual = match_bl.clean_source_with_valid_format(data)
        expected = 'ninja'
        self.assertEqual(actual, expected)

        data = 'http://www.ninja.org'
        actual = match_bl.clean_source_with_valid_format(data)
        expected = 'ninja'
        self.assertEqual(actual, expected)

        data = 'https://www.livescore.com/'
        actual = match_bl.clean_source_with_valid_format(data)
        expected = 'livescore'
        self.assertEqual(actual, expected)

        data = 'abc'
        actual = match_bl.clean_source_with_valid_format(data)
        expected = 'abc'
        self.assertEqual(actual, expected)

    def test_clean_source_with_valid_format(self):
        source1 = Source(
            name = "Source Test",
            url = "abc1.com",
            approved = 1
        )
        db.session.add(source1)

        source2 = Source(
            url = "http://www.abc2.com",
            approved = 1
        )
        db.session.add(source2)

        source3 = Source(
            name = "",
            url = "abc3.com",
            approved = 1
        )
        db.session.add(source3)
        db.session.commit()

        data1_json = match_bl.handle_source_data(Source.find_source_by_id(source1.id))
        data2_json = match_bl.handle_source_data(Source.find_source_by_id(source2.id))
        data3_json = match_bl.handle_source_data(Source.find_source_by_id(source3.id))

        self.assertEqual(data1_json["url_icon"], CONST.SOURCE_URL_ICON.format(match_bl.get_domain(source1.url)))

        self.assertEqual(data2_json["name"], 'www.abc2.com')

        self.assertEqual(data3_json["name"], 'abc3.com')

        db.session.delete(source1)
        db.session.delete(source2)
        db.session.delete(source3)
        db.session.commit()

    def get_text_list_need_approve(self):
        t = datetime.now().timetuple()
        seconds = local_to_utc(t)
        items = []
        match = Match(
            public=1,
            date=seconds - 100,
            reportTime=seconds + 200,
            disputeTime=seconds + 300,
            source_id = 3
        )
        db.session.add(match)
        db.session.commit()
        items.append(match)

        outcome = Outcome(
            match_id=match.id,
            name="test approve",
            approved=-1
        )
        db.session.add(outcome)
        items.append(outcome)
        db.session.commit()

        match1 = Match(
            public=0,
            date=seconds - 100,
            reportTime=seconds + 200,
            disputeTime=seconds + 300,
            source_id = 3
        )
        db.session.add(match1)
        db.session.commit()
        items.append(match1)

        outcome1 = Outcome(
            match_id=match1.id,
            name="test approve",
            approved=-1
        )
        db.session.add(outcome1)
        db.session.commit()
        items.append(outcome1)

        text = match_bl.get_text_list_need_approve()
        for item in items:
            db.session.delete(item)
            db.session.commit()
        
        self.assertTrue(text != '')

if __name__ == '__main__':
    unittest.main()