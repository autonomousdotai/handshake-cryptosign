#!/usr/bin/env python
#
# Copyright (C) 2017 Autonomous Inc. All rights reserved.
#

from flask_testing import TestCase
from tests.routes.base import BaseTestCase
from mock import patch
from datetime import datetime
from app import db, app
from app.models import Handshake, User, Outcome, Match, Shaker

import app.bl.handshake as handshake_bl
import app.constants as CONST
import mock
import json


class TestHandshakeBl(BaseTestCase):

    def setUp(self):
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
                hid=88
            )
            db.session.add(outcome)
            db.session.commit()
        else:
            outcome.result = -1
            db.session.commit()

    def clear_data_before_test(self):
        handshakes = db.session.query(Handshake).filter(Handshake.outcome_id==88).all()
        for handshake in handshakes:
            db.session.delete(handshake)
            db.session.commit()

    def test_find_all_matched_handshakes_with_side_against(self):
        self.clear_data_before_test()
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
                status=0
        )
        db.session.add(handshake)
        db.session.commit()

        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=88,
				outcome_id=88,
				odds=1.1,
				amount=1,
				currency='ETH',
				side=1,
				remaining_amount=1,
				from_address='0x1234',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()
        
        handshakes = handshake_bl.find_all_matched_handshakes(side=2, odds=5.0, outcome_id=88, amount=0.25)

        self.assertEqual(len(handshakes), 2)
        self.assertEqual(float(handshakes[0].odds), 1.1)
        self.assertEqual(float(handshakes[1].odds), 1.2)
    

    def test_find_all_matched_handshakes_with_side_support(self):
        self.clear_data_before_test()
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
                status=0
        )
        db.session.add(handshake)
        db.session.commit()

        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=88,
				outcome_id=88,
				odds=1.4,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=1,
				from_address='0x1234',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()
        
        handshakes = handshake_bl.find_all_matched_handshakes(side=1, odds=5.0, outcome_id=88, amount=0.25)
        self.assertEqual(len(handshakes), 1)
        self.assertEqual(float(handshakes[0].odds), 1.2)
        

    def test_find_all_joined_handshakes_with_side_support(self):
        self.clear_data_before_test()
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
                status=0
        )
        db.session.add(handshake)
        db.session.commit()

        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=88,
				outcome_id=88,
				odds=1.1,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=1,
				from_address='0x1234',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()
        
        handshakes = handshake_bl.find_all_joined_handshakes(side=1, outcome_id=88)
        self.assertEqual(len(handshakes), 1)
        self.assertEqual(float(handshakes[0].odds), 1.1)

        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=88,
				outcome_id=88,
				odds=1.0,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=1,
				from_address='0x1234',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()


        handshakes = handshake_bl.find_all_joined_handshakes(side=1, outcome_id=88)
        self.assertEqual(len(handshakes), 2)
        self.assertEqual(float(handshakes[0].odds), 1.1)
        self.assertEqual(float(handshakes[1].odds), 1.0)
        

    def test_find_all_joined_handshakes_with_side_against(self):
        self.clear_data_before_test()
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
                status=0
        )
        db.session.add(handshake)
        db.session.commit()

        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=88,
				outcome_id=88,
				odds=1.1,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=1,
				from_address='0x1234',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()
        
        handshakes = handshake_bl.find_all_joined_handshakes(side=2, outcome_id=88)
        self.assertEqual(len(handshakes), 1)
        self.assertEqual(float(handshakes[0].odds), 1.2)


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
                status=0
        )
        db.session.add(handshake)
        db.session.commit()
        
        handshakes = handshake_bl.find_all_joined_handshakes(side=2, outcome_id=88)
        self.assertEqual(len(handshakes), 2)
        self.assertEqual(float(handshakes[0].odds), 1.2)
        self.assertEqual(float(handshakes[1].odds), 1.2)


    def test_find_available_support_handshakes(self):
        self.clear_data_before_test()
        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=88,
				outcome_id=88,
				odds=1.25,
				amount=1,
				currency='ETH',
				side=1,
				remaining_amount=0.25,
				from_address='0x123',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()

        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=99,
				outcome_id=88,
				odds=1.25,
				amount=0.25,
				currency='ETH',
				side=1,
				remaining_amount=0.0625,
				from_address='0x123',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()

        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=88,
				outcome_id=88,
				odds=1.10,
				amount=1,
				currency='ETH',
				side=1,
				remaining_amount=0.10,
				from_address='0x1234',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()

        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=88,
				outcome_id=88,
				odds=1.10,
				amount=0.1,
				currency='ETH',
				side=1,
				remaining_amount=0.01,
				from_address='0x1234',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()


        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=99,
				outcome_id=88,
				odds=1.10,
				amount=1,
				currency='ETH',
				side=1,
				remaining_amount=0.1,
				from_address='0x12345',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()

        handshakes = handshake_bl.find_available_support_handshakes(outcome_id=88)
        self.assertEqual(len(handshakes), 2)
        self.assertEqual(float(handshakes[0].amount), 0.3125)
        self.assertEqual(float(handshakes[1].amount), 0.21)

    def test_find_available_against_handshakes(self):
        self.clear_data_before_test()
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
				remaining_amount=0.25,
				from_address='0x123',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()

        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=99,
				outcome_id=88,
				odds=1.2,
				amount=0.25,
				currency='ETH',
				side=2,
				remaining_amount=0.0625,
				from_address='0x123',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()

        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=88,
				outcome_id=88,
				odds=1.1,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=0.10,
				from_address='0x1234',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()

        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=88,
				outcome_id=88,
				odds=1.1,
				amount=0.1,
				currency='ETH',
				side=2,
				remaining_amount=0.01,
				from_address='0x1234',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()


        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=99,
				outcome_id=88,
				odds=1.1,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=0.1,
				from_address='0x12345',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()

        handshakes = handshake_bl.find_available_against_handshakes(outcome_id=88)
        self.assertEqual(len(handshakes), 2)
        self.assertEqual(float(handshakes[0].amount), 0.3125)
        self.assertEqual(float(handshakes[1].amount), 0.21)


    def test_save_collect_state_for_shaker(self):
        self.clear_data_before_test()
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
				remaining_amount=0,
				from_address='0x123',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()

        # -----
        shaker = Shaker(
					shaker_id=66,
					amount=0.2,
					currency='ETH',
					odds=6,
					side=1,
					handshake_id=handshake.id,
					from_address='0x123',
					chain_id=4
				)
        db.session.add(shaker)
        db.session.commit()

        outcome = Outcome.find_outcome_by_id(88)
        outcome.result = 1
        db.session.flush()

        handshake_bl.save_collect_state_for_shaker(shaker)

        h = Handshake.find_handshake_by_id(handshake.id)
        s = Shaker.find_shaker_by_id(shaker.id)

        self.assertEqual(h.status, 6)
        self.assertEqual(s.status, 6)

    def test_save_collect_state_for_maker(self):
        pass

    def test_rollback_shake_state(self):
        self.clear_data_before_test()

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
				remaining_amount=0,
				from_address='0x123',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()

        # -----
        shaker = Shaker(
					shaker_id=88,
					amount=0.2,
					currency='ETH',
					odds=6,
					side=1,
					handshake_id=handshake.id,
					from_address='0x123',
					chain_id=4
				)
        db.session.add(shaker)
        db.session.commit()

        handshake_bl.rollback_shake_state(shaker)

        h = Handshake.find_handshake_by_id(handshake.id)
        s = Shaker.find_shaker_by_id(shaker.id)

        self.assertEqual(h.remaining_amount, 1)
        self.assertEqual(s.status, -9)


    def test_data_need_set_result_for_outcome(self):
        self.clear_data_before_test()

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
				remaining_amount=0,
				from_address='0x123',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()

        hs1 = handshake.id

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
				side=2,
				remaining_amount=0,
				from_address='0x123',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()

        hs2 = handshake.id

        # -----
        shaker = Shaker(
					shaker_id=88,
					amount=0.2,
					currency='ETH',
					odds=6,
					side=1,
					handshake_id=handshake.id,
					from_address='0x123',
					chain_id=4
				)
        db.session.add(shaker)
        db.session.commit()

        outcome = Outcome.find_outcome_by_id(88)
        outcome.result = 1
        db.session.flush()

        handshakes, shakers = handshake_bl.data_need_set_result_for_outcome(outcome)
        self.assertEqual(len(handshakes), 2)
        self.assertEqual(len(shakers), 1)

        h1 = handshakes[0]
        h2 = handshakes[1]
        s = shakers[0]

        self.assertEqual(h1.id, hs1)
        self.assertEqual(h2.id, hs2)
        self.assertEqual(s.id, shaker.id)


if __name__ == '__main__':
    unittest.main()