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

class TestAdminBluePrint(BaseTestCase):

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

        matches = db.session.query(Match).filter(or_(Match.created_user_id==88, Match.created_user_id==99)).all()
        for m in matches:
            db.session.delete(m)
            db.session.commit()

        outcomes = db.session.query(Outcome).filter(or_(Outcome.created_user_id==88, Outcome.created_user_id==99, Outcome.created_user_id==None)).all()
        for oc in outcomes:
            db.session.delete(oc)
            db.session.commit()

        Task.query.delete()
        db.session.commit()


    def test_get_list_match_report_with_admin(self):
        self.clear_data_before_test()
        arr_hs = []
        t = datetime.now().timetuple()
        seconds = local_to_utc(t)
        # ----- 
        match = Match(
            date=seconds - 200,
            reportTime=seconds + 100,
            disputeTime=seconds + 300
        )
        db.session.add(match)
        db.session.commit()

        # -----        
        outcome = Outcome(
            match_id=match.id,
            hid=0,
            result=CONST.RESULT_TYPE['PENDING']
        )
        db.session.add(outcome)
        db.session.commit()

        with self.client:
            response = self.client.get(
                                    'admin/match/report',
                                    headers={
                                        "Authorization": "Bearer {}".format(create_access_token(identity=app.config.get("EMAIL"), fresh=True)),
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
                    break
            self.assertNotEqual(tmp, None)


    def test_get_list_match_resolve_with_admin(self):
        self.clear_data_before_test()
        arr_hs = []
        t = datetime.now().timetuple()
        seconds = local_to_utc(t)
        # ----- 

        match2 = Match(
            date=seconds - 200,
            reportTime=seconds - 100,
            disputeTime=seconds + 300,
            created_user_id=88,
            name="Dispute"
        )
        db.session.add(match2)
        db.session.commit()

        # -----        

        outcome1 = Outcome(
            match_id=match2.id,
            hid=1,
            result=CONST.RESULT_TYPE['DISPUTED']
        )
        db.session.add(outcome1)
        db.session.commit()        

        with self.client:
            response = self.client.get(
                                    'admin/match/resolve',
                                    headers={
                                        "Authorization": "Bearer {}".format(create_access_token(identity=app.config.get("EMAIL"), fresh=True)),
                                        "Uid": "{}".format(88),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)
            data_json = data['data']
            tmp = None
            for m in data_json:
                if m['id'] == match2.id:
                    tmp = m
                    break
            self.assertNotEqual(tmp, None)


    def test_create_market(self):
        self.clear_data_before_test()
        with self.client:
            response = self.client.post(
                                    'admin/create_market',
                                    headers={
                                        "Authorization": "Bearer {}".format(create_access_token(identity=app.config.get("EMAIL"), fresh=True)),
                                        "Uid": "{}".format(1000),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)


    def test_all_matches_need_report_by_admin(self):
        self.clear_data_before_test()

    
    def test_report_match(self):
        self.clear_data_before_test()

        t = datetime.now().timetuple()
        seconds = local_to_utc(t)

        match = Match.find_match_by_id(1)
        
        if match is not None:
            match.date = seconds - 1000
            match.reportTime = seconds + 1000
            match.disputeTime = seconds + 2000

        with self.client:
            response = self.client.post(
                                    'admin/match/report/1',
                                    headers={
                                        "Authorization": "Bearer {}".format(create_access_token(identity=app.config.get("EMAIL"), fresh=True)),
                                        "Uid": "{}".format(1000),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 0)


if __name__ == '__main__':
    unittest.main()