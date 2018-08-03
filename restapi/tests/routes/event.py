from tests.routes.base import BaseTestCase
from mock import patch
from app.models import Shaker, Handshake, Outcome, Shaker, User, Match, Tx
from app import db, app
from app.helpers.message import MESSAGE
from app.constants import Handshake as HandshakeStatus

import mock
import json
import time
import app.bl.user as user_bl
import app.constants as CONST

class TestEventBluePrint(BaseTestCase):

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


        user = User.find_user_with_id(33)
        if user is None:
            user = User(
                id=33
            )
            db.session.add(user)
            db.session.commit()

        user = User.find_user_with_id(22)
        if user is None:
            user = User(
                id=22
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
        # delete master user
        user = User.find_user_with_id(1)
        if user is not None:
            db.session.delete(user)
            db.session.commit()

        outcome = Outcome.find_outcome_by_id(88)
        if outcome is not None:
            outcome.result = -1
            db.session.commit()

        handshakes = db.session.query(Handshake).filter(Handshake.outcome_id==88).all()
        for handshake in handshakes:
            db.session.delete(handshake)
            db.session.commit()

    def test_reiceive_init_event(self):
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
                status=-1
        )
        db.session.add(handshake)
        db.session.commit()

        handshake_id = handshake.id

        with self.client:
            Uid = 1
            
            params = {
                "contract": "predictionHandshake",
                "eventName": "__init",
                "status": 1,
                "id": 1,
                "inputs": {
                    "offchain": "cryptosign_m{}".format(handshake_id),
                    "hid": 88
                }
            }

            response = self.client.post(
                                    '/event',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)
            db.session.close()

            h = Handshake.find_handshake_by_id(handshake_id)
            self.assertEqual(h.status, 0)

    def test_reiceive_init_event_with_status_2(self):
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
                status=-1
        )
        db.session.add(handshake)
        db.session.commit()
        handshake_id = handshake.id

        tx = Tx(
            offchain='cryptosign_m{}'.format(handshake_id)
        )
        db.session.add(tx)
        db.session.commit()

        with self.client:
            Uid = 1
            
            params = {
                "contract": "predictionHandshake",
                "methodName": "init",
                "status": 2,
                "id": tx.id,
                "inputs": {
                }
            }

            response = self.client.post(
                                    '/event',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)
            db.session.close()

            h = Handshake.find_handshake_by_id(handshake_id)
            self.assertEqual(h.status, -10)

    def test_reiceive_uninit_event(self):
        self.clear_data_before_test()
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
				side=1,
				remaining_amount=1,
				from_address='0x123',
                status=0,
                bk_status=0
        )
        db.session.add(handshake)
        db.session.commit()

        with self.client:
            Uid = 1
            
            params = {
                "contract": "predictionHandshake",
                "eventName": "__uninit",
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_m{}".format(handshake.id),
                    "hid": 88
                }
                
            }

            response = self.client.post(
                                    '/event',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

            h = Handshake.find_handshake_by_id(handshake.id)
            self.assertEqual(h.status, 1)


    def test_reiceive_create_maket_event(self):
        self.clear_data_before_test()
        # -----
        outcome = Outcome.find_outcome_by_id(22)
        if outcome is not None:
            db.session.delete(outcome)
            db.session.commit()

        outcome = Outcome(
            id=22,
            match_id=1
        )
        db.session.add(outcome)
        db.session.commit()

        with self.client:
            Uid = 1
            
            params = {
                "contract": "predictionHandshake",
                "eventName": "__createMarket",
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_createMarket{}".format(22),
                    "hid": 88
                }
            }

            response = self.client.post(
                                    '/event',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

            outcome = Outcome.find_outcome_by_id(22)
            self.assertEqual(outcome.hid, 88)


    def test_reiceive_collect_event_for_shaker(self):
        self.clear_data_before_test()
        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=33,
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
        shaker = Shaker(
					shaker_id=33,
					amount=0.2,
					currency='ETH',
					odds=6,
					side=1,
					handshake_id=handshake.id,
					from_address='0x123',
					chain_id=4,
                    status=2
				)
        db.session.add(shaker)
        db.session.commit()


        outcome = Outcome.find_outcome_by_id(88)
        outcome.result = 1

        match = Match.find_match_by_id(outcome.match_id)
        match.date = time.time() - 18600
        db.session.commit()

        with self.client:
            Uid = 66
            params = {
                "contract": "predictionHandshake",
                "eventName": "__collect",
                "status": 1,
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_s{}".format(shaker.id),
                    "hid": 88
                }
            }

            response = self.client.post(
                                    '/event',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

            hs = Handshake.find_handshake_by_id(handshake.id)
            s = Shaker.find_shaker_by_id(shaker.id)
            self.assertEqual(hs.status, 6)
            self.assertEqual(s.status, 6)

    def test_reiceive_collect_event_for_maker(self):
        self.clear_data_before_test()
        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=22,
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
        shaker = Shaker(
					shaker_id=22,
					amount=0.2,
					currency='ETH',
					odds=6,
					side=1,
					handshake_id=handshake.id,
					from_address='0x123',
					chain_id=4,
                    status=2
				)
        db.session.add(shaker)
        db.session.commit()


        outcome = Outcome.find_outcome_by_id(88)
        outcome.result = 2

        match = Match.find_match_by_id(outcome.match_id)
        match.date = time.time() - 18600
        db.session.commit()

        with self.client:
            Uid = 22
            params = {
                "contract": "predictionHandshake",
                "eventName": "__collect",
                "status": 1,
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_m{}".format(handshake.id),
                    "hid": 88
                }
            }

            response = self.client.post(
                                    '/event',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

            hs = Handshake.find_handshake_by_id(handshake.id)
            s = Shaker.find_shaker_by_id(shaker.id)

            self.assertEqual(hs.status, 6)
            self.assertEqual(s.status, 6)

    def test_reiceive_shake_event(self):
        self.clear_data_before_test()
        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=66,
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
        shaker = Shaker(
					shaker_id=66,
					amount=0.2,
					currency='ETH',
					odds=6,
					side=1,
					handshake_id=handshake.id,
					from_address='0x123',
					chain_id=4,
                    status=-1
				)
        db.session.add(shaker)
        db.session.commit()

        shaker_id = shaker.id

        with self.client:
            Uid = 1
            
            params = {
                "contract": "predictionHandshake",
                "eventName": "__shake",
                "status": 1,
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_s{}".format(shaker_id),
                    "hid": 88
                }   
            }

            response = self.client.post(
                                    '/event',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)
            db.session.close()

            s = Shaker.find_shaker_by_id(shaker_id)
            self.assertEqual(s.status, 2)

    def test_reiceive_refund_event(self):
        self.clear_data_before_test()
        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=66,
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
        handshake_id = handshake.id

        handshake_uninited = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=66,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=1,
				from_address='0x123',
                status=HandshakeStatus['STATUS_MAKER_UNINITED']
        )
        db.session.add(handshake_uninited)
        db.session.commit()
        handshake_uninited_id = handshake_uninited.id

        handshake_uninit_failed = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=66,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=1,
				from_address='0x123',
                status=HandshakeStatus['STATUS_MAKER_UNINIT_FAILED']
        )
        db.session.add(handshake_uninit_failed)
        db.session.commit()
        handshake_uninit_failed_id = handshake_uninit_failed.id
        # -----
        shaker = Shaker(
					shaker_id=66,
					amount=0.2,
					currency='ETH',
					odds=6,
					side=1,
					handshake_id=handshake.id,
					from_address='0x123',
					chain_id=4,
                    status=-1
				)
        db.session.add(shaker)
        db.session.commit()

        shaker_uninited = Shaker(
                shaker_id=66,
                amount=0.2,
                currency='ETH',
                odds=6,
                side=1,
                handshake_id=handshake_uninited.id,
                from_address='0x123',
                chain_id=4,
                status=HandshakeStatus['STATUS_MAKER_UNINITED']
        )
        db.session.add(shaker_uninited)
        db.session.commit()
        shaker_uninited_id = shaker_uninited.id

        shaker_uninit_failed = Shaker(
                shaker_id=66,
                amount=0.2,
                currency='ETH',
                odds=6,
                side=1,
                handshake_id=handshake_uninited.id,
                from_address='0x123',
                chain_id=4,
                status=HandshakeStatus['STATUS_MAKER_UNINIT_FAILED']
        )
        db.session.add(shaker_uninit_failed)

        db.session.commit()
        shaker_id = shaker.id
        shaker_uninit_failed_id = shaker_uninit_failed.id

        with self.client:
            Uid = 1
            
            params = {
                "contract": "predictionHandshake",
                "eventName": "__refund",
                "status": 1,
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_s{}".format(shaker_id),
                    "hid": 88
                }   
            }

            response = self.client.post(
                                    '/event',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)
            db.session.close()

            s = Shaker.find_shaker_by_id(shaker_id)
            self.assertEqual(s.status, HandshakeStatus['STATUS_REFUNDED'])
            h = Handshake.find_handshake_by_id(handshake_id)
            self.assertEqual(h.status, HandshakeStatus['STATUS_REFUNDED'])

            shaker_uninit_failed_=Shaker.find_shaker_by_id(shaker_uninit_failed_id)
            self.assertEqual(shaker_uninit_failed_.status, HandshakeStatus['STATUS_MAKER_UNINIT_FAILED'])

            shaker_uninited=Shaker.find_shaker_by_id(shaker_uninited_id)
            self.assertEqual(shaker_uninited.status, HandshakeStatus['STATUS_MAKER_UNINITED'])

            handshake_uninit_failed=Handshake.find_handshake_by_id(handshake_uninit_failed_id)
            self.assertEqual(handshake_uninit_failed.status, HandshakeStatus['STATUS_MAKER_UNINIT_FAILED'])

            handshake_uninited=Handshake.find_handshake_by_id(handshake_uninited_id)
            self.assertEqual(handshake_uninited.status, HandshakeStatus['STATUS_MAKER_UNINITED'])


    def test_reiceive_shake_event_with_status_0(self):
        self.clear_data_before_test()
        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=66,
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
        handshake_id = handshake.id

        # -----
        shaker = Shaker(
					shaker_id=66,
					amount=0.2,
					currency='ETH',
					odds=6,
					side=1,
					handshake_id=handshake.id,
					from_address='0x123',
					chain_id=4,
                    status=-1
				)
        db.session.add(shaker)
        db.session.commit()

        shaker_id = shaker.id

        with self.client:
            Uid = 1
            
            params = {
                "contract": "predictionHandshake",
                "methodName": "shake",
                "status": 0,
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_s{}".format(shaker_id),
                    "hid": 88
                }   
            }

            response = self.client.post(
                                    '/event',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)
            db.session.close()

            s = Shaker.find_shaker_by_id(shaker_id)
            self.assertEqual(s.status, HandshakeStatus['STATUS_SHAKE_FAILED'])

            h = Handshake.find_handshake_by_id(handshake_id)
            self.assertEqual(float(h.remaining_amount), 1)


    def test_reiceive_report_event_with_status_0(self):
        self.clear_data_before_test()
        outcome = Outcome.find_outcome_by_hid(88)
        outcome.result = -2
        db.session.commit()

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
				side=1,
				remaining_amount=1,
				from_address='0x123',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()

        with self.client:
            Uid = 1
            
            params = {
                "contract": "predictionHandshake",
                "methodName": "report",
                "status": 0,
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_report1",
                    "hid": 88    
                }   
            }

            response = self.client.post(
                                    '/event',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

        hs = Handshake.find_handshake_by_id(handshake.id)
        self.assertEqual(hs.status, 0)

        outcome = Outcome.find_outcome_by_hid(88)
        self.assertEqual(outcome.result, -1)

    def test_reiceive_report_event_with_status_2(self):
        self.clear_data_before_test()
        outcome = Outcome.find_outcome_by_hid(88)
        outcome.result = -2
        db.session.commit()

        # -----
        payload = {
                    "gasPrice": "0x4a817c800",
                    "gasLimit": 350000,
                    "to": "0x44c7370b355d5808b07e1ee757581610b7d9c5ca",
                    "from": "0x3d00536dc2869cc7ee11c45f2fcc86c0336bffed",
                    "nonce": "0x62e",
                    "chainId": 1,
                    "data": "0xda676f200000000000000000000000000000000000000000000000000000000000000015000000000000000000000000000000000000000000000000000000000000000263727970746f7369676e5f7265706f7274320000000000000000000000000000",
                    "_options": {
                        "onchainData": {
                            "contract_method": "reportOutcomeTransaction",
                            "hid": 88,
                            "outcome_result": 2,
                            "offchain": "cryptosign_report2"
                        },
                        "task": {
                            "id": 328,
                            "task_type": "REAL_BET",
                            "action": "REPORT",
                            "data": "{\"offchain\": \"cryptosign_report2\", \"hid\": 88, \"outcome_result\": 2}",
                            "status": -3
                        }
                    }
                }
        tx = Tx(
            payload=json.dumps(payload)
        )
        db.session.add(tx)
        db.session.commit()

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
				side=1,
				remaining_amount=1,
				from_address='0x123',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()

        with self.client:
            Uid = 1
            params = {
                "contract": "predictionHandshake",
                "methodName": "report",
                "status": 2,
                'id': tx.id,
                "inputs": {
                }   
            }

            response = self.client.post(
                                    '/event',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

        hs = Handshake.find_handshake_by_id(handshake.id)
        self.assertEqual(hs.status, 0)

        outcome = Outcome.find_outcome_by_hid(88)
        self.assertEqual(outcome.result, -1)

    def test_reiceive_report_event(self):
        self.clear_data_before_test()
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
				side=1,
				remaining_amount=1,
				from_address='0x123',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()

        with self.client:
            Uid = 1
            
            params = {
                "contract": "predictionHandshake",
                "eventName": "__report",
                "status": 1,
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_report1",
                    "hid": 88    
                }   
            }

            response = self.client.post(
                                    '/event',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

        hs = Handshake.find_handshake_by_id(handshake.id)
        self.assertEqual(hs.status, 0)

        outcome = Outcome.find_outcome_by_hid(88)
        self.assertEqual(outcome.result, 1)

    def test_reiceive_report_event_with_status_2(self):
        self.clear_data_before_test()
        outcome = Outcome.find_outcome_by_hid(88)
        outcome.result = -2
        db.session.commit()

        # -----
        payload = {
                    "gasPrice": "0x4a817c800",
                    "gasLimit": 350000,
                    "to": "0x44c7370b355d5808b07e1ee757581610b7d9c5ca",
                    "from": "0x3d00536dc2869cc7ee11c45f2fcc86c0336bffed",
                    "nonce": "0x62e",
                    "chainId": 1,
                    "data": "0xda676f200000000000000000000000000000000000000000000000000000000000000015000000000000000000000000000000000000000000000000000000000000000263727970746f7369676e5f7265706f7274320000000000000000000000000000",
                    "_options": {
                        "onchainData": {
                            "contract_method": "reportOutcomeTransaction",
                            "hid": 88,
                            "outcome_result": 2,
                            "offchain": "cryptosign_report2"
                        },
                        "task": {
                            "id": 328,
                            "task_type": "REAL_BET",
                            "action": "REPORT",
                            "data": "{\"offchain\": \"cryptosign_report2\", \"hid\": 88, \"outcome_result\": 2}",
                            "status": -3
                        }
                    }
                }
        tx = Tx(
            payload=json.dumps(payload)
        )
        db.session.add(tx)
        db.session.commit()

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
				side=1,
				remaining_amount=1,
				from_address='0x123',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()

        with self.client:
            Uid = 1
            params = {
                "contract": "predictionHandshake",
                "methodName": "report",
                "status": 2,
                'id': tx.id,
                "inputs": {
                }   
            }

            response = self.client.post(
                                    '/event',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

        hs = Handshake.find_handshake_by_id(handshake.id)
        self.assertEqual(hs.status, 0)

        outcome = Outcome.find_outcome_by_hid(88)
        self.assertEqual(outcome.result, -1)

    def test_reiceive_report_event(self):
        self.clear_data_before_test()
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
				side=1,
				remaining_amount=1,
				from_address='0x123',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()

        with self.client:
            Uid = 1
            
            params = {
                "contract": "predictionHandshake",
                "eventName": "__report",
                "status": 1,
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_report1",
                    "hid": 88    
                }   
            }

            response = self.client.post(
                                    '/event',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

        hs = Handshake.find_handshake_by_id(handshake.id)
        self.assertEqual(hs.status, 0)

        outcome = Outcome.find_outcome_by_hid(88)
        self.assertEqual(outcome.result, 1)
    
    def test_reiceive_dispute_event_with_state_0 (self):
        self.clear_data_before_test()

        with self.client:
            Uid = 1
            
            params = {
                "contract": "predictionHandshake",
                "eventName": "__dispute",
                "status": 1,
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_s1",
                    "hid": 88,
                    "state": 0
                }   
            }

            response = self.client.post(
                                    '/event',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)

    def test_reiceive_dispute_event_with_state_1 (self):
        self.clear_data_before_test()

        with self.client:
            Uid = 1
            
            params = {
                "contract": "predictionHandshake",
                "eventName": "__dispute",
                "status": 1,
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_s1",
                    "hid": 88,
                    "state": 1
                }   
            }

            response = self.client.post(
                                    '/event',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)

    def test_reiceive_dispute_event_with_state_2_maker (self):
        self.clear_data_before_test()
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
				side=1,
				remaining_amount=1,
				from_address='0x12345',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()
        shaker = Shaker(
				hs_type=3,
				chain_id=4,
				is_private=0,
				user_id=99,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=1,
				remaining_amount=1,
				from_address='0x1234',
                status=0,
                handshake_id=handshake.id
        )
        db.session.add(shaker)
        db.session.commit()

        with self.client:
            Uid = 1
            
            params = {
                "contract": "predictionHandshake",
                "eventName": "__dispute",
                "status": 1,
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_s{}".format(shaker.id),
                    "hid": 88,
                    "state": 2
                }   
            }

            response = self.client.post(
                                    '/event',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            print data
            self.assertTrue(data['status'] == 1)

        hs = Shaker.find_shaker_by_id(shaker.id)
        print hs
        print hs.status
        self.assertEqual(hs.status, HandshakeStatus['STATUS_USER_DISPUTED'])

        outcome = Outcome.find_outcome_by_hid(88)
        self.assertNotEqual(outcome.result, CONST.RESULT_TYPE['DISPUTED'])


    def test_reiceive_dispute_event_with_state_2_shaker (self):
        self.clear_data_before_test()
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
				side=1,
				remaining_amount=1,
				from_address='0x12345',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()

        with self.client:
            Uid = 1
            
            params = {
                "contract": "predictionHandshake",
                "eventName": "__dispute",
                "status": 1,
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_m{}".format(handshake.id),
                    "hid": 88,
                    "state": 2
                }   
            }

            response = self.client.post(
                                    '/event',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

        hs = Handshake.find_handshake_by_id(handshake.id)
        self.assertEqual(hs.status, HandshakeStatus['STATUS_USER_DISPUTED'])

        outcome = Outcome.find_outcome_by_hid(88)
        self.assertNotEqual(outcome.result, CONST.RESULT_TYPE['DISPUTED'])

    def test_reiceive_dispute_event_with_state_3_shaker (self):
        self.clear_data_before_test()
        # -----
        outcome = Outcome.find_outcome_by_id(100)
        if outcome is not None:
            outcome.result = -1
            db.session.commit()
        else:
            outcome = Outcome(
                id=100,
                match_id=1,
                hid=100
            )
            db.session.add(outcome)
            db.session.commit()
        
        # -----
        handshake_ = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=99,
				outcome_id=100,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=1,
				remaining_amount=1,
				from_address='0x12345',
                status=HandshakeStatus['STATUS_USER_DISPUTED']
        )
        db.session.add(handshake_)
        db.session.commit()

        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=99,
				outcome_id=100,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=1,
				remaining_amount=1,
				from_address='0x12345',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()

        with self.client:
            Uid = 1
            
            params = {
                "contract": "predictionHandshake",
                "eventName": "__dispute",
                "status": 1,
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_m{}".format(handshake.id),
                    "hid": 100,
                    "state": 3
                }   
            }

            response = self.client.post(
                                    '/event',
                                    data=json.dumps(params),
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)
        
        handshakes = db.session.query(Handshake).filter(Handshake.outcome_id==100).all()
        for hs in handshakes:
            self.assertEqual(hs.status, HandshakeStatus['STATUS_DISPUTED'])
            shakers = db.session.query(Shaker).filter(Shaker.handshake_id==hs.id).all()
            for shaker in shakers:
                self.assertEqual(shaker.status, HandshakeStatus['STATUS_DISPUTED'])

        outcome = Outcome.find_outcome_by_id(100)
        self.assertEqual(outcome.result, CONST.RESULT_TYPE['DISPUTED'])

    def test_reiceive_dispute_event_with_state_3_maker (self):
        self.clear_data_before_test()
        # -----
        outcome = Outcome.find_outcome_by_id(100)
        if outcome is not None:
            outcome.result = -1
            db.session.commit()
        else:
            outcome = Outcome(
                id=100,
                match_id=1,
                hid=100
            )
            
            db.session.add(outcome)
            db.session.commit()
        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=33,
				outcome_id=100,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=1,
				from_address='0x1233464576',
                status=-1
        )
        db.session.add(handshake)
        db.session.commit()
        # -----
        shaker = Shaker(
					shaker_id=33,
					amount=0.2,
					currency='ETH',
					odds=6,
					side=1,
					handshake_id=handshake.id,
					from_address='0x1235678',
					chain_id=4,
                    status=2
				)
        db.session.add(shaker)
        db.session.commit()

        with self.client:
            Uid = 1
            
            params = {
                "contract": "predictionHandshake",
                "eventName": "__dispute",
                "status": 1,
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_s{}".format(shaker.id),
                    "hid": 100,
                    "state": 3
                }   
            }

            response = self.client.post(
                                    '/event',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })
            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

        handshakes = db.session.query(Handshake).filter(Handshake.outcome_id==100).all()
        for hs in handshakes:
            self.assertEqual(hs.status, HandshakeStatus['STATUS_DISPUTED'])
            shakers = db.session.query(Shaker).filter(Shaker.handshake_id==hs.id).all()
            for shaker in shakers:
                self.assertEqual(shaker.status, HandshakeStatus['STATUS_DISPUTED'])

        hs = Shaker.find_shaker_by_id(shaker.id)
        self.assertEqual(hs.status, HandshakeStatus['STATUS_DISPUTED'])

        outcome = Outcome.find_outcome_by_id(100)
        self.assertEqual(outcome.result, CONST.RESULT_TYPE['DISPUTED'])

    def test_reiceive_resolve_event (self):
        self.clear_data_before_test()
        # -----
        result_report = 1
        outcome = Outcome.find_outcome_by_id(100)
        if outcome is not None:
            outcome.result = -3
            db.session.commit()
        else:
            outcome = Outcome(
                id=100,
                match_id=1,
                hid=100,
                result=-3,
                total_dispute_amount=1
            )
            
            db.session.add(outcome)
            db.session.commit()
        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=33,
				outcome_id=100,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=1,
				from_address='0x1233464576',
                status=4
        )
        db.session.add(handshake)
        db.session.commit()
        # -----
        shaker = Shaker(
					shaker_id=33,
					amount=0.2,
					currency='ETH',
					odds=6,
					side=1,
					handshake_id=handshake.id,
					from_address='0x1235678',
					chain_id=4,
                    status=4
				)
        db.session.add(shaker)
        db.session.commit()

        with self.client:
            Uid = 1
            
            params = {
                "contract": "predictionHandshake",
                "eventName": "__resolve",
                "status": 1,
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_report{}".format(result_report),
                    "hid": 100
                }   
            }

            response = self.client.post(
                                    '/event',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })
            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

        handshakes = db.session.query(Handshake).filter(Handshake.outcome_id==100).all()
        for hs in handshakes:
            self.assertEqual(hs.status, HandshakeStatus['STATUS_RESOLVED'])
            shakers = db.session.query(Shaker).filter(Shaker.handshake_id==hs.id).all()
            for shaker in shakers:
                self.assertEqual(shaker.status, HandshakeStatus['STATUS_RESOLVED'])

        outcome = Outcome.find_outcome_by_id(100)
        self.assertEqual(outcome.total_dispute_amount, 0)
        self.assertEqual(outcome.result, result_report)

    def test_reiceive_resolve_event_result_invalid (self):
        self.clear_data_before_test()
        # -----
        result_report = -1
        outcome = Outcome.find_outcome_by_id(100)
        if outcome is not None:
            outcome.result = -3
            db.session.commit()
        else:
            outcome = Outcome(
                id=100,
                match_id=1,
                hid=100,
                result=-3,
                total_dispute_amount=1
            )
            
            db.session.add(outcome)
            db.session.commit()
        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				is_private=1,
				user_id=33,
				outcome_id=100,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=1,
				from_address='0x1233464576',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()
        # -----
        shaker = Shaker(
					shaker_id=33,
					amount=0.2,
					currency='ETH',
					odds=6,
					side=1,
					handshake_id=handshake.id,
					from_address='0x1235678',
					chain_id=4,
                    status=0
				)
        db.session.add(shaker)
        db.session.commit()

        handshakes = db.session.query(Handshake).filter(Handshake.outcome_id==100).all()
        for hs in handshakes:
            hs.status = HandshakeStatus['STATUS_DISPUTED']
            shakers = db.session.query(Shaker).filter(Shaker.handshake_id==hs.id).all()
            for shaker in shakers:
                shaker.status = HandshakeStatus['STATUS_DISPUTED']
        db.session.commit()
        with self.client:
            Uid = 1
            
            params = {
                "contract": "predictionHandshake",
                "eventName": "__resolve",
                "status": 1,
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_report{}".format(result_report),
                    "hid": 100
                }   
            }

            response = self.client.post(
                                    '/event',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)

        handshakes = db.session.query(Handshake).filter(Handshake.outcome_id==100).all()
        for hs in handshakes:
            self.assertNotEqual(hs.status, HandshakeStatus['STATUS_RESOLVED'])
            shakers = db.session.query(Shaker).filter(Shaker.handshake_id==hs.id).all()
            for shaker in shakers:
                self.assertNotEqual(shaker.status, HandshakeStatus['STATUS_RESOLVED'])

        outcome = Outcome.find_outcome_by_id(100)
        self.assertNotEqual(outcome.result, result_report)

if __name__ == '__main__':
    unittest.main()