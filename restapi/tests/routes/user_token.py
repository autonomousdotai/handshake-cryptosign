# -*- coding: utf-8 -*-
from tests.routes.base import BaseTestCase
from mock import patch
from app.models import User, Token, UserToken, Referral
from app import db, app
from sqlalchemy import bindparam, literal_column, func
from app.helpers.message import MESSAGE
from app.constants import Handshake as HandshakeStatus

import mock
import json
import time
import app.bl.user as user_bl
import app.constants as CONST

class TestUserTokenBluePrint(BaseTestCase):

    def clear_data_before_test(self):
        token1 = Token.find_token_by_id(1)
        token1.tid = None
        token1.status = -1

        token2 = Token.find_token_by_id(2)
        token2.tid = None
        token2.status = -1

        # reset users
        users = db.session.query(User).filter(User.email=='trongdth@gmail.com').all()
        for u in users:
            u.email = None

        # reset referral code
        referral = db.session.query(Referral).filter(Referral.user_id==66).first()
        if referral is not None:
            db.session.delete(referral)

        user = User.find_user_with_id(66)
        user.tokens = []

        db.session.flush()
        db.session.commit()
        

    def test_get_user_token(self):
        # self.clear_data_before_test()
        Uid = 66
        arr = []

        ut = UserToken(
            user_id=Uid,
            hash="0x123",
            address="0x123456",
            token_id=1,
            status=CONST.USER_TOKEN_STATUS['PENDING']
        )
        db.session.add(ut)
        db.session.commit()
        arr.append(ut)

        ut2 = UserToken(
            user_id=Uid,
            hash="0x1234",
            address="0x1234567",
            token_id=1,
            status=CONST.USER_TOKEN_STATUS['PENDING']
        )
        db.session.add(ut2)
        db.session.commit()
        arr.append(ut2)

        with self.client:
            response = self.client.get(
                                    '/user-token',
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 1)
            for item in arr:
                db.session.delete(item)
                db.session.commit()

    def test_add_user_token(self):
        self.clear_data_before_test()

        with self.client:
            Uid = 66
            params = {
                "address": "0x123",
                "hash": "0x987",
                "token_id": 1
            }
            # call appprove token again
            response = self.client.post(
                                    '/user-token/add',
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
            self.assertTrue(data_json["address"] == "0x123")
            self.assertTrue(data_json["hash"] == "0x987")

            item = UserToken.find_user_token_with_id(data_json["id"])
            db.session.delete(item)
            db.session.commit()


            Uid = 66
            params = {
                "address": "0x123",
                "hash": "0x987",
                "token_id": 999999
            }
            # call appprove token again
            response = self.client.post(
                                    '/user-token/add',
                                    data=json.dumps(params), 
                                    content_type='application/json',
                                    headers={
                                        "Uid": "{}".format(Uid),
                                        "Fcm-Token": "{}".format(123),
                                        "Payload": "{}".format(123),
                                    })

            data = json.loads(response.data.decode()) 
            self.assertTrue(data['status'] == 0)

if __name__ == '__main__':
    unittest.main()