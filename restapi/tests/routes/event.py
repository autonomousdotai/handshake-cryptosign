from tests.routes.base import BaseTestCase
from mock import patch
from app.models import Shaker, Handshake, Outcome, Shaker, User, Match
from app import db, app
from app.helpers.message import MESSAGE
from app.constants import Handshake as HandshakeStatus

import mock
import json
import time
import app.bl.user as user_bl

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

        handshakes = db.session.query(Handshake).filter(Handshake.outcome_id==88).all()
        for handshake in handshakes:
            db.session.delete(handshake)
            db.session.commit()

    def test_reiceive_init_event(self):
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
				remaining_amount=1,
				from_address='0x123',
                status=-1
        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        with self.client:
            Uid = 1
            
            params = {
                "events": {
                    "contract": "predictionHandshake",
                    "eventName": "__init",
                    "offchain": "m{}".format(handshake.id),
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
        self.assertEqual(h.status, 0)

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()

    def test_reiceive_uninit_event(self):
        pass

    def test_reiceive_create_maket_event(self):
        pass

    def test_reiceive_report_event(self):
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
				remaining_amount=1,
				from_address='0x123',
                status=0
        )
        arr_hs.append(handshake)
        db.session.add(handshake)
        db.session.commit()

        with self.client:
            Uid = 1
            
            params = {
                "events": {
                    "contract": "predictionHandshake",
                    "eventName": "__report",
                    "offchain": "report1",
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

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()
    
if __name__ == '__main__':
    unittest.main()