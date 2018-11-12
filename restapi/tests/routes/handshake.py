#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from tests.routes.base import BaseTestCase
from mock import patch
from app import db, app
from app.models import Handshake, User, Outcome, Match, Shaker, Task, Contract, Token, Setting, Redeem
from app.helpers.message import MESSAGE
from io import BytesIO
from datetime import datetime
from app.constants import Handshake as HandshakeStatus, RESULT_TYPE
from app.helpers.utils import local_to_utc

import time
import os
import mock
import json
import time
import app.bl.handshake as handshake_bl

class TestHandshakeBluePrint(BaseTestCase):   

    def setUp(self):
        # create token
        token = Token.find_token_by_id(1)
        if token is None:
            token = Token(
                id=1,
                name="SHURIKEN",
                symbol="SHURI",
                decimal=18
            )
            db.session.add(token)
            db.session.commit()

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

        user = User.find_user_with_id(100)
        if user is None:
            user = User(
                id=100
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
        # delete master user
        user = User.find_user_with_id(1)
        if user is not None:
            db.session.delete(user)
            db.session.commit()

        user = User.find_user_with_id(88)
        if user is not None:
            user.free_bet = 0
            db.session.commit()

        outcome = Outcome.find_outcome_by_id(88)
        if outcome is not None:
            outcome.token_id = None
            db.session.commit()

        handshakes = db.session.query(Handshake).filter(Handshake.outcome_id==88).all()
        for handshake in handshakes:
            db.session.delete(handshake)
            db.session.commit()

        match = Match.find_match_by_id(100)
        if match is not None:
            db.session.delete(match)
            db.session.commit()

        Task.query.delete()
        db.session.commit()

    def clear_all_bets_for_user(self, user_id):
        user = User.find_user_with_id(user_id)
        user.free_bet = 0
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
                odds=1.2,
                amount=1,
                currency='ETH',
                side=1,
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

            self.assertEqual(data_json['support'][0]['odds'], 1.2)
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
        #          remaining_amount = 0.375
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
            data_json = data['data']['handshakes']
            self.assertTrue(data['status'] == 1)
            self.assertEqual(len(data_json), 1)
            self.assertEqual(response.status_code, 200)

            hs = data_json[0]
            handshake = Handshake.find_handshake_by_id(handshake.id)
            self.assertEqual(hs['type'], 'shake')
            self.assertEqual(float(handshake.amount), 1)
            self.assertEqual(float(handshake.remaining_amount), 0.375)
            
            self.assertEqual(hs['amount'], 1.25)


        handshakes = handshake_bl.find_available_support_handshakes(88)
        self.assertEqual(len(handshakes), 1)
        handshake = handshakes[0]

        expectedOdds = 3
        expectedAmount = 0.375
        self.assertEqual(handshake[0], expectedOdds)
        self.assertEqual(handshake[1], expectedAmount)


        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()

    def test_init_handshake_case_2(self):
        self.clear_data_before_test()

        # Support
        #   amount          odds
        #   0.2               3         1.5
        #   0.1               2.9       1.52
        #   0.3               2.8       1.55  
        # Shake with 1.25 ETH, odds: 1.4
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
                "odds": 1.4,
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
            data_json = data['data']['handshakes']
            self.assertTrue(data['status'] == 1)
            self.assertEqual(len(data_json), 4)
            self.assertEqual(response.status_code, 200)


        new_handshake = data_json[3]
        self.assertEqual(new_handshake['amount'], 0.12)
        self.assertEqual(new_handshake['odds'], 1.4)

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()


    def test_init_handshake_case_3(self):
        self.clear_data_before_test()

        # Against
        #   amount          odds
        #   0.2               1.5           3
        #   0.1               1.4           3.5
        #   0.3               1.3           4.33
        # Shake with 0.25 ETH, odds: 5
        # Expected:
        #   Against:            
        #      no match, create new one

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
                                    content_type='application/json',
                                    data=json.dumps(params), 
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            data_json = data['data']['handshakes']
            self.assertTrue(data['status'] == 1)
            self.assertEqual(len(data_json), 1)

            maker = data_json[0]
            self.assertEqual(float(maker['remaining_amount']), 0.25)
            self.assertEqual(len(maker['shakers']), 0)
            self.assertEqual(response.status_code, 200)

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()


    def test_init_handshake_case_4(self):
        # DEBUG
        # Against
        #   amount          odds
        #   0.7               6           1.2
        #   0.007             1.5         3
        #   0.003             1.25        5
        # Shake with 0.001 ETH, odds: 1.2, side 1
        # Expected:
        #   Response:
        #       Amount: 0.001
        self.clear_data_before_test()
        arr_hs = []
        # -----
        handshake = Handshake(
                hs_type=3,
                chain_id=4,
                is_private=1,
                user_id=88,
                outcome_id=88,
                odds=6,
                amount=0.7,
                currency='ETH',
                side=2,
                remaining_amount=0.7,
                from_address='0x123',
                status=0
        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        maker = handshake.id

        # -----
        handshake = Handshake(
                hs_type=3,
                chain_id=4,
                is_private=1,
                user_id=99,
                outcome_id=88,
                odds=1.5,
                amount=0.007,
                currency='ETH',
                side=2,
                remaining_amount=0.007,
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
                odds=1.2,
                amount=0.003,
                currency='ETH',
                side=2,
                remaining_amount=0.003,
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
                "odds": 1.2,
                "amount": 0.001,
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
            data_json = data['data']['handshakes']
            self.assertTrue(data['status'] == 1)
            self.assertEqual(len(data_json), 1)

            hs = data_json[0]

            handshake = Handshake.find_handshake_by_id(handshake.id)
            self.assertEqual(float(handshake.amount), 0.003)
            self.assertEqual(float(handshake.remaining_amount), 0.0028)

            self.assertEqual(hs['type'], 'shake')
            self.assertEqual(hs['amount'], 0.001)

            handshake = Handshake.find_handshake_by_id(maker)
            self.assertEqual(float(handshake.amount), 0.7)
            self.assertEqual(float(handshake.remaining_amount), 0.7)


        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()

    def test_init_handshake_case_5(self):
        # DEBUG
        # Against
        #   amount          odds
        #   0.005           3           1.5
        # Shake with 0.001 ETH, odds: 1.5, side 1
        # Expected:
        #   Response:
        #       Amount: 0.01
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
                amount=0.005,
                currency='ETH',
                side=2,
                remaining_amount=0.005,
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
                "amount": 0.01,
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
            data_json = data['data']['handshakes']
            self.assertTrue(data['status'] == 1)
            self.assertEqual(len(data_json), 1)


            hs = data_json[0]
            handshake = Handshake.find_handshake_by_id(handshake.id)
            self.assertEqual(handshake.remaining_amount, 0)
            self.assertEqual(float(handshake.amount), 0.005)

            self.assertEqual(hs['type'], 'shake')
            self.assertEqual(hs['amount'], 0.01)

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()


    def test_init_handshake_case_8(self):
        # DEBUG
        # Against
        #   amount          odds
        #   0.01           1.6           2.666666666666
        # Shake with 0.006 ETH, odds: 2.67, side 1
        # Expected:
        #   Response:
        #       Amount: 0.01
        self.clear_data_before_test()
        arr_hs = []
        # -----
        handshake = Handshake(
                hs_type=3,
                chain_id=4,
                is_private=1,
                user_id=88,
                outcome_id=88,
                odds=1.6,
                amount=0.01,
                currency='ETH',
                side=2,
                remaining_amount=0.01,
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
                "odds": 2.6,
                "amount": 0.006,
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
            data_json = data['data']['handshakes']

            handshake = data_json[0]
            self.assertEqual(len(data_json), 1)
            self.assertTrue(data['status'] == 1)
            self.assertEqual(handshake['type'], 'shake')

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()

    def test_init_handshake_case_6(self):
        # DEBUG
        # Support
        #   amount          odds
        #   0.001           2.25           
        # Shake with 0.01 ETH, odds: 1.8, side 2
        self.clear_data_before_test()
        arr_hs = []
        # -----
        handshake = Handshake(
                hs_type=3,
                chain_id=4,
                is_private=1,
                user_id=88,
                outcome_id=88,
                odds=2.2,
                amount=0.001,
                currency='ETH',
                side=1,
                remaining_amount=0.001,
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
                "odds": 1.8,
                "amount": 0.01,
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
            data_json = data['data']['handshakes']

            handshake = data_json[0]
            self.assertTrue(data['status'] == 1)
            self.assertEqual(handshake['type'], 'shake')

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()


    def test_init_handshake_case_7(self):
        # DEBUG
        # Support
        #   amount          odds
        #   0.000003        2.4
        # Shake with 0.0000042 ETH, odds: 1.71, side 2
        # Expected:
        #   Response:
        #       Amount: 0.01
        self.clear_data_before_test()
        arr_hs = []
        # -----
        handshake = Handshake(
                hs_type=3,
                chain_id=4,
                is_private=1,
                user_id=88,
                outcome_id=88,
                odds=2.4,
                amount=0.000003,
                currency='ETH',
                side=1,
                remaining_amount=0.000003,
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
                "odds": 1.7,
                "amount": 0.0000042,
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
            data_json = data['data']['handshakes']

            handshake = data_json[0]
            self.assertEqual(len(data_json), 1)
            self.assertTrue(data['status'] == 1)
            self.assertEqual(handshake['type'], 'shake')

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()


    def test_init_handshake_case_9(self):
        # DEBUG
        # Support
        #   amount          odds
        #   0.001           1.37
        # Shake with 0.01 ETH, odds: 3.7, side 2
        self.clear_data_before_test()
        arr_hs = []
        # -----
        handshake = Handshake(
                hs_type=3,
                chain_id=4,
                is_private=1,
                user_id=88,
                outcome_id=88,
                odds=1.37,
                amount=0.001,
                currency='ETH',
                side=1,
                remaining_amount=0.001,
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
                "odds": 3.7,
                "amount": 0.01,
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
            data_json = data['data']['handshakes']

            handshake = data_json[0]
            self.assertEqual(len(data_json), 2)
            self.assertTrue(data['status'] == 1)
            self.assertEqual(handshake['type'], 'shake')

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

    def test_rollback_handshake_with_shake_state(self):
        self.clear_data_before_test()
        arr_hs = []
        # -----
        handshake = Handshake(
                hs_type=3,
                chain_id=4,
                is_private=1,
                user_id=88,
                outcome_id=88,
                odds=6,
                amount=0.7,
                currency='ETH',
                side=2,
                remaining_amount=0.7,
                from_address='0x123',
                status=0,
                bk_status=-1,
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
                "odds": "1.2",
                "amount": "0.5",
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
            data_json = data['data']['handshakes']

            hs = Handshake.find_handshake_by_id(handshake.id)
            self.assertEqual(float(hs.remaining_amount), 0.6)

            sk = data_json[0]
            self.assertEqual(sk['amount'], 0.5)
            shaker_id = sk['id']
            handshake_id = handshake.id

            # rollback here
            params = {
                "offchain": 'cryptosign_s{}'.format(shaker_id)
            }
            response = self.client.post(
                                    '/handshake/rollback',
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

            h = Handshake.find_handshake_by_id(handshake_id)
            self.assertEqual(float(h.amount), 0.7)
            self.assertEqual(float(h.remaining_amount), 0.7)

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()

    def test_rollback_handshake_with_init_state(self):
        self.clear_data_before_test()
        arr_hs = []
        # -----
        handshake = Handshake(
                hs_type=3,
                chain_id=4,
                is_private=1,
                user_id=88,
                outcome_id=88,
                odds=6,
                amount=0.01,
                currency='ETH',
                side=2,
                remaining_amount=0.7,
                from_address='0x123',
                status=-1,
                bk_status=-1,
        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        with self.client:
            Uid = 88

            params = {
                "offchain": 'cryptosign_m{}'.format(handshake.id)
            }

            response = self.client.post(
                                    '/handshake/rollback',
                                    content_type='application/json',
                                    data=json.dumps(params),
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            handshake = data['data']
            self.assertNotEqual(handshake['status'], handshake['bk_status'])
            self.assertEqual(handshake['status'], HandshakeStatus['STATUS_MAKER_INIT_ROLLBACK'])

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()

    def test_rollback_handshake_with_init_state_and_free_bet(self):
        self.clear_data_before_test()

        user = User.find_user_with_id(88)
        user.free_bet = 1
        db.session.commit()

        arr_hs = []
        # -----
        handshake = Handshake(
                hs_type=3,
                chain_id=4,
                is_private=1,
                user_id=88,
                outcome_id=88,
                odds=6,
                amount=0.7,
                currency='ETH',
                side=2,
                remaining_amount=0.7,
                from_address='0x123',
                status=-1,
                bk_status=-1,
                free_bet=1
        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        with self.client:
            Uid = 88

            params = {
                "offchain": 'cryptosign_m{}'.format(handshake.id)
            }

            response = self.client.post(
                                    '/handshake/rollback',
                                    content_type='application/json',
                                    data=json.dumps(params),
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            handshake = data['data']
            self.assertNotEqual(handshake['status'], handshake['bk_status'])
            self.assertEqual(handshake['status'], HandshakeStatus['STATUS_MAKER_INIT_ROLLBACK'])

            user = User.find_user_with_id(88)
            self.assertEqual(user.free_bet, 0)

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()

    def test_rollback_handshake_with_shake_state_and_free_bet(self):
        self.clear_data_before_test()
        arr_hs = []
        # -----
        handshake = Handshake(
                hs_type=3,
                chain_id=4,
                is_private=1,
                user_id=88,
                outcome_id=88,
                odds=6,
                amount=0.7,
                currency='ETH',
                side=2,
                remaining_amount=0,
                from_address='0x123',
                status=0,
                bk_status=-1,
        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        shaker = Shaker(
            shaker_id=66,
            amount=3.5,
            currency='ETH',
            odds=1.2,
            side=1,
            handshake_id=handshake.id,
            from_address='0x123',
            chain_id=4,
            status=-1,
            free_bet=1
        )
        arr_hs.append(shaker)
        db.session.add(shaker)
        db.session.commit()

        user = User.find_user_with_id(66)
        user.free_bet = 1
        db.session.commit()

        with self.client:
            Uid = 66

            # rollback here
            params = {
                "offchain": 'cryptosign_s{}'.format(shaker.id)
            }
            response = self.client.post(
                                    '/handshake/rollback',
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

            h = Handshake.find_handshake_by_id(handshake.id)
            self.assertEqual(float(h.amount), 0.7)
            self.assertEqual(float(h.remaining_amount), 0.7)

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()

    def test_create_free_bet(self):
        self.clear_data_before_test()
        self.clear_all_bets_for_user(99)
        arr_hs = []
        # Make sure redeem_code added into "routes/redeem.txt"
        # Add reddem code
        redeem_code = "123abcd"
        redeem_path = os.path.abspath(os.path.dirname(__file__)) + '/../../app/routes/redeem.txt'
        with open(redeem_path, 'a') as file:
            file.write('{}\n'.format(redeem_code))

        redeem = Redeem.find_redeem_by_code(redeem_code)
        if redeem is None:
            redeem = Redeem(
                code=redeem_code
            )
            db.session.add(redeem)
        else:
            redeem.used_user=None
        db.session.commit()
        arr_hs.append(redeem)

        user = User.find_user_with_id(99)
        old_free_bet = user.free_bet

        outcome = Outcome.find_outcome_by_id(88)
        outcome.result = -1
        db.session.commit()

        with self.client:
            Uid = 99

            params = {
                "type": 3,
                "extra_data": "",
                "description": "DTHTRONG",
                "outcome_id": 88,
                "odds": "1.7",
                "currency": "ETH",
                "chain_id": 4,
                "side": 2,
                "from_address": "0x4f94a1392a6b48dda8f41347b15af7b80f3c5f03",
                "redeem": redeem_code
            }

            response = self.client.post(
                                    '/handshake/create_free_bet',
                                    content_type='application/json',
                                    data=json.dumps(params),
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            data = data['data']
            self.assertTrue('match' in data)

            user = User.find_user_with_id(99)
            self.assertEqual(old_free_bet + 1, user.free_bet)

            # create free-bet again
            handshake = Handshake(
                            hs_type=3,
                            chain_id=4,
                            is_private=1,
                            user_id=99,
                            outcome_id=88,
                            odds=6,
                            amount=0.7,
                            currency='ETH',
                            side=2,
                            remaining_amount=0.7,
                            from_address='0x123',
                            status=HandshakeStatus['STATUS_RESOLVED'],
                            bk_status=0,
                            free_bet=1
                        )
            arr_hs.append(handshake)
            db.session.add(handshake)
            db.session.commit()

            params = {
                "type": 3,
                "extra_data": "",
                "description": "DTHTRONG",
                "outcome_id": 88,
                "odds": "1.7",
                "currency": "ETH",
                "chain_id": 4,
                "side": 2,
                "from_address": "0x4f94a1392a6b48dda8f41347b15af7b80f3c5f03"
            }

            response = self.client.post(
                                    '/handshake/create_free_bet',
                                    content_type='application/json',
                                    data=json.dumps(params),
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })
            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 0)
            
            # call check-free-bet
            setting = Setting.find_setting_by_name('FreeBet')
            if setting is None:
                setting = Setting(
                    name="FreeBet",
                    status=1
                )
                db.session.add(setting)
            else:
                setting.status = 1
            db.session.commit()
            response = self.client.get(
                                    '/handshake/check_free_bet',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            d = data['data']
            self.assertEqual(d['free_bet_available'], 2)

    def test_collect_real_bet(self):
        self.clear_data_before_test()

        arr_hs = []
        # -----
        handshake_inited = Handshake(
                            hs_type=3,
                            chain_id=4,
                            is_private=1,
                            user_id=88,
                            outcome_id=88,
                            odds=6,
                            amount=0.7,
                            currency='ETH',
                            side=2,
                            remaining_amount=0.7,
                            from_address='0x123',
                            status=HandshakeStatus['STATUS_INITED'],
                            bk_status=0,
                            free_bet=1
                        )
        arr_hs.append(handshake_inited)
        db.session.add(handshake_inited)
        db.session.commit()

        # -----
        shaker_inited = Shaker(
            shaker_id=88,
            amount=3.5,
            currency='ETH',
            odds=1.2,
            side=2,
            handshake_id=handshake_inited.id,
            from_address='0x123',
            chain_id=4,
            status=HandshakeStatus['STATUS_SHAKER_SHAKED'],
            free_bet=1
        )
        arr_hs.append(shaker_inited)
        db.session.add(shaker_inited)
        db.session.commit()

        outcome = Outcome.find_outcome_by_id(88)
        outcome.result = 2
        db.session.commit()
        
        with self.client:
            Uid = 88

            params = {
                "offchain": "cryptosign_m{}".format(handshake_inited.id)
            }

            response = self.client.post(
                                    '/handshake/collect',
                                    content_type='application/json',
                                    data=json.dumps(params),
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['status'] == 1)
            
            hs = Handshake.find_handshake_by_id(handshake_inited.id)
            self.assertEqual(hs.status, HandshakeStatus['STATUS_COLLECT_PENDING'])

            sk = Shaker.find_shaker_by_id(shaker_inited.id)
            self.assertEqual(sk.status, HandshakeStatus['STATUS_COLLECT_PENDING'])

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()

    def test_collect_real_bet_resolved(self):
        self.clear_data_before_test()

        arr_hs = []
        # -----
        handshake_resolved = Handshake(
                            hs_type=3,
                            chain_id=4,
                            is_private=1,
                            user_id=88,
                            outcome_id=88,
                            odds=6,
                            amount=0.7,
                            currency='ETH',
                            side=2,
                            remaining_amount=0.7,
                            from_address='0x123',
                            status=HandshakeStatus['STATUS_RESOLVED'],
                            bk_status=0,
                            free_bet=1
                        )
        arr_hs.append(handshake_resolved)
        db.session.add(handshake_resolved)
        db.session.commit()

        # -----
        shaker_resolved = Shaker(
            shaker_id=88,
            amount=3.5,
            currency='ETH',
            odds=1.2,
            side=2,
            handshake_id=handshake_resolved.id,
            from_address='0x123',
            chain_id=4,
            status=HandshakeStatus['STATUS_RESOLVED'],
            free_bet=1
        )
        arr_hs.append(shaker_resolved)
        db.session.add(shaker_resolved)
        db.session.commit()
        
        outcome = Outcome.find_outcome_by_id(88)
        outcome.result = 2
        db.session.commit()
        
        with self.client:
            Uid = 88

            params = {
                "offchain": "cryptosign_m{}".format(handshake_resolved.id)
            }

            response = self.client.post(
                                    '/handshake/collect',
                                    content_type='application/json',
                                    data=json.dumps(params),
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['status'] == 1)
            
            hs = Handshake.find_handshake_by_id(handshake_resolved.id)
            self.assertEqual(hs.status, HandshakeStatus['STATUS_COLLECT_PENDING'])

            sk = Shaker.find_shaker_by_id(shaker_resolved.id)
            self.assertEqual(sk.status, HandshakeStatus['STATUS_COLLECT_PENDING'])

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()

    def test_refund_real_bet(self):
        self.clear_data_before_test()

        match = Match.find_match_by_id(1)
        match.reportTime = time.time() - 1000
        db.session.merge(match)
        db.session.commit()
        
        arr_hs = []

        # -----
        handshake_inited = Handshake(
                            hs_type=3,
                            chain_id=4,
                            is_private=1,
                            user_id=88,
                            outcome_id=88,
                            odds=6,
                            amount=0.7,
                            currency='ETH',
                            side=2,
                            remaining_amount=0.7,
                            from_address='0x123',
                            status=HandshakeStatus['STATUS_INITED'],
                            bk_status=0,
                            free_bet=1
                        )
        arr_hs.append(handshake_inited)
        db.session.add(handshake_inited)
        db.session.commit()

        # -----
        shaker_inited = Shaker(
            shaker_id=88,
            amount=3.5,
            currency='ETH',
            odds=1.2,
            side=1,
            handshake_id=handshake_inited.id,
            from_address='0x123',
            chain_id=4,
            status=HandshakeStatus['STATUS_SHAKER_SHAKED'],
            free_bet=1
        )
        arr_hs.append(shaker_inited)
        db.session.add(shaker_inited)
        db.session.commit()
        
        outcome = Outcome.find_outcome_by_id(88)
        outcome.result = 2
        db.session.commit()
        
        with self.client:
            Uid = 88

            params = {
                "offchain": "cryptosign_m{}".format(handshake_inited.id)
            }

            response = self.client.post(
                                    '/handshake/refund',
                                    content_type='application/json',
                                    data=json.dumps(params),
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            # If hacker know????
            self.assertTrue(data['status'] == 1)

            outcome.result = 3
            db.session.merge(outcome)
            db.session.commit()

            # call again
            response = self.client.post(
                                    '/handshake/refund',
                                    content_type='application/json',
                                    data=json.dumps(params),
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['status'] == 1)
            
            hs = Handshake.find_handshake_by_id(handshake_inited.id)
            self.assertEqual(hs.status, HandshakeStatus['STATUS_REFUND_PENDING'])

            sk = Shaker.find_shaker_by_id(shaker_inited.id)
            self.assertEqual(sk.status, HandshakeStatus['STATUS_REFUND_PENDING'])

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()


    def test_refund_real_bet_resolved(self):
        self.clear_data_before_test()

        match = Match.find_match_by_id(1)
        match.reportTime = time.time() - 1000
        db.session.merge(match)
        db.session.commit()
        
        arr_hs = []

        # -----
        handshake_resolved = Handshake(
                            hs_type=3,
                            chain_id=4,
                            is_private=1,
                            user_id=88,
                            outcome_id=88,
                            odds=6,
                            amount=0.7,
                            currency='ETH',
                            side=2,
                            remaining_amount=0.7,
                            from_address='0x123',
                            status=HandshakeStatus['STATUS_RESOLVED'],
                            bk_status=0,
                            free_bet=1
                        )
        arr_hs.append(handshake_resolved)
        db.session.add(handshake_resolved)
        db.session.commit()

        # -----
        shaker_resolved = Shaker(
            shaker_id=88,
            amount=3.5,
            currency='ETH',
            odds=1.2,
            side=1,
            handshake_id=handshake_resolved.id,
            from_address='0x123',
            chain_id=4,
            status=2,
            free_bet=1
        )
        arr_hs.append(shaker_resolved)
        db.session.add(shaker_resolved)
        db.session.commit()
        
        outcome = Outcome.find_outcome_by_id(88)
        outcome.result = 2
        db.session.commit()
        
        with self.client:
            Uid = 88

            params = {
                "offchain": "cryptosign_m{}".format(handshake_resolved.id)
            }

            response = self.client.post(
                                    '/handshake/refund',
                                    content_type='application/json',
                                    data=json.dumps(params),
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            # If hacker know????
            self.assertTrue(data['status'] == 1)

            outcome.result = 3
            db.session.merge(outcome)
            db.session.commit()

            # call again
            response = self.client.post(
                                    '/handshake/refund',
                                    content_type='application/json',
                                    data=json.dumps(params),
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['status'] == 1)

            hs = Handshake.find_handshake_by_id(handshake_resolved.id)
            self.assertEqual(hs.status, HandshakeStatus['STATUS_REFUND_PENDING'])

            sk = Shaker.find_shaker_by_id(shaker_resolved.id)
            self.assertEqual(sk.status, HandshakeStatus['STATUS_REFUND_PENDING'])

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()

    def test_collect_free_bet(self):
        self.clear_data_before_test()
        arr_hs = []
        # -----
        handshake = Handshake(
                            hs_type=3,
                            chain_id=4,
                            is_private=1,
                            user_id=88,
                            outcome_id=88,
                            odds=6,
                            amount=0.7,
                            currency='ETH',
                            side=2,
                            remaining_amount=0.7,
                            from_address='0x123',
                            status=0,
                            bk_status=0,
                            free_bet=1
                        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        outcome = Outcome.find_outcome_by_id(88)
        outcome.match_id = 1
        outcome.result = 2
        db.session.commit()

        match = Match.find_match_by_id(1)
        t = datetime.now().timetuple()
        seconds = local_to_utc(t)
        match.date = seconds = 100
        match.disputeTime = seconds + 1100
        match.reportTime = seconds + 1000
        db.session.commit()

        with self.client:
            Uid = 88

            params = {
                "offchain": "cryptosign_m{}".format(handshake.id)
            }

            response = self.client.post(
                                    '/handshake/collect_free_bet',
                                    content_type='application/json',
                                    data=json.dumps(params),
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            hs = data['data']
            self.assertEqual(hs['status'], HandshakeStatus['STATUS_COLLECT_PENDING'])
        
        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()


    def test_collect_free_bet_1(self):
        self.clear_data_before_test()
        arr_hs = []
        # -----
        handshake = Handshake(
                hs_type=3,
                chain_id=4,
                is_private=1,
                user_id=88,
                outcome_id=88,
                odds=6,
                amount=0.7,
                currency='ETH',
                side=2,
                remaining_amount=0.7,
                from_address='0x123',
                status=0,
                bk_status=0
        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        handshake_id = handshake.id

        # -----
        handshake = Handshake(
                hs_type=3,
                chain_id=4,
                is_private=1,
                user_id=66,
                outcome_id=88,
                odds=6,
                amount=0.7,
                currency='ETH',
                side=1,
                remaining_amount=0.7,
                from_address='0x123',
                status=0,
                bk_status=0
        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        handshake_id_1 = handshake.id
        
        shaker = Shaker(
            shaker_id=66,
            amount=3.5,
            currency='ETH',
            odds=1.2,
            side=1,
            handshake_id=handshake_id,
            from_address='0x123',
            chain_id=4,
            status=-1,
            free_bet=1
        )
        arr_hs.append(shaker)
        db.session.add(shaker)
        db.session.commit()

        shaker_id = shaker.id

        with self.client:
            Uid = 66

            params = {
                "offchain": "cryptosign_s{}".format(shaker_id)
            }

            response = self.client.post(
                                    '/handshake/collect_free_bet',
                                    content_type='application/json',
                                    data=json.dumps(params),
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            # cannot withdraw because status = -1
            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 0)
            self.assertEqual(response.status_code, 200)

        
        shaker = Shaker.find_shaker_by_id(shaker_id)
        shaker.status = 2

        outcome = Outcome.find_outcome_by_id(88)
        outcome.result = 1

        match = Match.find_match_by_id(outcome.match_id)
        match.disputeTime = time.time() - 28600
        db.session.commit()


        with self.client:
            Uid = 88

            params = {
                "offchain": "cryptosign_m{}".format(handshake_id)
            }

            response = self.client.post(
                                    '/handshake/collect_free_bet',
                                    content_type='application/json',
                                    data=json.dumps(params),
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            # cannot withdraw because handshake now win
            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 0)
            self.assertEqual(response.status_code, 200)

            Uid = 66
            params = {
                "offchain": 'cryptosign_s{}'.format(shaker_id)
            }
            response = self.client.post(
                                    '/handshake/collect_free_bet',
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

            shaker = Shaker.find_shaker_by_id(shaker_id)
            self.assertEqual(shaker.status, HandshakeStatus['STATUS_COLLECT_PENDING']) # pending collect method
            self.assertEqual(shaker.amount, 3.5)

            hs = Handshake.find_handshake_by_id(handshake_id)
            self.assertEqual(hs.status, HandshakeStatus['STATUS_INITED'])

            hs1 = Handshake.find_handshake_by_id(handshake_id_1)
            self.assertEqual(hs1.status, HandshakeStatus['STATUS_COLLECT_PENDING'])

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()
 

    def test_uninit_free_bet(self):
        self.clear_data_before_test()
        arr_hs = []
        # -----
        handshake = Handshake(
                            hs_type=3,
                            chain_id=4,
                            is_private=1,
                            user_id=88,
                            outcome_id=88,
                            odds=6,
                            amount=0.7,
                            currency='ETH',
                            side=2,
                            remaining_amount=0.7,
                            from_address='0x123',
                            status=0,
                            bk_status=0,
                            free_bet=1,
                            date_created=datetime.now(),
                            date_modified=datetime.now()
                        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        with self.client:
            Uid = 88

            response = self.client.post(
                                    '/handshake/uninit_free_bet/{}'.format(handshake.id),
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 0)
            self.assertEqual(response.status_code, 200)

            handshake.date_created=datetime(2018, 6, 18)
            db.session.flush()
            db.session.commit()

            # call uninit again
            response = self.client.post(
                                    '/handshake/uninit_free_bet/{}'.format(handshake.id),
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

    def test_check_free_bet(self):
        self.clear_data_before_test()
        arr_hs = []
        self.clear_all_bets_for_user(100)

        redeem_code = "123abcd"
        redeem = Redeem.find_redeem_by_code(redeem_code)
        if redeem is None:
            redeem = Redeem(
                code=redeem_code
            )
            db.session.add(redeem)
        else:
            redeem.used_user=None
        db.session.commit()    
        arr_hs.append(redeem)

        with self.client:
            Uid = 100
            setting = Setting.find_setting_by_name('FreeBet')
            if setting is None:
                setting = Setting(
                    name="FreeBet",
                    status=1
                )
                db.session.add(setting)
            else:
                setting.status = 1
            db.session.commit()
            response = self.client.get(
                                    '/handshake/check_free_bet',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)
            d = data['data']
            self.assertEqual(d['free_bet_available'], 3)

            # create a free-bet
            params = {
                "type": 3,
                "extra_data": "",
                "description": "DTHTRONG",
                "outcome_id": 88,
                "odds": "1.7",
                "currency": "ETH",
                "chain_id": 4,
                "side": 2,
                "from_address": "0x4f94a1392a6b48dda8f41347b15af7b80f3c5f03",
                "redeem": redeem_code
            }

            response = self.client.post(
                                    '/handshake/create_free_bet',
                                    content_type='application/json',
                                    data=json.dumps(params),
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

            # call check free bet again
            setting = Setting.find_setting_by_name('FreeBet')
            if setting is None:
                setting = Setting(
                    name="FreeBet",
                    status=1
                )
                db.session.add(setting)
            else:
                setting.status = 1
            db.session.commit()
            response = self.client.get(
                                    '/handshake/check_free_bet',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)
            d = data['data']
            self.assertEqual(d['free_bet_available'], 2)


            # call check-free-bet with extension
            setting = Setting.find_setting_by_name('FreeBet')
            if setting is None:
                setting = Setting(
                    name="FreeBet",
                    status=0
                )
                db.session.add(setting)
            else:
                setting.status = 0
            db.session.commit()

            response = self.client.get(
                                    '/handshake/check_free_bet',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 0)
            self.assertEqual(response.status_code, 200)

            response = self.client.get(
                                    '/handshake/check_free_bet',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                        "Request-From": 'extension'
                                    })
            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)
            self.assertEqual(response.status_code, 200)

            response = self.client.get(
                                    '/handshake/check_free_bet',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                        "Request-From": 'mobile'
                                    })
            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 0)
            self.assertEqual(response.status_code, 200)

            setting = Setting.find_setting_by_name('FreeBet')
            setting.status = 1
            db.session.commit()

    def test_refund_free_bet(self):
        self.clear_data_before_test()

        match = Match.find_match_by_id(1)
        match.reportTime = time.time() + 1000
        db.session.merge(match)
        db.session.commit()

        arr_hs = []
        # -----
        handshake = Handshake(
                            hs_type=3,
                            chain_id=4,
                            is_private=1,
                            user_id=88,
                            outcome_id=88,
                            odds=6,
                            amount=0.7,
                            currency='ETH',
                            side=2,
                            remaining_amount=0.7,
                            from_address='0x123',
                            status=0,
                            bk_status=0,
                            free_bet=1,
                            date_created=datetime.now(),
                            date_modified=datetime.now()
                        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        with self.client:
            Uid = 88

            params = {
                "offchain": "cryptosign_m{}".format(handshake.id)
            }

            response = self.client.post(
                                    '/handshake/refund_free_bet',
                                    content_type='application/json',
                                    data=json.dumps(params),
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 0)
            self.assertEqual(response.status_code, 200)

            outcome = Outcome.find_outcome_by_id(88)
            outcome.result = 3
            db.session.merge(outcome)
            db.session.commit()

            # call refund again
            response = self.client.post(
                                    '/handshake/refund_free_bet',
                                    content_type='application/json',
                                    data=json.dumps(params),
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

    def test_dispute_real_bet(self):
        self.clear_data_before_test()

        match = Match.find_match_by_id(1)
        match.disputeTime = time.time() + 1000
        match.date = time.time() - 1000
        db.session.merge(match)
        db.session.commit()
        
        arr_hs = []

        # -----
        handshake = Handshake(
                            hs_type=3,
                            chain_id=4,
                            is_private=1,
                            user_id=88,
                            outcome_id=88,
                            odds=6,
                            amount=1,
                            currency='ETH',
                            side=2,
                            shake_count=1,
                            remaining_amount=0.7,
                            from_address='0x123',
                            status=0,
                            bk_status=0,
                            free_bet=1
                        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        # -----
        shaker = Shaker(
            shaker_id=88,
            amount=3.5,
            currency='ETH',
            odds=1.2,
            side=1,
            handshake_id=handshake.id,
            from_address='0x123',
            chain_id=4,
            status=2,
            free_bet=1
        )
        arr_hs.append(shaker)
        db.session.add(shaker)
        db.session.commit()
        
        outcome = Outcome.find_outcome_by_id(88)
        outcome.result = 2
        db.session.commit()
        
        with self.client:
            Uid = 88

            params = {
                "offchain": 'cryptosign_s{}'.format(shaker.id)
            }

            response = self.client.post(
                                    '/handshake/dispute',
                                    content_type='application/json',
                                    data=json.dumps(params),
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['status'] == 1)

            sk = Shaker.find_shaker_by_id(shaker.id)
            self.assertEqual(sk.status, HandshakeStatus['STATUS_DISPUTE_PENDING'])

            outcome.result = 1
            db.session.commit()
            params = {
                "offchain": 'cryptosign_m{}'.format(handshake.id)
            }

            response = self.client.post(
                                    '/handshake/dispute',
                                    content_type='application/json',
                                    data=json.dumps(params),
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['status'] == 1)

            hs = Handshake.find_handshake_by_id(handshake.id)
            self.assertEqual(hs.status, HandshakeStatus['STATUS_DISPUTE_PENDING'])

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()


    def test_init_handshake_with_free_bet(self):
        self.clear_data_before_test()
        arr_hs = []
        self.clear_all_bets_for_user(100)
    
        with self.client:

            outcome = Outcome.find_outcome_by_id(88)
            outcome.token_id = 1
            db.session.commit()

            Uid = 100

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
                "from_address": "0x4f94a1392A6B48dda8F41347B15AF7B80f3c5f03",
                "free_bet": 1
            }

            response = self.client.post(
                                    '/handshake/init',
                                    content_type='application/json',
                                    data=json.dumps(params),
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 0)


    def test_create_free_bet_with_erc20_outcome(self):
        self.clear_data_before_test()
        self.clear_all_bets_for_user(100)

        outcome = Outcome.find_outcome_by_id(88)
        outcome.token_id = 1
        db.session.commit()

        arr_hs = []
        with self.client:
            Uid = 99

            params = {
                "type": 3,
                "extra_data": "",
                "description": "DTHTRONG",
                "outcome_id": 88,
                "odds": "1.7",
                "currency": "ETH",
                "chain_id": 4,
                "side": 2,
                "from_address": "0x4f94a1392a6b48dda8f41347b15af7b80f3c5f03"
            }

            response = self.client.post(
                                    '/handshake/create_free_bet',
                                    content_type='application/json',
                                    data=json.dumps(params),
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 0)
            self.assertEqual(response.status_code, 200)

    
    def test_uninit_free_bet_with_erc20_outcome(self):
        self.clear_data_before_test()

        outcome = Outcome.find_outcome_by_id(88)
        outcome.token_id = 1
        db.session.commit()

        arr_hs = []
        # -----
        handshake = Handshake(
                            hs_type=3,
                            chain_id=4,
                            is_private=1,
                            user_id=88,
                            outcome_id=88,
                            odds=6,
                            amount=0.7,
                            currency='ETH',
                            side=2,
                            remaining_amount=0.7,
                            from_address='0x123',
                            status=0,
                            bk_status=0,
                            free_bet=1,
                            date_created=datetime.now(),
                            date_modified=datetime.now()
                        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        with self.client:
            Uid = 88

            response = self.client.post(
                                    '/handshake/uninit_free_bet/{}'.format(handshake.id),
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 0)
            self.assertEqual(response.status_code, 200)

            handshake.date_created=datetime(2018, 6, 18)
            db.session.flush()
            db.session.commit()

            # call uninit again
            response = self.client.post(
                                    '/handshake/uninit_free_bet/{}'.format(handshake.id),
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 0)
            self.assertEqual(response.status_code, 200)

        
        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()


    def test_collect_free_bet_with_erc20_outcome(self):
        self.clear_data_before_test()
        arr_hs = []

        outcome = Outcome.find_outcome_by_id(88)
        outcome.token_id = 1
        db.session.commit()

        # -----
        handshake = Handshake(
                            hs_type=3,
                            chain_id=4,
                            is_private=1,
                            user_id=88,
                            outcome_id=88,
                            odds=6,
                            amount=0.7,
                            currency='ETH',
                            side=2,
                            remaining_amount=0.7,
                            from_address='0x123',
                            status=0,
                            bk_status=0,
                            free_bet=1
                        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        outcome = Outcome.find_outcome_by_id(88)
        outcome.match_id = 1
        outcome.result = 2
        db.session.commit()

        match = Match.find_match_by_id(1)
        t = datetime.now().timetuple()
        seconds = local_to_utc(t)
        match.date = seconds = 100
        match.disputeTime = seconds + 1100
        match.reportTime = seconds + 1000
        db.session.commit()

        with self.client:
            Uid = 88

            params = {
                "offchain": "cryptosign_m{}".format(handshake.id)
            }

            response = self.client.post(
                                    '/handshake/collect_free_bet',
                                    content_type='application/json',
                                    data=json.dumps(params),
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 0)
        
        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()


    def test_case_1_init_handshake_with_binary_event(self):
        """
        "   No need odds, outcome_id
        "   Required: match_id
        """
        self.clear_data_before_test()
        arr_hs = []

        match = Match.find_match_by_id(1)
        outcome = match.outcomes.first()
        outcome.result = -1
        outcome.contract_id = 1
        db.session.commit()
        
        # -----
        with self.client:
            Uid = 66

            params = {
                "type": 3,
                "extra_data": "",
                "description": "TESTING MODE",
                "match_id": 1,
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
            data_json = data['data']['handshakes']
            self.assertTrue(data['status'] == 1)
            self.assertEqual(len(data_json), 1)
            self.assertEqual(response.status_code, 200)

            hs = data_json[0]
            self.assertEqual(hs['type'], 'init')
            self.assertEqual(hs['amount'], 1.25)
            arr_hs.append(Handshake.find_handshake_by_id(hs['id']))
        
        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()


    def test_case_2_init_handshake_with_binary_event(self):
        """
        "   No need odds, outcome_id
        "   Required: match_id
        """
        self.clear_data_before_test()
        arr_hs = []

        match = Match.find_match_by_id(1)
        outcome = match.outcomes.first()
        outcome.result = -1
        outcome.contract_id = 1
        db.session.commit()

        # -----
        handshake = Handshake(
                            hs_type=3,
                            chain_id=4,
                            is_private=1,
                            user_id=88,
                            outcome_id=outcome.id,
                            odds=2,
                            amount=0.7,
                            currency='ETH',
                            side=1,
                            remaining_amount=0.7,
                            from_address='0x123',
                            status=0,
                            bk_status=0,
                            free_bet=0
                        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        # ----
        original_handshake_id = handshake.id
        
        # -----
        with self.client:
            Uid = 66

            params = {
                "type": 3,
                "extra_data": "",
                "description": "TESTING MODE",
                "match_id": 1,
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
            data_json = data['data']['handshakes']
            self.assertTrue(data['status'] == 1)
            self.assertEqual(len(data_json), 2)
            self.assertEqual(response.status_code, 200)

            hs1 = data_json[0]
            self.assertEqual(hs1['type'], 'shake')
            self.assertEqual(hs1['amount'], 0.7)
            arr_hs.append(Handshake.find_handshake_by_id(hs1['id']))

            hs2 = data_json[1]
            self.assertEqual(hs2['type'], 'init')
            self.assertEqual(hs2['amount'], 0.55)
            arr_hs.append(Handshake.find_handshake_by_id(hs2['id']))

            # check remaining amount of original handshake
            ori_hs = Handshake.find_handshake_by_id(original_handshake_id)
            self.assertEqual(ori_hs.remaining_amount, 0)
        
        for handshake in arr_hs:
            if handshake is not None:
                db.session.delete(handshake)
                db.session.commit()


if __name__ == '__main__':
    unittest.main()