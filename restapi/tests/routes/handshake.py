#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from tests.routes.base import BaseTestCase
from mock import patch
from app import db, app
from app.models import Handshake, User, Outcome
from app.helpers.message import MESSAGE
from io import BytesIO

import os
import mock
import json
import time
import app.bl.handshake as handshake_bl

class TestHandshakeBluePrint(BaseTestCase):   

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


        user = User.find_user_with_id(109)
        if user is None:
            user = User(
                id=109
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

    def test_list_of_handshakes(self):
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

        with self.client:
            Uid = 66
            
            params = {
                "outcome_id": 88
            }
            response = self.client.post(
                                    '/handshake',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            data_json = data['data']
            self.assertTrue(data['status'] == 1)
            self.assertEqual(len(data_json['support']), 1)

            self.assertEqual(data_json['support'][0]['odds'], '1.25')
            self.assertEqual(response.status_code, 200)

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()

    def test_init_handshake_case_1(self):
        # Support
        #   amount          odds
        #   1               3
        # Shake with 1.25 ETH, odds: 1.5
        # Expected: 
        #   Maker:  
        #          remaining_amount = 0
        #          list handshake is now empty
        #  Shaker:
        #          match with handshake

        self.clear_data_before_test()
        arr_hs = []
        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=88,
				outcome_id=88,
				odds=3,
				amount=1,
				currency='ETH',
				side=1,
				win_value=3,
				remaining_amount=1,
				from_address='0x123',
                status=0
        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        with self.client:
            Uid = 66

            params = {
                "type": 3,
                "extra_data": "",
                "description": "TESTING MODE",
                "outcome_id": 88,
                "odds": 1.5,
                "amount": 1.25,
                "currency": "ETH",
                "chain_id": 4,
                "side": 2,
                "from_address": "0x4f94a1392A6B48dda8F41347B15AF7B80f3c5f03"
            }
            response = self.client.post(
                                    '/handshake/init',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()

    def test_init_handshake_case_2(self):
        self.clear_data_before_test()

        # Support
        #   amount          odds
        #   0.2               3
        #   0.1               2.9
        #   0.3               2.8
        # Shake with 1.25 ETH, odds: 1.6
        # Expected: 
        #   Maker:  
        #          remaining_amount = 0
        #          list handshake is now empty
        #  Shaker:
        #          match 3 handshakes
        #          create 1 handshakes

        self.clear_data_before_test()
        arr_hs = []
        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=88,
				outcome_id=88,
				odds=3,
				amount=0.2,
				currency='ETH',
				side=1,
				win_value=0.6,
				remaining_amount=0.2,
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
				is_private=1,
				user_id=99,
				outcome_id=88,
				odds=2.9,
				amount=0.1,
				currency='ETH',
				side=1,
				win_value=0.29,
				remaining_amount=0.1,
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
				is_private=1,
				user_id=109,
				outcome_id=88,
				odds=2.8,
				amount=0.3,
				currency='ETH',
				side=1,
				win_value=0.84,
				remaining_amount=0.3,
				from_address='0x123',
                status=0
        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        with self.client:
            Uid = 66

            params = {
                "type": 3,
                "extra_data": "",
                "description": "TESTING MODE",
                "outcome_id": 88,
                "odds": 1.6,
                "amount": 1.25,
                "currency": "ETH",
                "chain_id": 4,
                "side": 2,
                "from_address": "0x4f94a1392A6B48dda8F41347B15AF7B80f3c5f03"
            }
            response = self.client.post(
                                    '/handshake/init',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            data_json = data['data']
            self.assertTrue(data['status'] == 1)
            self.assertEqual(len(data_json), 4)
            self.assertEqual(response.status_code, 200)

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()


    def test_init_handshake_case_3(self):
        self.clear_data_before_test()

        # Against
        #   amount          odds
        #   0.2               1.5
        #   0.1               1.4
        #   0.3               1.3
        # Shake with 0.25 ETH, odds: 5
        # Expected:
        #   Against:            
        #      has 2 

        self.clear_data_before_test()
        arr_hs = []
        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=88,
				outcome_id=88,
				odds=1.5,
				amount=0.2,
				currency='ETH',
				side=2,
				win_value=0.3,
				remaining_amount=0.2,
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
				is_private=1,
				user_id=99,
				outcome_id=88,
				odds=1.4,
				amount=0.1,
				currency='ETH',
				side=2,
				win_value=0.14,
				remaining_amount=0.1,
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
				is_private=1,
				user_id=109,
				outcome_id=88,
				odds=1.3,
				amount=0.3,
				currency='ETH',
				side=1,
				win_value=0.39,
				remaining_amount=0.3,
				from_address='0x123',
                status=0
        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        with self.client:
            Uid = 66

            params = {
                "type": 3,
                "extra_data": "",
                "description": "TESTING MODE",
                "outcome_id": 88,
                "odds": 5,
                "amount": 0.25,
                "currency": "ETH",
                "chain_id": 4,
                "side": 1,
                "from_address": "0x4f94a1392A6B48dda8F41347B15AF7B80f3c5f03"
            }
            response = self.client.post(
                                    '/handshake/init',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            data_json = data['data']
            self.assertTrue(data['status'] == 1)
            self.assertEqual(len(data_json), 3)
            self.assertEqual(response.status_code, 200)

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()


    def test_init_handshake_with_win_value_equal_amount(self):
        self.clear_data_before_test()
        
        with self.client:
            Uid = 88

            params = {
                "type": 3,
                "extra_data": "",
                "description": "TESTING MODE",
                "outcome_id": 4,
                "odds": 1,
                "amount": 1,
                "currency": "ETH",
                "chain_id": 4,
                "side": 2,
                "from_address": "0x4f94a1392A6B48dda8F41347B15AF7B80f3c5f03"
            }
            response = self.client.post(
                                    '/handshake/init',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 0)
            self.assertEqual(response.status_code, 200)

    def test_shake_handshake(self):
        pass

    def test_uninit_handshake(self):
        pass

    def test_refund_handshake(self):
        pass

    def test_collect_handshake(self):
        pass

    def test_rollback_handshake(self):
        pass
    
if __name__ == '__main__':
    unittest.main()