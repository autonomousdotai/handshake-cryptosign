from tests.routes.base import BaseTestCase
from mock import patch
from app import db
from app.models import Handshake, User, Outcome, Match, Task, Contract
from app.helpers.utils import local_to_utc
from app import app
from datetime import datetime
from flask_jwt_extended import (create_access_token)
from sqlalchemy import or_
import mock
import json
import time
import app.constants as CONST

class TestMatchBluePrint(BaseTestCase):

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

        # create contract
        contract = Contract.find_contract_by_id(1)
        if contract is None:
            contract = Contract(
                id=1,
                contract_name='contract1',
                contract_address='0x123',
                json_name='1.json'
            )
            db.session.add(contract)
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

        matches = db.session.query(Match).filter(or_(Match.created_user_id==88, Match.created_user_id==99, Match.created_user_id==None)).all()
        for m in matches:
            db.session.delete(m)
            db.session.commit()

        outcomes = db.session.query(Outcome).filter(or_(Outcome.created_user_id==88, Outcome.created_user_id==99, Outcome.created_user_id==None)).all()
        for oc in outcomes:
            db.session.delete(oc)
            db.session.commit()

        Task.query.delete()
        db.session.commit()


    def test_get_match_with_no_report_and_time_exceed_closing_time(self):
        self.clear_data_before_test()
        arr_hs = []
        t = datetime.now().timetuple()
        seconds = local_to_utc(t)
        # ----- 

        match = Match.find_match_by_id(1000)
        if match is not None:
            match.date=seconds - 100,
            match.reportTime=seconds + 100,
            match.disputeTime=seconds + 200,
            db.session.flush()
        else:
            match = Match(
                id=1000,
                date=seconds - 100,
                reportTime=seconds + 100,
                disputeTime=seconds + 200,
            )
            db.session.add(match)

        # ----- 

        match = Match.find_match_by_id(1001)
        if match is not None:
            match.date=seconds - 100,
            match.reportTime=seconds + 100,
            match.disputeTime=seconds + 200,
            db.session.flush()
        else:
            match = Match(
                id=1001,
                date=seconds - 100,
                reportTime=seconds + 100,
                disputeTime=seconds + 200,
            )
            db.session.add(match)


        # ----- 

        match = Match.find_match_by_id(1002)
        if match is not None:
            match.date=seconds - 100,
            match.reportTime=seconds + 100,
            match.disputeTime=seconds + 200,
            db.session.flush()
        else:
            match = Match(
                id=1002,
                date=seconds - 100,
                reportTime=seconds + 100,
                disputeTime=seconds + 200,
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
        t = datetime.now().timetuple()
        seconds = local_to_utc(t)
        # ----- 
        match = Match.find_match_by_id(1001)
        if match is not None:
            match.date=seconds + 100,
            match.reportTime=seconds + 200,
            match.disputeTime=seconds + 300,
            db.session.flush()
        else:
            match = Match(
                id=1001,
                date=seconds + 100,
                reportTime=seconds + 200,
                disputeTime=seconds + 300,
            )
            db.session.add(match)
        db.session.commit()
        arr_hs.append(match)
        match_id_1 = match.id

        # ----- 
        match = Match.find_match_by_id(1002)
        if match is not None:
            match.date=seconds + 50,
            match.reportTime=seconds + 200,
            match.disputeTime=seconds + 300,
            db.session.flush()
        else:
            match = Match(
                id=1002,
                date=seconds + 50,
                reportTime=seconds + 200,
                disputeTime=seconds + 300,
            )
            db.session.add(match)

        db.session.commit()
        arr_hs.append(match)
        match_id_2 = match.id

        # -----        
        outcome = Outcome(
            match_id=1001,
            public=1,
            hid=0,
            result=-1
        )
        db.session.add(outcome)
        db.session.commit()
        arr_hs.append(outcome)
    
        # -----        
        outcome = Outcome(
            match_id=1002,
            public=1,
            hid=1,
            result=-1
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
            print data_json
            self.assertTrue(data['status'] == 1)
            self.assertEqual(len(data_json), 2)

            m = data_json[0]
            self.assertNotEqual(m, None)
            self.assertEqual(m['id'], match_id_2)


        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()

    def test_list_match_need_report_by_user(self):
        self.clear_data_before_test()
        t = datetime.now().timetuple()
        seconds = local_to_utc(t)
        # ----- 

        match = Match(
            date=seconds - 100,
            reportTime=seconds + 200,
            disputeTime=seconds + 300,
            created_user_id=99
        )
        db.session.add(match)
        db.session.commit()
        match2 = Match(
            date=seconds - 200,
            reportTime=seconds - 100,
            disputeTime=seconds + 300,
            created_user_id=99
        )
        db.session.add(match2)
        db.session.commit()
        # -----        
        outcome = Outcome(
            created_user_id=88,
            match_id=match.id,
            public=1,
            hid=0,
            name="88",
            result=CONST.RESULT_TYPE['PENDING']
        )
        db.session.add(outcome)
        db.session.commit()
        outcome1 = Outcome(
            created_user_id=99,
            match_id=match.id,
            public=1,
            hid=0,
            name="99",
            result=CONST.RESULT_TYPE['PENDING']
        )
        db.session.add(outcome1)
        db.session.commit()
        outcome2 = Outcome(
            created_user_id=88,
            match_id=match2.id,
            public=1,
            hid=1,
            result=CONST.RESULT_TYPE['PROCESSING']
        )
        db.session.add(outcome2)
        db.session.commit()

        with self.client:
            response = self.client.get(
                                    '/match/report',
                                    headers={
                                        "Uid": "{}".format(88),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })
            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)
            data_json = data['data']
            
            tmp = None
            for m in data_json:
                if m['id'] == match.id:
                    tmp = m
                    self.assertEqual(len(tmp['outcomes']), 1)
                    self.assertEqual(tmp['outcomes'][0]['id'], outcome.id)
                    break

            self.assertNotEqual(tmp, None)


    def test_match_need_user_report(self):
        self.clear_data_before_test()
        t = datetime.now().timetuple()
        seconds = local_to_utc(t)

        # ----- Add matches
        match1 = Match(
            name='match1',
            date=seconds - 100,
            reportTime=seconds + 200,
            disputeTime=seconds + 300,
            created_user_id=88
        )
        db.session.add(match1)
        db.session.commit()

        match2 = Match(
            name='match2',
            date=seconds - 200,
            reportTime=seconds + 100,
            disputeTime=seconds + 300,
            created_user_id=99
        )
        db.session.add(match2)
        db.session.commit()

        match3 = Match(
            name='match3',
            date=seconds - 200,
            reportTime=seconds - 100,
            disputeTime=seconds + 300,
            created_user_id=88
        )
        db.session.add(match3)
        db.session.commit()

        # ----- Add outcomes   
        outcome1 = Outcome(
            name='outcome1',
            created_user_id=99,
            match_id=match1.id,
            public=1,
            hid=0,
            contract_id=1,
            result=CONST.RESULT_TYPE['PENDING']
        )
        db.session.add(outcome1)
        db.session.commit()

        outcome2 = Outcome(
            name='outcome2',
            created_user_id=88,
            match_id=match2.id,
            public=1,
            hid=1,
            result=CONST.RESULT_TYPE['PENDING']
        )
        db.session.add(outcome2)
        db.session.commit()

        outcome3 = Outcome(
            name='outcome3',
            created_user_id=88,
            match_id=match1.id,
            public=1,
            hid=2,
            result=CONST.RESULT_TYPE['PENDING']
        )
        db.session.add(outcome3)
        db.session.commit()

        with self.client:
            # Get match for uid = 88
            # Expected: 
            #   match 1: outcome 1
            #   match 2: outcome 2
            response = self.client.get(
                                    '/match/report',
                                    headers={
                                        "Uid": "{}".format(88),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })
            data = json.loads(response.data.decode())          
            self.assertTrue(data['status'] == 1)
            data_json = data['data']
            self.assertEqual(len(data_json), 2)

            m = data_json[0]
            o = m['outcomes'][0]
            self.assertEqual(o['name'], 'outcome3')

            m1 = data_json[1]
            o1 = m1['outcomes'][0]
            self.assertEqual(o1['name'], 'outcome2')

            # Get match for uid = 99
            # Expected: 
            #   match 1: 1 outcome
            response = self.client.get(
                                    '/match/report',
                                    headers={
                                        "Uid": "{}".format(99),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })
            data = json.loads(response.data.decode())             
            self.assertTrue(data['status'] == 1)
            data_json = data['data']
            self.assertEqual(len(data_json), 1)

            m = data_json[0]
            o = m['outcomes'][0]
            self.assertEqual(o['name'], 'outcome1')


    def test_issue_54(self):
        self.clear_data_before_test()
        t = datetime.now().timetuple()
        seconds = local_to_utc(t)

        # ----- Add matches
        match1 = Match(
            name='match1',
            date=seconds - 100,
            reportTime=seconds + 200,
            disputeTime=seconds + 300,
            created_user_id=88
        )
        db.session.add(match1)
        db.session.commit()

        # ----- Add outcomes   
        outcome1 = Outcome(
            name='outcome1',
            created_user_id=88,
            match_id=match1.id,
            public=1,
            hid=0,
            contract_id=1,
            result=CONST.RESULT_TYPE['PENDING']
        )
        db.session.add(outcome1)
        db.session.commit()

        outcome2 = Outcome(
            name='outcome2',
            created_user_id=88,
            match_id=match1.id,
            public=1,
            hid=1,
            result=CONST.RESULT_TYPE['PENDING']
        )
        db.session.add(outcome2)
        db.session.commit()

        with self.client:
            # Get match for uid = 88
            # Expected: 
            #   match 1: outcome 1, outcome 2
            response = self.client.get(
                                    '/match/report',
                                    headers={
                                        "Uid": "{}".format(88),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })
            data = json.loads(response.data.decode())          
            self.assertTrue(data['status'] == 1)
            data_json = data['data']
            self.assertEqual(len(data_json), 1)
            self.assertEqual(len(data_json[0]['outcomes']), 2)
     
            
    def test_add_match(self):
        self.clear_data_before_test()

        with self.client:
            params = [
                        {
                            "homeTeamName": "Nigeria",
                            "awayTeamName": "Iceland",
                            "date": 1539913910,
                            "reportTime": 1539923910,
                            "disputeTime": 1539933910,
                            "homeTeamCode": "",
                            "homeTeamFlag": "",
                            "awayTeamCode": "",
                            "awayTeamFlag": "",
                            "name": "Nigeria - Iceland - Sangunji",
                            "market_fee": 5,
                            "public": 1,
                            "source": {
                                "name": "Worlcup Russia 2018",
                                "url": "google.com"
                            },
                            "category": {
                                "name": "Worlcup Russia 2018"
                            },
                            "outcomes": [
                                {
                                    "name": "Nigeria wins"
                                },
                                {
                                    "name": "Iceland wins"
                                }
                            ]
                        }
                    ]

            response = self.client.post(
                                    '/match/add',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(88),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })
            data = json.loads(response.data.decode())          
            self.assertTrue(data['status'] == 1)

    def test_add_match_without_market_fee(self):
        self.clear_data_before_test()

        with self.client:
            params = [
                        {
                            "homeTeamName": "Nigeria",
                            "awayTeamName": "Iceland",
                            "date": 1539913910,
                            "reportTime": 1539923910,
                            "disputeTime": 1539933910,
                            "homeTeamCode": "",
                            "homeTeamFlag": "",
                            "awayTeamCode": "",
                            "awayTeamFlag": "",
                            "name": "Nigeria - Iceland - Sangunji",
                            "public": 1,
                            "source": {
                                "name": "Worlcup Russia 2018",
                                "url": "google.com"
                            },
                            "category": {
                                "name": "Worlcup Russia 2018"
                            },
                            "outcomes": [
                                {
                                    "name": "Nigeria wins"
                                },
                                {
                                    "name": "Iceland wins"
                                }
                            ]
                        }
                    ]

            response = self.client.post(
                                    '/match/add',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(88),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })
            data = json.loads(response.data.decode())          
            self.assertTrue(data['status'] == 1)
            for match in data['data']:
                if 'market_fee' not in match or match['market_fee'] is None:
                    self.assertTrue(match['market_fee'] == 0)


if __name__ == '__main__':
    unittest.main()