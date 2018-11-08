from tests.routes.base import BaseTestCase
from mock import patch
from app import db
from app.models import Handshake, User, Outcome, Match, Task, Contract, Source, Category, Token, Source
from app.helpers.utils import local_to_utc
from app import app
from datetime import datetime
from flask_jwt_extended import (create_access_token)
from sqlalchemy import or_
from requests_toolbelt.multipart.encoder import MultipartEncoder

import mock
import json
import time
import hashlib
import app.constants as CONST

class TestMatchBluePrint(BaseTestCase):

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
                contract_name='PredictionHandshake',
                contract_address=app.config['PREDICTION_SMART_CONTRACT'],
                json_name=app.config['PREDICTION_JSON']
            )
            db.session.add(contract)
            db.session.commit()
        else:
            contract.contract_address = app.config['PREDICTION_SMART_CONTRACT']
            contract.json_name = app.config['PREDICTION_JSON']
            db.session.commit()


        contract = Contract.find_contract_by_id(2)
        if contract is None:
            contract = Contract(
                id=2,
                contract_name='PredictionHandshakeWithToken',
                contract_address=app.config['ERC20_PREDICTION_SMART_CONTRACT'],
                json_name=app.config['ERC20_PREDICTION_JSON']
            )
            db.session.add(contract)
            db.session.commit()
        else:
            contract.contract_address = app.config['ERC20_PREDICTION_SMART_CONTRACT']
            contract.json_name = app.config['ERC20_PREDICTION_JSON']
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

        sources = Source.find_source_by_url('voa.com')
        for s in sources:
            db.session.delete(s)
            db.session.commit()

        Task.query.delete()
        db.session.commit()


    def test_get_match_with_no_report_and_time_exceed_closing_time(self):
        self.clear_data_before_test()
        arr_hs = []
        t = datetime.now().timetuple()
        seconds = local_to_utc(t)

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
            old_matches = len(data_json)

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
                hid=0
            )
            db.session.add(outcome)
            db.session.commit()
            arr_hs.append(outcome)    

            #  call match endpoint again
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
            new_matches = len(data_json)
            self.assertEqual(old_matches, new_matches) 

        for handshake in arr_hs:
            db.session.delete(handshake)
            db.session.commit()


    def test_get_match_with_no_report_and_time_not_exceed_closing_time(self):
        self.clear_data_before_test()
        arr_hs = []
        t = datetime.now().timetuple()
        seconds = local_to_utc(t)

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
            old_matches = len(data_json)

            source1 = Source.find_source_by_id(1)
            if source1 is None:
                source1 = Source(
                    id = 1,
                    name = "Source",
                    url = "htpp://www.abc.com",
                    approved = 1
                )
                db.session.add(source1)
                db.session.commit()
            # ----- 
            match = Match.find_match_by_id(1001)
            if match is not None:
                match.date=seconds + 100,
                match.reportTime=seconds + 200,
                match.disputeTime=seconds + 300,
                match.public=1,
                source_id=1
                db.session.flush()
            else:
                match = Match(
                    id=1001,
                    date=seconds + 100,
                    reportTime=seconds + 200,
                    disputeTime=seconds + 300,
                    source_id=1,
                    public=1
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
                match.public=1,
                source_id=1
                db.session.flush()
            else:
                match = Match(
                    id=1002,
                    date=seconds + 50,
                    reportTime=seconds + 200,
                    disputeTime=seconds + 300,
                    source_id=1,
                    public=1,
                )
                db.session.add(match)

            db.session.commit()
            arr_hs.append(match)
            match_id_2 = match.id

            # -----        
            outcome = Outcome(
                match_id=1001,
                hid=0,
                result=-1
            )
            db.session.add(outcome)
            db.session.commit()
            arr_hs.append(outcome)
        
            # -----        
            outcome = Outcome(
                match_id=1002,
                hid=1,
                result=-1
            )
            db.session.add(outcome)
            db.session.commit()
            arr_hs.append(outcome)

            # call match endpoint again
            response = self.client.get(
                                    '/match',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            print data
            self.assertTrue(data['status'] == 1)
            data_json = data['data']
            self.assertTrue(data['status'] == 1)
            new_matches = len(data_json)
            self.assertEqual(old_matches+2, new_matches)

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
            hid=0,
            name="88",
            result=CONST.RESULT_TYPE['PENDING']
        )
        db.session.add(outcome)
        db.session.commit()
        outcome1 = Outcome(
            created_user_id=99,
            match_id=match.id,
            hid=0,
            name="99",
            result=CONST.RESULT_TYPE['PENDING']
        )
        db.session.add(outcome1)
        db.session.commit()
        outcome2 = Outcome(
            created_user_id=88,
            match_id=match2.id,
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
            hid=1,
            result=CONST.RESULT_TYPE['PENDING']
        )
        db.session.add(outcome2)
        db.session.commit()

        outcome3 = Outcome(
            name='outcome3',
            created_user_id=88,
            match_id=match1.id,
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
            self.assertEqual(o['name'], 'outcome2')

            m1 = data_json[1]
            o1 = m1['outcomes'][0]
            self.assertEqual(o1['name'], 'outcome3')

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
        t = datetime.now().timetuple()
        seconds = local_to_utc(t)

        with self.client:
            params = {
                            "homeTeamName": "Nigeria",
                            "awayTeamName": "Iceland",
                            "date": seconds + 100,
                            "reportTime": seconds + 200,
                            "disputeTime": seconds + 300,
                            "homeTeamCode": "",
                            "homeTeamFlag": "",
                            "awayTeamCode": "",
                            "awayTeamFlag": "",
                            "name": "Nigeria - Iceland - Sangunji",
                            "market_fee": 5,
                            "public": 1,
                            "source": {
                                "name": "Worlcup Russia 2018_{}".format(seconds),
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

            multipart_form_data = MultipartEncoder(
                fields= {
                    'data': json.dumps(params),
                }
            )
            response = self.client.post(
                                    '/match/add',
                                    data=multipart_form_data,
                                    headers={
                                        "Uid": "{}".format(88),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                        "Content-Type": multipart_form_data.content_type #application/json
                                    })

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertTrue(len(data['data']) == 1)
            match_added = data['data'][0]
            self.assertTrue(len(match_added['outcomes']) == 1)
            self.assertTrue(match_added['outcomes'][0]['name'] == 'Yes')
            

    def test_add_match_without_market_fee(self):
        self.clear_data_before_test()
        t = datetime.now().timetuple()
        seconds = local_to_utc(t)
        with self.client:
            params = {
                        "homeTeamName": "Nigeria",
                        "awayTeamName": "Iceland",
                        "date": seconds + 100,
                        "reportTime": seconds + 200,
                        "disputeTime": seconds + 300,
                        "homeTeamCode": "",
                        "homeTeamFlag": "",
                        "awayTeamCode": "",
                        "awayTeamFlag": "",
                        "name": "Nigeria - Iceland - Sangunji",
                        "public": 1,
                        "source": {
                            "name": "{}".format(seconds),
                            "url": "{}".format(seconds),
                        },
                        "category": {
                            "name": "Worlcup Russia 2018"
                        }
                    }

            multipart_form_data = MultipartEncoder(
                fields= {
                    'data': json.dumps(params),
                }
            )
            print json.dumps(params)
            response = self.client.post(
                                    '/match/add',
                                    data=multipart_form_data,
                                    headers={
                                        "Uid": "{}".format(88),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                        "Content-Type": multipart_form_data.content_type
                                    })
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            for match in data['data']:
                if 'market_fee' not in match or match['market_fee'] is None:
                    self.assertTrue(match['market_fee'] == 0)

    def test_add_match_with_source_existed(self):
        self.clear_data_before_test()
        t = datetime.now().timetuple()
        seconds = local_to_utc(t)
        with self.client:
            params = {
                            "homeTeamName": "Nigeria",
                            "awayTeamName": "Iceland",
                            "date": seconds + 100,
                            "reportTime": seconds + 200,
                            "disputeTime": seconds + 300,
                            "homeTeamCode": "",
                            "homeTeamFlag": "",
                            "awayTeamCode": "",
                            "awayTeamFlag": "",
                            "name": "Nigeria - Iceland - Sangunji",
                            "public": 1,
                            "source": {
                                "name": "Worlcup Russia 2018",
                                "url": "google.com",
                            },
                            "category": {
                                "name": "Worlcup Russia 2018"
                            }
                        }

            multipart_form_data = MultipartEncoder(
                fields= {
                    'data': json.dumps(params),
                }
            )
            response = self.client.post(
                                    '/match/add',
                                    data=multipart_form_data,
                                    headers={
                                        "Uid": "{}".format(88),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                        "Content-Type": multipart_form_data.content_type #application/json
                                    })
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)

    def test_add_match_with_category_existed(self):
        self.clear_data_before_test()
        t = datetime.now().timetuple()
        seconds = local_to_utc(t)
        cate = Category.find_category_by_id(1)
        if cate is None:
            cate = Category(
                id = 1,
                name = "Cate Existed",
                approved = 1
            )
        else:
            cate.name = "Cate Existed"

        db.session.flush()
        db.session.commit()
        with self.client:
            params = {
                            "homeTeamName": "Nigeria",
                            "awayTeamName": "Iceland",
                            "date": seconds + 100,
                            "reportTime": seconds + 200,
                            "disputeTime": seconds + 300,
                            "homeTeamCode": "",
                            "homeTeamFlag": "",
                            "awayTeamCode": "",
                            "awayTeamFlag": "",
                            "name": "Nigeria - Iceland - Sangunji",
                            "public": 1,
                            "source": {
                                "name": "Worlcup Russia 2018",
                                "url": "google.com",
                            },
                            "category": {
                                "name": "Cate Existed"
                            }
                        }



            multipart_form_data = MultipartEncoder(
                fields= {
                    'data': json.dumps(params),
                }
            )
            response = self.client.post(
                                    '/match/add',
                                    data=multipart_form_data,
                                    headers={
                                        "Uid": "{}".format(88),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                        "Content-Type": multipart_form_data.content_type #application/json
                                    })

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertTrue(len(data['data']) > 0)
            self.assertTrue(data['data'][0]['category']['id'] == cate.id)
            self.assertTrue(data['data'][0]['category']['name'] == cate.name)


    def test_get_matchs_relevant_event(self):
        self.clear_data_before_test()
        t = datetime.now().timetuple()
        seconds = local_to_utc(t)
        arr_match = []

        # ----- 
        source_relevant = Source.find_source_by_id(1)
        if source_relevant is None:
            source_relevant = Source(
                id = 1,
                name = "Source Relevant",
                url = "htpp://www.google.com",
                approved = 1
            )
            db.session.flush()
        
        source = Source.find_source_by_id(2)
        if source is None:
            source = Source(
                id = 2,
                name = "Source",
                url = "htpp://www.abc.com",
                approved = 1
            )
            db.session.flush()
        # ----- 
        cate_relevant = Category.find_category_by_id(1)
        if cate_relevant is None:
            cate_relevant = Category(
                id = 1,
                name = "Cate Relevant",
                approved = 1
            )
            db.session.flush()
        cate = Category.find_category_by_id(2)
        if cate is None:
            cate = Category(
                id = 2,
                name = "Cate",
                approved = 1
            )
            db.session.flush()
        # ----- 
        db.session.commit()

        match = Match.find_match_by_id(999)
        if match is not None:
            match.date=seconds + 100
            match.reportTime=seconds + 200
            match.disputeTime=seconds + 300
            match.source_id = source_relevant.id
            match.category_id = cate.id
            db.session.flush()
            arr_match.append(match)
        else:
            match = Match(
                id=999,
                date=seconds + 100,
                reportTime=seconds + 200,
                disputeTime=seconds + 300,
                source_id = source_relevant.id,
                category_id = cate.id
            )
            arr_match.append(match)
            db.session.add(match)

        match_source = Match.find_match_by_id(1000)
        if match_source is not None:
            match_source.date=seconds + 100
            match_source.reportTime=seconds + 200
            match_source.disputeTime=seconds + 300
            match_source.source_id = source_relevant.id
            match_source.name = "Match same source "
            db.session.flush()
            arr_match.append(match_source)
        else:
            match_source = Match(
                id=1000,
                date=seconds + 100,
                reportTime=seconds + 200,
                disputeTime=seconds + 300,
                source_id = source_relevant.id,
                name = "Match same source "
            )
            arr_match.append(match_source)
            db.session.add(match_source)

        # ----- 
        match_cate = Match.find_match_by_id(1001)
        if match_cate is not None:
            match_cate.date=seconds + 100
            match_cate.reportTime=seconds + 100
            match_cate.disputeTime=seconds + 200
            match_cate.category_id = cate.id
            match_cate.name = "Match same cate "
            db.session.flush()
            arr_match.append(match_cate)
        else:
            match_cate = Match(
                id=1001,
                date=seconds + 100,
                reportTime=seconds + 100,
                disputeTime=seconds + 200,
                category_id = cate.id,
                name = "Match same cate "
            )
            arr_match.append(match_cate)
            db.session.add(match_cate)

        # ----- 
        match_invalid = Match.find_match_by_id(1002)
        if match_invalid is not None:
            match_invalid.date=seconds + 100
            match_invalid.reportTime=seconds + 100
            match_invalid.disputeTime=seconds + 200
            match_invalid.name = "Match invalid "
            arr_match.append(match_invalid)
            db.session.flush()
        else:
            match_invalid = Match(
                id=1002,
                date=seconds + 100,
                reportTime=seconds + 100,
                disputeTime=seconds + 200,
                name = "Match invalid "
            )
            db.session.add(match_invalid)
            arr_match.append(match_invalid)
        # ----- 
        db.session.commit()

        # -----        
        outcome1 = Outcome(
            match_id=match_source.id,
            hid=1,
            result=-1
        )
        db.session.add(outcome1)

        outcome2 = Outcome(
            match_id=match_cate.id,
            hid=1,
            result=-1
            
        )
        db.session.add(outcome2)
        db.session.commit()

        with self.client:
            Uid = 66
            response = self.client.get(
                                    '/match/relevant-event?match={}'.format(match.id),
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)

            for match in arr_match:
                self.assertFalse(match.id == match_invalid)

            for match in arr_match:
                db.session.delete(match)
                db.session.commit()


    def test_get_match_detail_relevant_event(self):
        self.clear_data_before_test()
        t = datetime.now().timetuple()
        seconds = local_to_utc(t)
        arr_match = []

        sources = Source.find_source_by_url('voa.com')
        source = None
        if sources is None or len(sources) == 0:
            source = Source(
                name="voa",
                url="https://www.voa.com"
            )
            db.session.add(source)
            db.session.commit()
        else:
            source = sources[0]

        # ----- 
        match = Match.find_match_by_id(999)
        if match is not None:
            match.date=seconds + 100
            match.reportTime=seconds + 200
            match.disputeTime=seconds + 300
            match.public=1
            match.source_id=source.id
            db.session.flush()
            arr_match.append(match)

            for oc in match.outcomes:
                db.session.delete(oc)
                db.session.commit()
        else:
            match = Match(
                id=999,
                public=1,
                date=seconds + 100,
                reportTime=seconds + 200,
                disputeTime=seconds + 300,
                source_id=source.id
            )
            arr_match.append(match)
            db.session.add(match)

        # -----        
        outcome = Outcome(
            match_id=match.id,
            hid=1,
            result=-1
        )
        db.session.add(outcome)
        db.session.commit()
        arr_match.append(outcome)

        # Data before test source_name is none
        source1 = Source.find_source_by_id(1)
        if source1 is None:
            source1 = Source(
                id = 1,
                url = "htpp://www.abc.com",
                approved = 1
            )
            db.session.add(source1)
        else:
            source1.url = "htpp://www.abc.com"
            source1.name= None
            db.session.flush()
        db.session.commit()
        arr_match.append(source1)

        match1 = Match.find_match_by_id(1000)
        if match1 is not None:
            match1.date=seconds + 100
            match1.reportTime=seconds + 200
            match1.disputeTime=seconds + 300
            match1.public=1
            match1.source_id=source1.id
            db.session.flush()
            arr_match.append(match1)

            for oc in match1.outcomes:
                db.session.delete(oc)
                db.session.commit()
        else:
            match1 = Match(
                id=1000,
                public=1,
                date=seconds + 100,
                reportTime=seconds + 200,
                disputeTime=seconds + 300,
                source_id=source1.id
            )
            arr_match.append(match1)
            db.session.add(match1)
        db.session.commit()
        # -----        
        outcome1 = Outcome(
            match_id=match1.id,
            hid=1,
            result=-1
        )
        db.session.add(outcome1)
        db.session.commit()
        arr_match.append(outcome1)

        with self.client:
            Uid = 66
            # Case: get event
            response = self.client.get(
                                    '/match/{}'.format(match.id),
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertTrue(len(data['data']['outcomes']) != 0)
            # self.assertNotIn("source_id", data['data'])
            self.assertTrue(data['data']['source'] != None)
            self.assertTrue(data['data']['source']['id'] == source.id)
            self.assertTrue(data['data']['source']['name'] == source.name)
            self.assertTrue(data['data']['source']['url_icon'] == CONST.SOURCE_URL_ICON.format('www.voa.com'))

            response = self.client.get(
                                    '/match/{}'.format(match1.id),
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            self.assertTrue(len(data['data']['outcomes']) != 0)
            self.assertTrue(data['data']['source'] != None)
            self.assertTrue(data['data']['source']['id'] == source1.id)
            self.assertTrue(data['data']['source']['name'] == "www.abc.com")
            self.assertTrue(data['data']['source']['url_icon'] == CONST.SOURCE_URL_ICON.format('www.abc.com'))

            for match in arr_match:
                db.session.delete(match)
                db.session.commit()


    def test_count_event_based_on_source(self):
        self.clear_data_before_test()
        t = datetime.now().timetuple()
        seconds = local_to_utc(t)
        arr_match = []

        # ------
        source = Source(
            name = "Source",
            url = "voa.com",
            approved = 1
        )
        db.session.add(source)
        db.session.commit()
        
        # ------
        match = Match.find_match_by_id(4685)
        if match is not None:
            match.date = seconds + 100
            match.reportTime = seconds + 200
            match.disputeTime = seconds + 300
            match.source_id = source.id,
            match.category_id = cate.id
        else:
            match = Match(
                id=4685,
                public=1,
                date=seconds + 100,
                reportTime=seconds + 200,
                disputeTime=seconds + 300,
                source_id = source.id
            )
            db.session.add(match)

        # -----        
        outcome = Outcome(
            match_id=match.id,
            hid=1,
            result=-1
        )
        db.session.add(outcome)
        arr_match.append(match)
        db.session.commit()

        with self.client:
            Uid = 88

            source = 'https://voa.com'
            code = hashlib.md5('{}{}'.format(source, app.config['PASSPHASE'])).hexdigest()
            response = self.client.get(
                                    '/match/count-event?source={}&code={}'.format(source, code),
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(88),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            bets = data['data']
            self.assertEqual(int(bets['bets']), 1)

            for match in arr_match:
                db.session.delete(match)
                db.session.commit()


    def test_add_match_with_token_id(self):
        self.clear_data_before_test()
        t = datetime.now().timetuple()
        seconds = local_to_utc(t)
        with self.client:
            params = {
                            "homeTeamName": "Nigeria",
                            "awayTeamName": "Iceland",
                            "date": seconds + 100,
                            "reportTime": seconds + 200,
                            "disputeTime": seconds + 300,
                            "homeTeamCode": "",
                            "homeTeamFlag": "",
                            "awayTeamCode": "",
                            "awayTeamFlag": "",
                            "name": "Nigeria - Iceland - Sangunji",
                            "public": 1,
                            "source": {
                                "name": "Worlcup Russia 2018_{}".format(seconds),
                                "url": "google.com_{}".format(seconds),
                            },
                            "category": {
                                "name": "Worlcup Russia 2018"
                            }
                        }

            multipart_form_data = MultipartEncoder(
                fields= {
                    'data': json.dumps(params),
                }
            )
            response = self.client.post(
                                    '/match/add?token_id=1',
                                    data=multipart_form_data,
                                    headers={
                                        "Uid": "{}".format(88),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                        "Content-Type": multipart_form_data.content_type #application/json
                                    })
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 1)
            contract = data['data'][0]['contract']
            self.assertEqual(contract['json_name'], app.config['ERC20_PREDICTION_JSON'])
            self.assertEqual(contract['contract_address'], app.config['ERC20_PREDICTION_SMART_CONTRACT'])

            for match in data['data']:
                if 'market_fee' not in match or match['market_fee'] is None:
                    self.assertTrue(match['market_fee'] == 0)

    def test_add_private_event_and_send_mail(self):
        self.clear_data_before_test()
        t = datetime.now().timetuple()
        seconds = local_to_utc(t)

        email = "abc1234567890@xyz0987.com"
        user = db.session.query(User).filter_by(email=email).first()

        if user is None:
            user = User(
                email=email,
                payload="LDwp7UQoRNW5tUwzrA6q2trkwJLS3q6IHdOB0vt4T3dWV-a720yuWC1A9g==",
                is_subscribe=1
            )
            db.session.add(user)
        else: 
            user.is_subscribe=1
        db.session.commit()
        with self.client:
            params = {
                            "homeTeamName": "Nigeria",
                            "awayTeamName": "Iceland",
                            "date": seconds + 100,
                            "reportTime": seconds + 200,
                            "disputeTime": seconds + 300,
                            "homeTeamCode": "",
                            "homeTeamFlag": "",
                            "awayTeamCode": "",
                            "awayTeamFlag": "",
                            "name": "Nigeria - Iceland - Sangunji",
                            "market_fee": 5,
                            "public": 0,
                            "source_id": 1,
                            "category": {
                                "name": "Worlcup Russia 2018"
                            }
                        }

            multipart_form_data = MultipartEncoder(
                fields= {
                    'data': json.dumps(params),
                }
            )
            response = self.client.post(
                                    '/match/add',
                                    data=multipart_form_data,
                                    headers={
                                        "Uid": "{}".format(user.id),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                        "Content-Type": multipart_form_data.content_type #application/json
                                    })
            data = json.loads(response.data.decode())
            print data
            self.assertTrue(data['status'] == 1)


if __name__ == '__main__':
    unittest.main()