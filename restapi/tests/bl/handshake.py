#!/usr/bin/env python
#
# Copyright (C) 2017 Autonomous Inc. All rights reserved.
#

from flask_testing import TestCase
from tests.routes.base import BaseTestCase
from mock import patch
from datetime import datetime
from app import db, app
from app.models import Handshake, User

import app.bl.handshake as handshake_bl
import app.constants as CONST
import mock
import json


class TestHandshakeBl(BaseTestCase):

    def test_find_all_matched_handshakes_with_side_against(self):
        arr_hs = []
        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=49,
				outcome_id=4,
				odds=1.25,
				amount=1,
				currency='ETH',
				side=1,
				win_value=1.25,
				remaining_amount=0.25,
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
				user_id=49,
				outcome_id=4,
				odds=1.10,
				amount=1,
				currency='ETH',
				side=1,
				win_value=1.10,
				remaining_amount=0.10,
				from_address='0x1234',
                status=0
        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        self.assertEqual(float(handshake.win_value), 1.1)
        
        handshakes = handshake_bl.find_all_matched_handshakes(side=2, odds=5.0, outcome_id=4, amount=0.25)
        self.assertEqual(len(handshakes), 2)
        self.assertEqual(float(handshakes[0].odds), 1.10)
        self.assertEqual(float(handshakes[1].odds), 1.25)
        
        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()

    def test_find_all_matched_handshakes_with_side_support(self):
        arr_hs = []

        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=49,
				outcome_id=4,
				odds=1.25,
				amount=1,
				currency='ETH',
				side=2,
				win_value=1.25,
				remaining_amount=0.25,
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
				user_id=49,
				outcome_id=4,
				odds=1.10,
				amount=1,
				currency='ETH',
				side=2,
				win_value=1.10,
				remaining_amount=0.10,
				from_address='0x1234',
                status=0
        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        self.assertEqual(float(handshake.win_value), 1.1)
        
        handshakes = handshake_bl.find_all_matched_handshakes(side=1, odds=5.0, outcome_id=4, amount=0.25)
        self.assertEqual(len(handshakes), 2)
        self.assertEqual(float(handshakes[0].odds), 1.10)
        self.assertEqual(float(handshakes[1].odds), 1.25)
        
        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()

    def test_find_all_joined_handshakes_with_side_support(self):
        arr_hs = []

        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=49,
				outcome_id=4,
				odds=1.25,
				amount=1,
				currency='ETH',
				side=1,
				win_value=1.25,
				remaining_amount=0.25,
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
				user_id=49,
				outcome_id=4,
				odds=1.10,
				amount=1,
				currency='ETH',
				side=2,
				win_value=1.10,
				remaining_amount=0.10,
				from_address='0x1234',
                status=0
        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        self.assertEqual(float(handshake.win_value), 1.1)
        
        handshakes = handshake_bl.find_all_joined_handshakes(side=1, outcome_id=4)
        self.assertEqual(len(handshakes), 1)
        self.assertEqual(float(handshakes[0].odds), 1.10)
        
        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()

    def test_find_all_joined_handshakes_with_side_against(self):
        arr_hs = []

        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=49,
				outcome_id=4,
				odds=1.25,
				amount=1,
				currency='ETH',
				side=1,
				win_value=1.25,
				remaining_amount=0.25,
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
				user_id=49,
				outcome_id=4,
				odds=1.10,
				amount=1,
				currency='ETH',
				side=2,
				win_value=1.10,
				remaining_amount=0.10,
				from_address='0x1234',
                status=0
        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        self.assertEqual(float(handshake.win_value), 1.1)
        
        handshakes = handshake_bl.find_all_joined_handshakes(side=2, outcome_id=4)
        self.assertEqual(len(handshakes), 1)
        self.assertEqual(float(handshakes[0].odds), 1.25)
        
        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()


    def test_find_available_support_handshakes(self):
        pass

    def test_find_available_against_handshakes(self):
        pass

if __name__ == '__main__':
    unittest.main()