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

        outcomes = db.session.query(Outcome).filter(or_(Outcome.created_user_id==88, Outcome.created_user_id==99, Outcome.created_user_id==None)).all()
        for oc in outcomes:
            db.session.delete(oc)
            db.session.commit()

        Task.query.delete()
        db.session.commit()


    def test_get_list_match_report_by_admin(self):
        self.clear_data_before_test()
        arr_hs = []

        t = datetime.now().timetuple()
        seconds = local_to_utc(t)

        # ----- 
        match = Match(
            name='DEBUG 123',
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
            result=CONST.RESULT_TYPE['PENDING'],
            contract_id=1
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


    def test_get_list_match_resolve_by_admin(self):
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
            result=CONST.RESULT_TYPE['DISPUTED'],
            contract_id=1
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