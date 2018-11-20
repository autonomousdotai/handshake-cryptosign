from tests.routes.base import BaseTestCase
from mock import patch
from app.models import Shaker, Handshake, Outcome, Shaker, User, Match, Tx, Contract
from app import db, app
from app.helpers.message import MESSAGE
from app.constants import Handshake as HandshakeStatus
from sqlalchemy import or_

import mock
import json
import time
import app.bl.user as user_bl
import app.constants as CONST

class TestEventBluePrint(BaseTestCase):

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
                hid=88,
                contract_id=contract.id
            )
            db.session.add(outcome)
            db.session.commit()
        else:
            outcome.match_id = 1
            outcome.result = -1
            db.session.commit()

        outcome = Outcome.find_outcome_by_id(100)
        if outcome is None:
            outcome = Outcome(
                id=100,
                match_id=1,
                hid=100
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

        outcome = Outcome.find_outcome_by_id(100)
        if outcome is not None:
            outcome.result = -1
            db.session.commit()

        handshakes = db.session.query(Handshake).filter(or_(Handshake.outcome_id==88, Handshake.outcome_id==100)).all()
        for handshake in handshakes:
            db.session.delete(handshake)
            db.session.commit()

    def test_reiceive_init_event(self):
        self.clear_data_before_test()
        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
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
                "contract": app.config.get("PREDICTION_JSON"),
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
                "contract": app.config.get("PREDICTION_JSON"),
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
                "contract": app.config.get("PREDICTION_JSON"),
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
                "contract": app.config.get("PREDICTION_JSON"),
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
        if match is not None:
            match.date=time.time() - 18600
            db.session.flush()
        else:
            match = Match(
                id=outcome.match_id,
                date=time.time() - 18600
            )
            db.session.add(match)
        db.session.commit()

        with self.client:
            Uid = 66
            params = {
                "contract": app.config.get("PREDICTION_JSON"),
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
        if match is not None:
            match.date=time.time() - 18600
            db.session.flush()
        else:
            match = Match(
                id=outcome.match_id,
                date=time.time() - 18600
            )
            db.session.add(match)
        db.session.commit()


        with self.client:
            Uid = 22
            params = {
                "contract": app.config.get("PREDICTION_JSON"),
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
                "contract": app.config.get("PREDICTION_JSON"),
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
        arr_hs = []
        arr_sk = []
        # -----
        handshake1 = Handshake(
						hs_type=3,
						chain_id=4,
						user_id=66,
						outcome_id=88,
						odds=1.5,
						amount=1,
						currency='ETH',
						side=2,
						remaining_amount=0,
						from_address='0x123',
						status=HandshakeStatus['STATUS_REFUND_PENDING']
					)
        db.session.add(handshake1)
        db.session.commit()
        arr_hs.append(handshake1)

        handshake2 = Handshake(
						hs_type=3,
						chain_id=4,
						user_id=66,
						outcome_id=88,
						odds=1.5,
						amount=1,
						currency='ETH',
						side=2,
						remaining_amount=0,
						from_address='0x123',
						status=HandshakeStatus['STATUS_MAKER_UNINITED']
					)
        db.session.add(handshake2)
        db.session.commit()
        arr_hs.append(handshake2)

        handshake3 = Handshake(
						hs_type=3,
						chain_id=4,
						user_id=66,
						outcome_id=88,
						odds=1.5,
						amount=1,
						currency='ETH',
						side=2,
						remaining_amount=0,
						from_address='0x123',
						status=HandshakeStatus['STATUS_INITED']
					)
        db.session.add(handshake3)
        db.session.commit()
        arr_hs.append(handshake3)        

        handshake_uninited = Handshake(
				hs_type=3,
				chain_id=4,
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
        arr_hs.append(handshake_uninited)

        handshake_uninit_failed = Handshake(
				hs_type=3,
				chain_id=4,
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
        arr_hs.append(handshake_uninit_failed)
        # -----
        shaker1 = Shaker(
					shaker_id=66,
					amount=0.2,
					currency='ETH',
					odds=6,
					side=1,
					handshake_id=handshake1.id,
					from_address='0x123',
					chain_id=4,
					status=HandshakeStatus['STATUS_REFUND_PENDING']
				)
        db.session.add(shaker1)
        db.session.commit()
        arr_sk.append(shaker1)
		# -----
        shaker2 = Shaker(
					shaker_id=66,
					amount=0.2,
					currency='ETH',
					odds=6,
					side=1,
					handshake_id=handshake1.id,
					from_address='0x123',
					chain_id=4,
					status=HandshakeStatus['STATUS_REFUND_PENDING']
				)
        db.session.add(shaker2)
        db.session.commit()
        arr_sk.append(shaker2)
        # -----
        shaker = Shaker(
					shaker_id=66,
					amount=0.2,
					currency='ETH',
					odds=6,
					side=1,
					handshake_id=handshake3.id,
					from_address='0x123',
					chain_id=4,
                    status=-1
				)
        db.session.add(shaker)
        db.session.commit()
        shaker_id = shaker.id
        arr_sk.append(shaker)

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
        arr_sk.append(shaker_uninited)

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
        shaker_uninit_failed_id = shaker_uninit_failed.id
        arr_sk.append(shaker_uninit_failed)

        with self.client:
            Uid = 1
            
            params = {
                "contract": app.config.get("PREDICTION_JSON"),
                "eventName": "__refund",
                "status": 1,
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_s{}".format(shaker2.id),
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

            hs1 = Handshake.find_handshake_by_id(handshake1.id)
            self.assertEqual(hs1.status, HandshakeStatus['STATUS_REFUNDED'])
            hs2 = Handshake.find_handshake_by_id(handshake2.id)
            self.assertEqual(hs2.status, HandshakeStatus['STATUS_MAKER_UNINITED'])
            hs3 = Handshake.find_handshake_by_id(handshake3.id)
            self.assertEqual(hs3.status, HandshakeStatus['STATUS_REFUNDED'])

            sk1 = Shaker.find_shaker_by_id(shaker1.id)
            self.assertEqual(sk1.status, HandshakeStatus['STATUS_REFUNDED'])
            sk2 = Shaker.find_shaker_by_id(shaker2.id)
            self.assertEqual(sk2.status, HandshakeStatus['STATUS_REFUNDED'])

            s = Shaker.find_shaker_by_id(shaker_id)
            self.assertEqual(s.status, HandshakeStatus['STATUS_PENDING'])

            shaker_uninit_failed_=Shaker.find_shaker_by_id(shaker_uninit_failed_id)
            self.assertEqual(shaker_uninit_failed_.status, HandshakeStatus['STATUS_MAKER_UNINIT_FAILED'])

            shaker_uninited=Shaker.find_shaker_by_id(shaker_uninited_id)
            self.assertEqual(shaker_uninited.status, HandshakeStatus['STATUS_MAKER_UNINITED'])

            handshake_uninit_failed=Handshake.find_handshake_by_id(handshake_uninit_failed_id)
            self.assertEqual(handshake_uninit_failed.status, HandshakeStatus['STATUS_MAKER_UNINIT_FAILED'])

            handshake_uninited=Handshake.find_handshake_by_id(handshake_uninited_id)
            self.assertEqual(handshake_uninited.status, HandshakeStatus['STATUS_MAKER_UNINITED'])
            
            for item in arr_hs:
                db.session.delete(item)
                db.session.commit()
            for item in arr_sk:
                db.session.delete(item)
                db.session.commit()
            db.session.close()

    def test_reiceive_shake_event_with_status_0(self):
        self.clear_data_before_test()
        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
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
                "contract": app.config.get("PREDICTION_JSON"),
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
                "contract": app.config.get("PREDICTION_JSON"),
                "methodName": "report",
                "status": 0,
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_report{}_1".format(outcome.id),
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

        outcome = Outcome.find_outcome_by_id(outcome.id)
        self.assertEqual(outcome.result, CONST.RESULT_TYPE['REPORT_FAILED'])

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
                            "outcome_id": outcome.id,
                            "offchain": "cryptosign_report{}_2".format(outcome.id)
                        },
                        "task": {
                            "id": 328,
                            "task_type": "REAL_BET",
                            "action": "REPORT",
                            "data": "{\"offchain\": \"cryptosign_report{}_2\", \"hid\": 88, \"outcome_result\": 2}".format(outcome.id),
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
                "contract": app.config.get("PREDICTION_JSON"),
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
                "contract": app.config.get("PREDICTION_JSON"),
                "eventName": "__report",
                "status": 1,
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_report{}_1".format(88),
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
        self.assertEqual(hs.status, HandshakeStatus['STATUS_MAKER_SHOULD_UNINIT'])

        outcome = Outcome.find_outcome_by_id(88)
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
                            "outcome_id": outcome.id,
                            "offchain": "cryptosign_report{}_2".format(outcome.id)
                        },
                        "task": {
                            "id": 328,
                            "task_type": "REAL_BET",
                            "action": "REPORT",
                            "data": '{"offchain": "cryptosign_report' + str(outcome.id) + '_2", "hid": 88, "outcome_result": 2}',
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
                "contract": app.config.get("PREDICTION_JSON"),
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
        self.assertEqual(outcome.result, CONST.RESULT_TYPE['REPORT_FAILED'])

    def test_reiceive_report_event_with_not_shaker(self):
        self.clear_data_before_test()
        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
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
                "contract": app.config.get("PREDICTION_JSON"),
                "eventName": "__report",
                "status": 1,
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_report{}_1".format(88),
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
        self.assertEqual(hs.status, HandshakeStatus['STATUS_MAKER_SHOULD_UNINIT'])

        outcome = Outcome.find_outcome_by_id(88)
        self.assertEqual(outcome.result, 1)
    
    def test_reiceive_report_event_with_shaker(self):
        self.clear_data_before_test()
        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=99,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=1,
				remaining_amount=1,
				from_address='0x123',
                status=2
        )
        db.session.add(handshake)
        db.session.commit()

        shaker = Shaker(
				hs_type=3,
				chain_id=4,
				shaker_id=88,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=1,
				from_address='0x1234',
                status=2,
                handshake_id=handshake.id
        )
        db.session.add(shaker)
        db.session.commit()

        with self.client:
            Uid = 1
            
            params = {
                "contract": app.config.get("PREDICTION_JSON"),
                "eventName": "__report",
                "status": 1,
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_report{}_1".format(88),
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
        self.assertEqual(hs.status, HandshakeStatus['STATUS_SHAKER_SHAKED'])

        outcome = Outcome.find_outcome_by_id(88)
        self.assertEqual(outcome.result, 1)

    def test_reiceive_dispute_event_with_state_0 (self):
        self.clear_data_before_test()

        with self.client:
            Uid = 1
            
            params = {
                "contract": app.config.get("PREDICTION_JSON"),
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
                "contract": app.config.get("PREDICTION_JSON"),
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

    # Dispute all makers were same user_id, outcome_id, side
    # This case: STATUS_USER_DISPUTED
    def test_reiceive_dispute_event_with_state_2 (self):
        self.clear_data_before_test()
        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=99,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=1,
                shake_count=1,
				remaining_amount=1,
				from_address='0x12345',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()

        handshake1 = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=99,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=2,
                shake_count=1,
				remaining_amount=1,
				from_address='0x12345',
                status=0
        )
        db.session.add(handshake1)
        db.session.commit()

        handshake2 = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=99,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=2,
                shake_count=1,
				remaining_amount=1,
				from_address='0x12345',
                status=0
        )
        db.session.add(handshake2)
        db.session.commit()

        shaker = Shaker(
				hs_type=3,
				chain_id=4,
				shaker_id=88,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=1,
				from_address='0x1234',
                status=0,
                handshake_id=handshake.id
        )
        db.session.add(shaker)
        db.session.commit()

        shaker2 = Shaker(
				hs_type=3,
				chain_id=4,
				shaker_id=88,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=1,
				remaining_amount=1,
				from_address='not change',
                status=0,
                handshake_id=handshake.id
        )
        db.session.add(shaker2)
        db.session.commit()

        shaker3 = Shaker(
				hs_type=3,
				chain_id=4,
				shaker_id=99,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=1,
				from_address='not change',
                status=0,
                handshake_id=handshake.id
        )
        db.session.add(shaker3)
        db.session.commit()

        with self.client:
            Uid = 1
            
            params = {
                "contract": app.config.get("PREDICTION_JSON"),
                "eventName": "__dispute",
                "status": 1,
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_m{}".format(handshake1.id),
                    "hid": 88,
                    "state": 2,
                    "outcome": 2
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
        self.assertEqual(hs.status, HandshakeStatus['STATUS_INITED'])

        s1 = Shaker.find_shaker_by_id(shaker.id)
        self.assertEqual(s1.status, HandshakeStatus['STATUS_INITED'])

        hs1 = Handshake.find_handshake_by_id(handshake1.id)
        self.assertEqual(hs1.status, HandshakeStatus['STATUS_USER_DISPUTED'])

        s2 = Shaker.find_shaker_by_id(shaker2.id)
        self.assertEqual(s2.status, HandshakeStatus['STATUS_INITED'])

        s3 = Shaker.find_shaker_by_id(shaker3.id)
        self.assertEqual(s3.status, HandshakeStatus['STATUS_USER_DISPUTED'])

        hs4 = Handshake.find_handshake_by_id(handshake2.id)
        self.assertEqual(hs4.status, HandshakeStatus['STATUS_USER_DISPUTED'])


    # Dispute all makers and shakers matched
    # Dont dispute all makers did not match
    def test_reiceive_dispute_event_with_state_3_shaker (self):
        self.clear_data_before_test()
        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=99,
				outcome_id=88,
				odds=1.2,
				amount=2,
				currency='ETH',
				side=1,
                shake_count=1,
				remaining_amount=1,
				from_address='0x12345',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()

        handshake1 = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=99,
				outcome_id=88,
				odds=2.2,
				amount=2,
				currency='ETH',
				side=1,
                shake_count=1,
				remaining_amount=1,
				from_address='0x12345',
                status=0
        )
        db.session.add(handshake1)
        db.session.commit()

        handshake2 = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=99,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=1,
                shake_count=0,
				remaining_amount=1,
				from_address='0x12345',
                status=0
        )
        db.session.add(handshake2)
        db.session.commit()

        shaker = Shaker(
				hs_type=3,
				chain_id=4,
				shaker_id=99,
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

        shaker1 = Shaker(
				hs_type=3,
				chain_id=4,
				shaker_id=99,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=1,
				remaining_amount=1,
				from_address='0x1234',
                status=0,
                handshake_id=handshake1.id
        )
        db.session.add(shaker1)
        db.session.commit()

        shaker2 = Shaker(
				hs_type=3,
				chain_id=4,
				shaker_id=100,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=1,
				remaining_amount=1,
				from_address='not change',
                status=0,
                handshake_id=handshake.id
        )
        db.session.add(shaker2)
        db.session.commit()

        with self.client:
            Uid = 1
            
            params = {
                "contract": app.config.get("PREDICTION_JSON"),
                "eventName": "__dispute",
                "status": 1,
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_s{}".format(shaker1.id),
                    "hid": 88,
                    "state": 3,
                    "outcome": 2
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
        self.assertEqual(hs.status, HandshakeStatus['STATUS_DISPUTED'])

        hs1 = Handshake.find_handshake_by_id(handshake1.id)
        self.assertEqual(hs1.status, HandshakeStatus['STATUS_DISPUTED'])

        hs2 = Handshake.find_handshake_by_id(handshake2.id)
        self.assertEqual(hs2.status, HandshakeStatus['STATUS_INITED'])

        s = Shaker.find_shaker_by_id(shaker.id)
        self.assertEqual(s.status, HandshakeStatus['STATUS_DISPUTED'])

        s1 = Shaker.find_shaker_by_id(shaker1.id)
        self.assertEqual(s1.status, HandshakeStatus['STATUS_DISPUTED'])

        s2 = Shaker.find_shaker_by_id(shaker2.id)
        self.assertEqual(s2.status, HandshakeStatus['STATUS_DISPUTED'])

        outcome = Outcome.find_outcome_by_id(88)
        self.assertEqual(outcome.result, CONST.RESULT_TYPE['DISPUTED'])

    # Dispute all makers and shakers matched
    # Dont dispute all makers did not match
    def test_reiceive_dispute_event_with_state_3_maker (self):
        self.clear_data_before_test()
        # -----
        handshake = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=99,
				outcome_id=88,
				odds=1.2,
				amount=2,
				currency='ETH',
				side=1,
                shake_count=1,
				remaining_amount=1,
				from_address='0x12345',
                status=0
        )
        db.session.add(handshake)
        db.session.commit()

        handshake1 = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=99,
				outcome_id=88,
				odds=2.2,
				amount=2,
				currency='ETH',
				side=1,
                shake_count=1,
				remaining_amount=1,
				from_address='0x12345',
                status=0
        )
        db.session.add(handshake1)
        db.session.commit()

        handshake2 = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=99,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=1,
                shake_count=0,
				remaining_amount=1,
				from_address='0x12345',
                status=0
        )
        db.session.add(handshake2)
        db.session.commit()

        shaker = Shaker(
				hs_type=3,
				chain_id=4,
				shaker_id=99,
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

        shaker1 = Shaker(
				hs_type=3,
				chain_id=4,
				shaker_id=99,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=1,
				remaining_amount=1,
				from_address='0x1234',
                status=0,
                handshake_id=handshake1.id
        )
        db.session.add(shaker1)
        db.session.commit()

        shaker2 = Shaker(
				hs_type=3,
				chain_id=4,
				shaker_id=100,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=1,
				remaining_amount=1,
				from_address='not change',
                status=0,
                handshake_id=handshake.id
        )
        db.session.add(shaker2)
        db.session.commit()

        with self.client:
            Uid = 1
            
            params = {
                "contract": app.config.get("PREDICTION_JSON"),
                "eventName": "__dispute",
                "status": 1,
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_s{}".format(shaker.id),
                    "hid": 88,
                    "state": 3,
                    "outcome": 2
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
        self.assertEqual(hs.status, HandshakeStatus['STATUS_DISPUTED'])

        hs1 = Handshake.find_handshake_by_id(handshake1.id)
        self.assertEqual(hs1.status, HandshakeStatus['STATUS_DISPUTED'])

        hs2 = Handshake.find_handshake_by_id(handshake2.id)
        self.assertEqual(hs2.status, HandshakeStatus['STATUS_INITED'])

        s = Shaker.find_shaker_by_id(shaker.id)
        self.assertEqual(s.status, HandshakeStatus['STATUS_DISPUTED'])

        s1 = Shaker.find_shaker_by_id(shaker1.id)
        self.assertEqual(s1.status, HandshakeStatus['STATUS_DISPUTED'])

        s2 = Shaker.find_shaker_by_id(shaker2.id)
        self.assertEqual(s2.status, HandshakeStatus['STATUS_DISPUTED'])

        outcome = Outcome.find_outcome_by_id(88)
        self.assertEqual(outcome.result, CONST.RESULT_TYPE['DISPUTED'])

    def test_reiceive_resolve_event (self):
        self.clear_data_before_test()
        # -----
        result_report = 1
        outcome = Outcome.find_outcome_by_id(100)
        if outcome is not None:
            outcome.result = -3
            outcome.hid=100
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
				user_id=33,
				outcome_id=outcome.id,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=1,
				from_address='0x1233464576',
                status=HandshakeStatus['STATUS_DISPUTED']
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
                    status=HandshakeStatus['STATUS_DISPUTED']
				)
        db.session.add(shaker)
        db.session.commit()

        with self.client:
            Uid = 1
            
            params = {
                "contract": app.config.get("PREDICTION_JSON"),
                "eventName": "__resolve",
                "status": 1,
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_resolve{}_{}".format(outcome.id, result_report),
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

        handshakes = db.session.query(Handshake).filter(Handshake.outcome_id==outcome.id).all()
        for hs in handshakes:
            self.assertEqual(hs.status, HandshakeStatus['STATUS_RESOLVED'])
            shakers = db.session.query(Shaker).filter(Shaker.handshake_id==hs.id).all()
            for shaker in shakers:
                self.assertEqual(shaker.status, HandshakeStatus['STATUS_RESOLVED'])

        outcome = Outcome.find_outcome_by_id(outcome.id)
        self.assertEqual(outcome.total_dispute_amount, 0)
        self.assertEqual(outcome.result, result_report)

    def test_reiceive_dispute_event_with_state_2_draw (self):
        self.clear_data_before_test()
        outcome = Outcome.find_outcome_by_id(88)
        outcome.total_amount = 0
        outcome.total_dispute_amount = 0
        db.session.commit()
        # -----
        handshake_user88_side1 = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=88,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=1,
                shake_count=1,
				remaining_amount=1,
				from_address='0x12345',
                status=0
        )
        db.session.add(handshake_user88_side1)
        db.session.commit()

        handshake_user88_side2 = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=88,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=2,
                shake_count=1,
				remaining_amount=1,
				from_address='0x12345',
                status=0
        )
        db.session.add(handshake_user88_side2)
        db.session.commit()

        handshake_user99 = Handshake(
				hs_type=3,
				chain_id=4,
				user_id=99,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=2,
                shake_count=1,
				remaining_amount=1,
				from_address='0x12345',
                status=0
        )
        db.session.add(handshake_user99)
        db.session.commit()

        shaker_user88_side2 = Shaker(
				hs_type=3,
				chain_id=4,
				shaker_id=88,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=2,
				remaining_amount=1,
				from_address='0x1234',
                status=0,
                handshake_id=handshake_user88_side1.id
        )
        db.session.add(shaker_user88_side2)
        db.session.commit()

        shaker_user88_shaked_user99_side1 = Shaker(
				hs_type=3,
				chain_id=4,
				shaker_id=88,
				outcome_id=88,
				odds=1.2,
				amount=1,
				currency='ETH',
				side=1,
				remaining_amount=1,
				from_address='not change',
                status=0,
                handshake_id=handshake_user99.id
        )
        db.session.add(shaker_user88_shaked_user99_side1)
        db.session.commit()

        with self.client:
            Uid = 1
            
            params = {
                "contract": app.config.get("PREDICTION_JSON"),
                "eventName": "__dispute",
                "status": 1,
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_m{}".format(handshake_user88_side1.id),
                    "hid": 88,
                    "state": 2,
                    "outcome": 3
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

        hs_user88_side1 = Handshake.find_handshake_by_id(handshake_user88_side1.id)
        self.assertEqual(hs_user88_side1.status, HandshakeStatus['STATUS_USER_DISPUTED'])

        hs_user88_side2 = Handshake.find_handshake_by_id(handshake_user88_side2.id)
        self.assertEqual(hs_user88_side2.status, HandshakeStatus['STATUS_USER_DISPUTED'])

        hs_user99 = Handshake.find_handshake_by_id(handshake_user99.id)
        self.assertEqual(hs_user99.status, HandshakeStatus['STATUS_INITED'])

        s_user88_side2 = Shaker.find_shaker_by_id(shaker_user88_side2.id)
        self.assertEqual(s_user88_side2.status, HandshakeStatus['STATUS_USER_DISPUTED'])

        s_user88_shaked_user99_side1 = Shaker.find_shaker_by_id(shaker_user88_shaked_user99_side1.id)
        self.assertEqual(s_user88_shaked_user99_side1.status, HandshakeStatus['STATUS_USER_DISPUTED'])

    def test_reiceive_resolve_event_with_status_0(self):
        self.clear_data_before_test()
        outcome = Outcome.find_outcome_by_hid(88)
        outcome.result = -3
        db.session.commit()

        with self.client:
            Uid = 1
            
            params = {
                "contract": app.config.get("PREDICTION_JSON"),
                "methodName": "resolve",
                "status": 0,
                'id': 1,
                "inputs": {
                    "offchain": "cryptosign_resolve{}_1".format(outcome.id),
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

        outcome = Outcome.find_outcome_by_id(outcome.id)
        self.assertEqual(outcome.result, CONST.RESULT_TYPE['REPORT_FAILED'])


    # def test_reiceive_resolve_event_result_invalid (self):
    #     self.clear_data_before_test()
    #     # -----
    #     result_report = -1
    #     outcome = Outcome.find_outcome_by_id(100)
    #     if outcome is not None:
    #         outcome.result = -3
    #         db.session.commit()
    #     else:
    #         outcome = Outcome(
    #             id=100,
    #             match_id=1,
    #             hid=100,
    #             result=-3,
    #             total_dispute_amount=1
    #         )
            
    #         db.session.add(outcome)
    #         db.session.commit()
    #     # -----
    #     handshake = Handshake(
	# 			hs_type=3,
	# 			chain_id=4,
	# 			user_id=33,
	# 			outcome_id=100,
	# 			odds=1.2,
	# 			amount=1,
	# 			currency='ETH',
	# 			side=2,
	# 			remaining_amount=1,
	# 			from_address='0x1233464576',
    #             status=0
    #     )
    #     db.session.add(handshake)
    #     db.session.commit()
    #     # -----
    #     shaker = Shaker(
	# 				shaker_id=33,
	# 				amount=0.2,
	# 				currency='ETH',
	# 				odds=6,
	# 				side=1,
	# 				handshake_id=handshake.id,
	# 				from_address='0x1235678',
	# 				chain_id=4,
    #                 status=0
	# 			)
    #     db.session.add(shaker)
    #     db.session.commit()

    #     handshakes = db.session.query(Handshake).filter(Handshake.outcome_id==100).all()
    #     for hs in handshakes:
    #         hs.status = HandshakeStatus['STATUS_DISPUTED']
    #         shakers = db.session.query(Shaker).filter(Shaker.handshake_id==hs.id).all()
    #         for shaker in shakers:
    #             shaker.status = HandshakeStatus['STATUS_DISPUTED']
    #     db.session.commit()
    #     with self.client:
    #         Uid = 1
            
    #         params = {
    #             "contract": app.config.get("PREDICTION_JSON"),
    #             "eventName": "__resolve",
    #             "status": 1,
    #             'id': 1,
    #             "inputs": {
    #                 "offchain": "cryptosign_report{}".format(result_report),
    #                 "hid": 100
    #             }   
    #         }

    #         response = self.client.post(
    #                                 '/event',
    #                                 data=json.dumps(params), 
    #                                 content_type='application/json',
    #                                 headers={
    #                                     "Uid": "{}".format(Uid),
    #                                     "Fcm-Token": "{}".format(123),
    #                                     "Payload": "{}".format(123),
    #                                 })
    #         data = json.loads(response.data.decode())
    #         self.assertTrue(data['status'] == 1)

    #     handshakes = db.session.query(Handshake).filter(Handshake.outcome_id==100).all()
    #     for hs in handshakes:
    #         self.assertNotEqual(hs.status, HandshakeStatus['STATUS_RESOLVED'])
    #         shakers = db.session.query(Shaker).filter(Shaker.handshake_id==hs.id).all()
    #         for shaker in shakers:
    #             self.assertNotEqual(shaker.status, HandshakeStatus['STATUS_RESOLVED'])

    #     outcome = Outcome.find_outcome_by_id(100)
    #     self.assertNotEqual(outcome.result, result_report)

if __name__ == '__main__':
    unittest.main()