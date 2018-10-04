# -*- coding: utf-8 -*-
from tests.routes.base import BaseTestCase
from mock import patch
from app.models import User, Handshake, Shaker, Outcome, Token
from app import db, app
from sqlalchemy import bindparam, literal_column, func
from app.helpers.message import MESSAGE
from app.constants import Handshake as HandshakeStatus

import mock
import json
import time
import app.bl.user as user_bl

class TestUserBluePrint(BaseTestCase):
            
    def setUp(self):
        # create token
        token = Token.find_token_by_id(1)
        if token is None:
            token = Token(
                id=1,
                name="SHURIKEN",
                symbol="SHURI",
                decimal=18,
                contract_address='0x123'
            )
            db.session.add(token)
            db.session.commit()

        else:
            token.tid = None
            token.status = -1
            db.session.flush()
            db.session.commit()

        token = Token.find_token_by_id(2)
        if token is None:
            token = Token(
                id=2,
                name="SHURIKEN",
                symbol="SHURI",
                decimal=18,
                contract_address='0x1234'
            )
            db.session.add(token)
            db.session.commit()
        
        else:
            token.tid = None
            token.status = -1
            db.session.flush()
            db.session.commit()


    def tearDown(self):
        pass


    def clear_data_before_test(self):
        token1 = Token.find_token_by_id(1)
        token1.tid = None
        token1.status = -1

        token2 = Token.find_token_by_id(2)
        token2.tid = None
        token2.status = -1

        user = User.find_user_with_id(66)
        user.tokens = []

        db.session.flush()
        db.session.commit()
        

    def test_user_approve_token(self):
        self.clear_data_before_test()

        with self.client:
            Uid = 66
            params = {
                "token_id": 1
            }
            response = self.client.post(
                                    '/approve_token',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 0)

            # approve token first
            token = Token.find_token_by_id(1)
            token.tid = 0
            token.status = 1

            # call appprove token again
            response = self.client.post(
                                    '/approve_token',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)
    

if __name__ == '__main__':
    unittest.main()