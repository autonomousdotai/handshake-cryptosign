#!/usr/bin/env python
#
# Copyright (C) 2017 Autonomous Inc. All rights reserved.
#

from flask_testing import TestCase
from tests.routes.base import BaseTestCase
from mock import patch
from datetime import datetime
from app import db, app
from app.models import Handshake, User, Outcome

import app.bl.handshake as handshake_bl
import app.constants as CONST
import mock
import json


class TestHandshakeBl(BaseTestCase):

    def setUp(self):
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

    def clear_data_before_test(self):
        handshakes = db.session.query(Handshake).filter(Handshake.outcome_id==88).all()
        for handshake in handshakes:
            db.session.delete(handshake)
            db.session.commit()

    def test_find_all_matched_handshakes_with_side_against(self):
        self.clear_data_before_test()

        arr_hs = []
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
				win_value=1.25,
				remaining_amount=1,
				from_address='0x123',
                status=0
        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        self.assertEqual(float(handshake.win_value), 1.25)
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
				win_value=1.10,
				remaining_amount=1,
				from_address='0x1234',
                status=0
        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        self.assertEqual(float(handshake.win_value), 1.10)
        
        handshakes = handshake_bl.find_all_matched_handshakes(side=2, odds=5.0, outcome_id=88, amount=0.25)

        self.assertEqual(len(handshakes), 2)
        self.assertEqual(float(handshakes[0].odds), 1.25)
        self.assertEqual(float(handshakes[1].odds), 1.1)
        
        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()

    def test_find_all_matched_handshakes_with_side_support(self):
        self.clear_data_before_test()

        arr_hs = []

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
				side=2,
				win_value=1.25,
				remaining_amount=1,
				from_address='0x123',
                status=0
        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        self.assertEqual(float(handshake.win_value), 1.25)
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
				side=2,
				win_value=1.10,
				remaining_amount=1,
				from_address='0x1234',
                status=0
        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        self.assertEqual(float(handshake.win_value), 1.1)
        
        handshakes = handshake_bl.find_all_matched_handshakes(side=1, odds=5.0, outcome_id=88, amount=0.25)
        self.assertEqual(len(handshakes), 1)
        self.assertEqual(float(handshakes[0].odds), 1.25)
        
        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()

    def test_find_all_joined_handshakes_with_side_support(self):
        self.clear_data_before_test()

        arr_hs = []

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
				win_value=1.25,
				remaining_amount=1,
				from_address='0x123',
                status=0
        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        self.assertEqual(float(handshake.win_value), 1.25)
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
				side=2,
				win_value=1.10,
				remaining_amount=1,
				from_address='0x1234',
                status=0
        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        self.assertEqual(float(handshake.win_value), 1.1)
        
        handshakes = handshake_bl.find_all_joined_handshakes(side=1, outcome_id=88)
        self.assertEqual(len(handshakes), 1)
        self.assertEqual(float(handshakes[0].odds), 1.10)

        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=88,
				outcome_id=88,
				odds=1.09,
				amount=1,
				currency='ETH',
				side=2,
				win_value=1.10,
				remaining_amount=1,
				from_address='0x1234',
                status=0
        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()


        handshakes = handshake_bl.find_all_joined_handshakes(side=1, outcome_id=88)
        self.assertEqual(len(handshakes), 2)
        self.assertEqual(float(handshakes[0].odds), 1.10)
        self.assertEqual(float(handshakes[1].odds), 1.09)
        
        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()

    def test_find_all_joined_handshakes_with_side_against(self):
        self.clear_data_before_test()

        arr_hs = []

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
				win_value=1.25,
				remaining_amount=1,
				from_address='0x123',
                status=0
        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        self.assertEqual(float(handshake.win_value), 1.25)
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
				side=2,
				win_value=1.10,
				remaining_amount=1,
				from_address='0x1234',
                status=0
        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        self.assertEqual(float(handshake.win_value), 1.1)
        
        handshakes = handshake_bl.find_all_joined_handshakes(side=2, outcome_id=88)
        self.assertEqual(len(handshakes), 1)
        self.assertEqual(float(handshakes[0].odds), 1.25)


        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=88,
				outcome_id=88,
				odds=1.24,
				amount=1,
				currency='ETH',
				side=1,
				win_value=1.24,
				remaining_amount=1,
				from_address='0x123',
                status=0
        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        self.assertEqual(float(handshake.win_value), 1.24)
        
        handshakes = handshake_bl.find_all_joined_handshakes(side=2, outcome_id=88)
        self.assertEqual(len(handshakes), 2)
        self.assertEqual(float(handshakes[0].odds), 1.25)
        self.assertEqual(float(handshakes[1].odds), 1.24)
        
        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()


    # def test_find_available_support_handshakes(self):
    #     self.clear_data_before_test()

    #     arr_hs = []

    #     # -----
    #     handshake = Handshake(
	# 			hs_type=3,
	# 			chain_id=4,
	# 			is_private=1,
	# 			user_id=88,
	# 			outcome_id=88,
	# 			odds=1.25,
	# 			amount=1,
	# 			currency='ETH',
	# 			side=1,
	# 			win_value=1.25,
	# 			remaining_amount=0.25,
	# 			from_address='0x123',
    #             status=0
    #     )
    #     arr_hs.append(handshake)
    #     db.session.add(handshake)
    #     db.session.commit()

    #     self.assertEqual(float(handshake.win_value), 1.25)

    #     # -----
    #     handshake = Handshake(
	# 			hs_type=3,
	# 			chain_id=4,
	# 			is_private=1,
	# 			user_id=99,
	# 			outcome_id=88,
	# 			odds=1.25,
	# 			amount=0.25,
	# 			currency='ETH',
	# 			side=1,
	# 			win_value=0.3125,
	# 			remaining_amount=0.0625,
	# 			from_address='0x123',
    #             status=0
    #     )
    #     arr_hs.append(handshake)
    #     db.session.add(handshake)
    #     db.session.commit()

    #     self.assertEqual(float(handshake.win_value), 0.3125)

    #     # -----
    #     handshake = Handshake(
	# 			hs_type=3,
	# 			chain_id=4,
	# 			is_private=1,
	# 			user_id=88,
	# 			outcome_id=88,
	# 			odds=1.10,
	# 			amount=1,
	# 			currency='ETH',
	# 			side=1,
	# 			win_value=1.10,
	# 			remaining_amount=0.10,
	# 			from_address='0x1234',
    #             status=0
    #     )
    #     arr_hs.append(handshake)
    #     db.session.add(handshake)
    #     db.session.commit()

    #     self.assertEqual(float(handshake.win_value), 1.10)

    #     # -----
    #     handshake = Handshake(
	# 			hs_type=3,
	# 			chain_id=4,
	# 			is_private=1,
	# 			user_id=88,
	# 			outcome_id=88,
	# 			odds=1.10,
	# 			amount=0.1,
	# 			currency='ETH',
	# 			side=1,
	# 			win_value=0.11,
	# 			remaining_amount=0.01,
	# 			from_address='0x1234',
    #             status=0
    #     )
    #     arr_hs.append(handshake)
    #     db.session.add(handshake)
    #     db.session.commit()


    #     # -----
    #     handshake = Handshake(
	# 			hs_type=3,
	# 			chain_id=4,
	# 			is_private=1,
	# 			user_id=99,
	# 			outcome_id=88,
	# 			odds=1.10,
	# 			amount=1,
	# 			currency='ETH',
	# 			side=1,
	# 			win_value=1.11,
	# 			remaining_amount=0.1,
	# 			from_address='0x12345',
    #             status=0
    #     )
    #     arr_hs.append(handshake)
    #     db.session.add(handshake)
    #     db.session.commit()

    #     self.assertEqual(float(handshake.win_value), 1.11)

    #     handshakes = handshake_bl.find_available_support_handshakes(outcome_id=88)
    #     self.assertEqual(len(handshakes), 2)
    #     self.assertEqual(float(handshakes[0].amount), 2.10)
    #     self.assertEqual(float(handshakes[1].amount), 1.25)


    #     for handshake in arr_hs:
    #         db.session.delete(handshake)
    #         db.session.commit()

    # def test_find_available_against_handshakes(self):
    #     self.clear_data_before_test()

    #     arr_hs = []

    #     # -----
    #     handshake = Handshake(
	# 			hs_type=3,
	# 			chain_id=4,
	# 			is_private=1,
	# 			user_id=88,
	# 			outcome_id=88,
	# 			odds=1.25,
	# 			amount=1,
	# 			currency='ETH',
	# 			side=2,
	# 			win_value=1.25,
	# 			remaining_amount=0.25,
	# 			from_address='0x123',
    #             status=0
    #     )
    #     arr_hs.append(handshake)
    #     db.session.add(handshake)
    #     db.session.commit()

    #     self.assertEqual(float(handshake.win_value), 1.25)

    #     # -----
    #     handshake = Handshake(
	# 			hs_type=3,
	# 			chain_id=4,
	# 			is_private=1,
	# 			user_id=99,
	# 			outcome_id=88,
	# 			odds=1.25,
	# 			amount=0.25,
	# 			currency='ETH',
	# 			side=2,
	# 			win_value=0.3125,
	# 			remaining_amount=0.0625,
	# 			from_address='0x123',
    #             status=0
    #     )
    #     arr_hs.append(handshake)
    #     db.session.add(handshake)
    #     db.session.commit()

    #     self.assertEqual(float(handshake.win_value), 0.3125)

    #     # -----
    #     handshake = Handshake(
	# 			hs_type=3,
	# 			chain_id=4,
	# 			is_private=1,
	# 			user_id=88,
	# 			outcome_id=88,
	# 			odds=1.10,
	# 			amount=1,
	# 			currency='ETH',
	# 			side=2,
	# 			win_value=1.10,
	# 			remaining_amount=0.10,
	# 			from_address='0x1234',
    #             status=0
    #     )
    #     arr_hs.append(handshake)
    #     db.session.add(handshake)
    #     db.session.commit()

    #     self.assertEqual(float(handshake.win_value), 1.10)

    #     # -----
    #     handshake = Handshake(
	# 			hs_type=3,
	# 			chain_id=4,
	# 			is_private=1,
	# 			user_id=88,
	# 			outcome_id=88,
	# 			odds=1.10,
	# 			amount=0.1,
	# 			currency='ETH',
	# 			side=2,
	# 			win_value=0.11,
	# 			remaining_amount=0.01,
	# 			from_address='0x1234',
    #             status=0
    #     )
    #     arr_hs.append(handshake)
    #     db.session.add(handshake)
    #     db.session.commit()


    #     # -----
    #     handshake = Handshake(
	# 			hs_type=3,
	# 			chain_id=4,
	# 			is_private=1,
	# 			user_id=99,
	# 			outcome_id=88,
	# 			odds=1.10,
	# 			amount=1,
	# 			currency='ETH',
	# 			side=2,
	# 			win_value=1.11,
	# 			remaining_amount=0.1,
	# 			from_address='0x12345',
    #             status=0
    #     )
    #     arr_hs.append(handshake)
    #     db.session.add(handshake)
    #     db.session.commit()

    #     self.assertEqual(float(handshake.win_value), 1.11)

    #     handshakes = handshake_bl.find_available_against_handshakes(outcome_id=88)
    #     self.assertEqual(len(handshakes), 2)
    #     self.assertEqual(float(handshakes[0].amount), 1.25)
    #     self.assertEqual(float(handshakes[1].amount), 2.10)


    #     for handshake in arr_hs:
    #         db.session.delete(handshake)
    #         db.session.commit()

if __name__ == '__main__':
    unittest.main()