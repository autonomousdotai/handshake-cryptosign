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


    def test_get_match_with_no_report_and_time_exceed_closing_time(self):
        self.clear_data_before_test()
        arr_hs = []

        # ----- 

        match = Match.find_match_by_id(1000)
        if match is not None:
            match.date=time.time() - 100,
            match.reportTime=time.time() + 100,
            match.disputeTime=time.time() + 200,
            db.session.flush()
        else:
            match = Match(
                id=1000,
                date=time.time() - 100,
                reportTime=time.time() + 100,
                disputeTime=time.time() + 200,
            )
            db.session.add(match)

        # ----- 

        match = Match.find_match_by_id(1001)
        if match is not None:
            match.date=time.time() - 100,
            match.reportTime=time.time() + 100,
            match.disputeTime=time.time() + 200,
            db.session.flush()
        else:
            match = Match(
                id=1001,
                date=time.time() - 100,
                reportTime=time.time() + 100,
                disputeTime=time.time() + 200,
            )
            db.session.add(match)


        # ----- 

        match = Match.find_match_by_id(1002)
        if match is not None:
            match.date=time.time() - 100,
            match.reportTime=time.time() + 100,
            match.disputeTime=time.time() + 200,
            db.session.flush()
        else:
            match = Match(
                id=1002,
                date=time.time() - 100,
                reportTime=time.time() + 100,
                disputeTime=time.time() + 200,
            )
            db.session.add(match)

        db.session.commit()
        arr_hs.append(match)

        # -----        
        outcome = Outcome(
            match_id=1000,
            public=1,
            hid=0
        )
        db.session.add(outcome)
        db.session.commit()
        arr_hs.append(outcome)

        with self.client:
            Uid = 66
            
            response = self.client.get(
                                    '/match',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

            data_json = data['data']
            self.assertTrue(data['status'] == 1)
            self.assertEqual(len(data_json), 0)            

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()


    def test_get_match_with_no_report_and_time_not_exceed_closing_time(self):
        self.clear_data_before_test()
        arr_hs = []

        # ----- 
        match = Match.find_match_by_id(1001)
        if match is not None:
            match.date=time.time() + 100,
            match.reportTime=time.time() + 200,
            match.disputeTime=time.time() + 300,
            db.session.flush()
        else:
            match = Match(
                id=1001,
                date=time.time() + 100,
                reportTime=time.time() + 200,
                disputeTime=time.time() + 300,
            )
            db.session.add(match)
        db.session.commit()
        arr_hs.append(match)
        match_id_1 = match.id

        # ----- 
        match = Match.find_match_by_id(1002)
        if match is not None:
            match.date=time.time() + 50,
            match.reportTime=time.time() + 200,
            match.disputeTime=time.time() + 300,
            db.session.flush()
        else:
            match = Match(
                id=1002,
                date=time.time() + 50,
                reportTime=time.time() + 200,
                disputeTime=time.time() + 300,
            )
            db.session.add(match)

        db.session.commit()
        arr_hs.append(match)
        match_id_2 = match.id

        # -----        
        outcome = Outcome(
            match_id=1001,
            public=1,
            hid=0
        )
        db.session.add(outcome)
        db.session.commit()
        arr_hs.append(outcome)
    
        # -----        
        outcome = Outcome(
            match_id=1002,
            public=1,
            hid=1
        )
        db.session.add(outcome)
        db.session.commit()
        arr_hs.append(outcome)

        with self.client:
            Uid = 66
            
            response = self.client.get(
                                    '/match',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

            data_json = data['data']
            self.assertTrue(data['status'] == 1)
            self.assertEqual(len(data_json), 2)

            m = data_json[0]
            self.assertNotEqual(m, None)
            self.assertEqual(m['id'], match_id_2)


        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()


    def test_get_match_with_report_and_time_exceed_closing_time(self):
        self.clear_data_before_test()
        arr_hs = []

        # ----- 

        match = Match.find_match_by_id(1000)
        if match is not None:
            match.date=time.time() - 100,
            match.reportTime=time.time() + 100,
            match.disputeTime=time.time() + 200,
            db.session.flush()
        else:
            match = Match(
                id=1000,
                date=time.time() - 100,
                reportTime=time.time() + 100,
                disputeTime=time.time() + 200,
            )
            db.session.add(match)

        db.session.commit()
        arr_hs.append(match)

        # -----        
        outcome = Outcome(
            match_id=1000,
            public=1,
            hid=0
        )
        db.session.add(outcome)
        db.session.commit()
        arr_hs.append(outcome)

        with self.client:
            Uid = 66
            
            response = self.client.get(
                                    '/match?report=1',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)

            data_json = data['data']
            self.assertTrue(data['status'] == 1)
            self.assertNotEqual(len(data_json), 0)            

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()


    def test_get_match_with_report_and_time_not_exceed_closing_time(self):
        self.clear_data_before_test()
        arr_hs = []

        # ----- 

        match = Match.find_match_by_id(1000)
        if match is not None:
            match.date=time.time() + 100,
            match.reportTime=time.time() + 100,
            match.disputeTime=time.time() + 200,
            db.session.flush()
        else:
            match = Match(
                id=1000,
                date=time.time() + 100,
                reportTime=time.time() + 100,
                disputeTime=time.time() + 200,
            )
            db.session.add(match)

        db.session.commit()
        arr_hs.append(match)

        # -----        
        outcome = Outcome(
            match_id=1000,
            public=1,
            hid=0
        )
        db.session.add(outcome)
        db.session.commit()
        arr_hs.append(outcome)

        with self.client:
            Uid = 66
            
            response = self.client.get(
                                    '/match?report=1',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)
            data_json = data['data']
            self.assertTrue(data['status'] == 1)

            tmp = None
            for m in data_json:
                if m['id'] == 1000:
                    tmp = m
                    break

            self.assertEqual(tmp, None)

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()

    def test_get_list_match_report_with_user(self):
        self.clear_data_before_test()
        arr_hs = []
        uid = 66
        # ----- 

        match = Match.find_match_by_id(1000)
        if match is not None:
            match.date=time.time() - 100,
            match.reportTime=time.time() + 200,
            match.disputeTime=time.time() + 300,
            created_user_id=uid,
            db.session.flush()
        else:
            match = Match(
                id=1000,
                date=time.time() - 100,
                reportTime=time.time() + 200,
                disputeTime=time.time() + 300,
                created_user_id=uid
            )
            db.session.add(match)
        match = Match.find_match_by_id(1000)

        db.session.commit()
        arr_hs.append(match)

        # -----        
        outcome = Outcome(
            match_id=1000,
            public=1,
            hid=0,
            result=-1
        )
        db.session.add(outcome)
        db.session.commit()
        arr_hs.append(outcome)

        with self.client:
            Uid = uid
            
            response = self.client.get(
                                    '/match/list/report',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)
            data_json = data['data']
            self.assertTrue(data['status'] == 1)

            tmp = None
            for m in data_json:
                if m['id'] == 1000:
                    tmp = m
                    break

            self.assertNotEqual(tmp, None)

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()


    def test_get_list_match_report_with_admin(self):
        self.clear_data_before_test()
        arr_hs = []
        uid = 66
        # ----- 

        match = Match.find_match_by_id(1000)
        if match is not None:
            match.date=time.time() - 100,
            match.reportTime=time.time() + 200,
            match.disputeTime=time.time() + 300,
            created_user_id=uid,
            db.session.flush()
        else:
            match = Match(
                id=1000,
                date=time.time() - 100,
                reportTime=time.time() + 200,
                disputeTime=time.time() + 300,
                created_user_id=uid
            )
            db.session.add(match)
        match = Match.find_match_by_id(1000)

        db.session.commit()
        arr_hs.append(match)

        # -----        
        outcome = Outcome(
            match_id=1000,
            public=1,
            hid=0,
            result=-1
        )
        db.session.add(outcome)
        db.session.commit()
        arr_hs.append(outcome)

        with self.client:
            Uid = uid
            
            response = self.client.get(
                                    '/match/list/report',
                                    headers={
                                        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIwYzBlOTBjMS0xZjc3LTRmMzgtYjFhZi1kY2UzNzE3MDkyN2MiLCJleHAiOjE1MzY0Mjg4ODUsImZyZXNoIjp0cnVlLCJpYXQiOjE1MzEyNDQ4ODUsInR5cGUiOiJhY2Nlc3MiLCJuYmYiOjE1MzEyNDQ4ODUsImlkZW50aXR5IjoiYWRtaW5AbmluamEub3JnIn0.M48Ngokr0wDEhVEPG1Qjn8j6qNC5B1H1cSX6rBXv8xo",
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)
            data_json = data['data']
            self.assertTrue(data['status'] == 1)

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()
    
if __name__ == '__main__':
    unittest.main()