from tests.routes.base import BaseTestCase
from mock import patch
from app import db
from app.helpers.message import MESSAGE
from app.models import Handshake, User, Outcome, Match, Shaker, Task

import mock
import json
import time

class TestMatchBluePrint(BaseTestCase):

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
        else:
            outcome.result = -1
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

        handshakes = db.session.query(Handshake).filter(Handshake.outcome_id==88).all()
        for handshake in handshakes:
            db.session.delete(handshake)
            db.session.commit()

        Task.query.delete()
        db.session.commit()

    def test_get_match_with_public(self):
        with self.client:
            pass


    def test_get_match(self):
        self.clear_data_before_test()
        arr_hs = []

        # ----- 
        match = Match(
            id=10000
        )
        db.session.add(match)
        db.session.commit()
        arr_hs.append(match)

        # -----        
        outcome = Outcome(
            match_id=1,
            public=1
        )
        db.session.add(outcome)
        db.session.commit()
        arr_hs.append(outcome)

        with self.client:
            Uid = 66
            
            params = {
                "public": 1
            }
            response = self.client.post(
                                    '/match',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

            data_json = data['data']
            self.assertTrue(data['status'] == 0)

            outcomes = []
            for match in data_json:
                if match['id'] == 1:
                    outcomes = match['outcomes']
            

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()

    
if __name__ == '__main__':
    unittest.main()